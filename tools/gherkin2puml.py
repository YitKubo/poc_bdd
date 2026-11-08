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

ELAPSE = re.compile(r"^(\d+)\s*ms\s*経過する$")
SIGNAL = re.compile(r"^(?P<name>.+?)が\s*(?P<value>.+?)\s*である$")
CHECK_WIDTH_MS = 10  # 確認時点の強調表示の幅


@dataclass
class Chart:
    title: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    events: list[tuple[int, str, str]] = field(default_factory=list)  # (時刻, 信号, 値)
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
    for step, kind in zip(steps, _step_kinds(steps), strict=True):
        text = _fill(step["text"], row).strip()
        m = ELAPSE.match(text)
        if m:
            now += int(m.group(1))
            continue
        m = SIGNAL.match(text)
        if not m:
            chart.notes.append(text)
            continue
        name, value = m.group("name"), m.group("value")
        if kind == "Outcome":
            if name not in chart.outputs:
                chart.outputs.append(name)
            chart.checks.append(now)
        elif name not in chart.inputs:
            chart.inputs.append(name)
        chart.events.append((now, name, value))
    chart.end_ms = now
    return chart


def render(chart: Chart) -> str:
    signals = chart.inputs + chart.outputs
    ids = {name: f"s{i}" for i, name in enumerate(signals)}
    first_at = {}
    for t, name, _ in chart.events:
        first_at.setdefault(name, t)

    lines = ["@startuml", "skinparam defaultFontName IPAGothic", f"title {chart.title}"]
    if chart.notes:
        lines.append("legend left")
        lines.extend(f"  {note}" for note in chart.notes)
        lines.append("endlegend")
    for name in chart.inputs:
        lines.append(f'concise "{name}" as {ids[name]}')
    for name in chart.outputs:
        lines.append(f'concise "{name} (期待)" as {ids[name]}')
    lines.append("")

    by_time: dict[int, list[tuple[str, str]]] = {}
    for t, name, value in chart.events:
        by_time.setdefault(t, []).append((name, value))
    for name in signals:  # 最初の値が 0 ms より後の信号は、それまで「?」にする
        if first_at.get(name, 0) > 0:
            by_time.setdefault(0, []).append((name, "?"))

    for t in sorted(by_time):
        lines.append(f"@{t}")
        for name, value in by_time[t]:
            lines.append(f'{ids[name]} is "{value}"')
    if chart.end_ms not in by_time:
        lines.append(f"@{chart.end_ms}")
    for t in sorted(set(chart.checks)):
        lines.append(f"highlight {t} to {t + CHECK_WIDTH_MS} #Gold;line:DimGrey : 確認")
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
                    label = ", ".join(f"{k}={v}" for k, v in row.items())
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
