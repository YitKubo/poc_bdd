"""feature (Gherkin) から PlantUML タイミングチャートを生成する。

入力は feature だけ。ステップの「文の形」で解釈するので、信号ごとの対応表は不要。

  前提/もし  「〇〇が 値 [単位] である」  -> 入力信号〇〇をその時刻で変える
  「N ms 経過する」                       -> 時間を N ms 進める
  ならば     「〇〇が 値 [単位] である」  -> 出力信号〇〇の期待値（確認時点に印を付ける）
  上記の形に合わないステップ              -> 図の上のメモにする

使い方: python tools/gherkin2puml.py <featureディレクトリ> <出力ディレクトリ>
"""

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from gherkin.parser import Parser
from gherkin.token_scanner import TokenScanner

ELAPSE = re.compile(r'^"(\d+)\s*ms"\s*経過する$')
SIGNAL = re.compile(r"^(?P<name>.+?)が\s*(?P<value>.+?)\s*である$")
NUMBER = re.compile(r"^(-?\d+(?:\.\d+)?)\s*(\S*)$")  # 「1200 rpm」のような数値＋単位
# 図の横幅の目安。PlantUML は最後の時刻の約 2 倍まで軸を伸ばすので、scale には半分を指定する
CHART_WIDTH_PX = 1400
CHECK_COLOR = "#FFD70066"  # 確認時点の帯（半透明で波形を隠さない）


@dataclass
class Chart:
    title: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    # (時刻, 信号, 値, 確認の直後か)
    events: list[tuple[int, str, str, bool]] = field(default_factory=list)
    checks: list[int] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    end_ms: int = 0


def _fill(text: str, row: dict[str, str]) -> str:
    for key, val in row.items():
        text = text.replace(f"<{key}>", val)
    return text


def _step_kinds(steps: list[dict]) -> list[str]:
    """And/But は直前のステップの種類を引き継ぐ。"""
    kinds, last = [], "Context"
    for step in steps:
        kind = step["keywordType"]
        if kind != "Conjunction":
            last = kind
        kinds.append(last)
    return kinds


def build_chart(title: str, steps: list[dict], row: dict[str, str]) -> Chart:
    chart = Chart(title=title)
    now = 0
    checked = False  # 直前に確認があり、まだ時間が進んでいない（この間の入力は確認の「後」の変化）
    for step, kind in zip(steps, _step_kinds(steps), strict=True):
        text = _fill(step["text"], row).strip()
        m = ELAPSE.match(text)
        if m:
            now += int(m.group(1))
            checked = False
            continue
        m = SIGNAL.match(text)
        if not m:
            chart.notes.append(text)
            continue
        name, value = m.group("name"), m.group("value").strip('"')
        if kind == "Outcome":
            if name not in chart.outputs:
                chart.outputs.append(name)
            chart.checks.append(now)
            checked = True
        elif name not in chart.inputs:
            chart.inputs.append(name)
        chart.events.append((now, name, value, checked and kind != "Outcome"))
    chart.end_ms = now
    return chart


def _kind_of(values: list[str], is_output: bool = False) -> str:
    """信号の描き方: 数値は analog（物理値の波形）、ON/OFF は binary、他は concise（文字）。

    出力は確認した時点の値しか分からないので、常に concise（文字の帯。確認前は「?」）。
    値が変わらない数値も、波形にする意味がないので concise にする。
    """
    if is_output or len(set(values)) == 1:
        return "concise"
    if all(NUMBER.match(v) for v in values):
        return "analog"
    if all(v in ("ON", "OFF") for v in values):
        return "binary"
    return "concise"


def _unit_of(values: list[str]) -> str:
    return NUMBER.match(values[0]).group(2)


def _range_of(nums: list[float]) -> tuple[float, float]:
    """縦軸の範囲。軸の上下に実際の最小値・最大値が出るようにする。"""
    return min(nums), max(nums)


def _num(x: float) -> str:
    return str(int(x)) if float(x).is_integer() else str(x)


def render(chart: Chart) -> str:
    signals = chart.inputs + chart.outputs
    ids = {name: f"s{i}" for i, name in enumerate(signals)}
    series: dict[str, list[tuple[int, str]]] = {name: [] for name in signals}
    edge_ms = max(1, chart.end_ms // 100)  # 数値が切り替わる前後の傾き（階段状に見せる）
    check_ms = max(1, chart.end_ms // 50)  # 確認時点の帯の幅
    # 確認の直後に変わる入力は、確認と同じ時刻に描くと「その値で確認した」ように見える。
    # 帯の幅だけ後ろにずらす（次の「経過する」の最小 10 ms を超えない範囲）。
    after_ms = min(check_ms, 9)
    for t, name, value, after_check in chart.events:
        series[name].append((t + after_ms if after_check else t, value))
    kinds = {n: _kind_of([v for _, v in series[n]], n in chart.outputs) for n in signals}
    right_ms = chart.end_ms + 2 * check_ms  # 右端: 最後の確認の帯が収まる余白

    lines = [
        "@startuml",
        "skinparam defaultFontName IPAGothic",
        f"title {chart.title}",
        f"scale {right_ms} as {CHART_WIDTH_PX // 2} pixels",
    ]
    if chart.notes:
        lines.append("legend left")
        lines.extend(f"  {note}" for note in chart.notes)
        lines.append("endlegend")
    for name in signals:
        values = [v for _, v in series[name]]
        label = name + (" (期待)" if name in chart.outputs else "")
        if kinds[name] == "analog":
            unit = _unit_of(values)
            lo, hi = _range_of([float(NUMBER.match(v).group(1)) for v in values])
            label += f" [{unit}]" if unit else ""
            lines.append(f'analog "{label}" between {_num(lo)} and {_num(hi)} as {ids[name]}')
        else:
            lines.append(f'{kinds[name]} "{label}" as {ids[name]}')
    lines.append("")

    # 時刻ごとの点を作る。analog は変化の直前にも点を打って、階段状に変化させる。
    points: dict[int, list[str]] = {}

    def put(t: int, name: str, text: str) -> None:
        points.setdefault(t, []).append(f"{ids[name]} is {text}")

    for name in signals:
        kind, prev_t, prev_v = kinds[name], None, None
        for t, value in series[name]:
            if kind == "analog":
                num = _num(float(NUMBER.match(value).group(1)))
                if prev_v is not None and prev_v != num and t - edge_ms > prev_t:
                    put(t - edge_ms, name, prev_v)
                put(t, name, num)
                prev_v = num
            elif kind == "binary":
                put(t, name, "high" if value == "ON" else "low")
            else:
                put(t, name, f'"{value}"')
            prev_t = t
        if series[name] and series[name][0][0] > 0 and kind == "concise":
            put(0, name, '"?"')  # 最初の値が 0 ms より後の信号は、それまで「?」
        if kind == "analog" and prev_t is not None and prev_t < right_ms:
            put(right_ms, name, prev_v)  # 最後の値を図の右端まで延ばす

    for t in sorted(points):
        lines.append(f"@{t}")
        lines.extend(points[t])
    lines.append(f"@{right_ms}")
    for t in sorted(set(chart.checks)):
        lines.append(f"highlight {t} to {t + check_ms} {CHECK_COLOR};line:DimGrey : 確認")
    lines.append("@enduml")
    return "\n".join(lines) + "\n"


def _safe(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|\s]+', "_", name).strip("_")


def convert(feature_path: Path, out_dir: Path) -> list[Path]:
    doc = Parser().parse(TokenScanner(feature_path.read_text(encoding="utf-8")))
    feature = doc["feature"]
    background = []
    for child in feature["children"]:
        if "background" in child:
            background = child["background"]["steps"]

    written = []
    target = out_dir / feature_path.stem
    target.mkdir(parents=True, exist_ok=True)
    for child in feature["children"]:
        scenario = child.get("scenario")
        if not scenario:
            continue
        steps = background + scenario["steps"]
        tags = " ".join(t["name"] for t in scenario["tags"])
        examples = scenario["examples"]
        if not examples:
            variants = [(scenario["name"], {})]
        else:
            variants = []
            for ex in examples:
                header = [c["value"] for c in ex["tableHeader"]["cells"]]
                for i, r in enumerate(ex["tableBody"], 1):
                    row = dict(zip(header, [c["value"] for c in r["cells"]], strict=True))
                    label = ", ".join(f"{k}={v}" for k, v in row.items() if k != "備考")
                    variants.append((f"{scenario['name']} [{i}] {label}", row))
        for i, (name, row) in enumerate(variants, 1):
            title = f"{feature['name']} / {name}" + (f"  {tags}" if tags else "")
            chart = build_chart(title, steps, row)
            suffix = f"_{i:02d}" if examples else ""
            path = target / f"{_safe(scenario['name'])}{suffix}.puml"
            path.write_text(render(chart), encoding="utf-8")
            written.append(path)
    return written


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    src, out = Path(argv[1]), Path(argv[2])
    total = 0
    for feature in sorted(src.glob("*.feature")):
        total += len(convert(feature, out))
    print(f"{total} 個のタイミングチャート(.puml)を {out}/ に出力しました")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
