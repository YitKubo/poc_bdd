"""全 feature で共有するステップ定義 ＝ 日本語の言葉と ECU 信号の「辞書」。

このファイルには振る舞い（どの条件で何が起きるか）を書かない。
振る舞いは tests/features/*.feature、しきい値の根拠は docs/specs/*.md を読む。

| ステップ文                       | 種別 | ECU フィールド      | 単位・値                |
|----------------------------------|------|---------------------|-------------------------|
| 水温が N ℃ である                | 入力 | coolant_temp_c      | ℃                       |
| エンジン回転数が N rpm である    | 入力 | engine_rpm          | rpm                     |
| スロットル開度が N % である      | 入力 | throttle_pct        | % (0=全閉)              |
| 車速が N km/h である             | 入力 | vehicle_speed_kmh   | km/h                    |
| 水温センサ電圧が N mV である     | 入力 | ect_sensor_mv       | mV                      |
| N ms 経過する                    | 時間 | （ecu_step を N/10 回） | ms (10 の倍数)        |
| 目標アイドル回転数が N rpm である | 出力 | target_idle_rpm     | rpm                     |
| 燃料カットが ON/OFF である       | 出力 | fuel_cut            | ON=1(カット) / OFF=0    |
| 確定DTCが X である               | 出力 | dtc                 | なし / P0117 / P0118    |
| 制御用水温が N ℃ である          | 出力 | ect_used_c          | ℃ (故障時は代替値)      |
| 推奨ギアが N 速 である           | 出力 | gear                | 1..4                    |

入力は「前提」でも「もし」でも使える。値はセットされるだけで、ECU に渡るのは
次の「N ms 経過する」のとき（tests/ecu_driver.py の run_for_ms）。
「ECUが初期化されている」の直後の入力値は EcuDriver.reset() の平常状態
（暖機済み 90 ℃・停止・センサ正常 2000 mV）。

ステップの文は「〇〇が 値 [単位] である」「N ms 経過する」の形に揃える。
この形は tools/gherkin2puml.py がタイミングチャートへ変換する際にも使われる。
"""

import pytest
from ecu_driver import EcuDriver
from pytest_bdd import given, parsers, then, when

# 確定DTCの表記 → ECU の dtc 値
DTC_CODES = {
    "なし": 0,
    "P0117": 0x0117,  # 水温センサ電圧が下限未満
    "P0118": 0x0118,  # 水温センサ電圧が上限超え
}


@pytest.fixture
def ecu() -> EcuDriver:
    return EcuDriver()


# ---- 前提 / もし: 入力 ----


@given("ECUが初期化されている")
def _init(ecu):
    """ECU を初期化し、入力を平常状態に戻す。"""
    ecu.reset()


@given(parsers.parse("水温が {temp:d} ℃ である"))
@when(parsers.parse("水温が {temp:d} ℃ である"))
def _coolant_temp(ecu, temp):
    """入力 coolant_temp_c [℃]"""
    ecu.set_input("coolant_temp_c", temp)


@given(parsers.parse("エンジン回転数が {rpm:d} rpm である"))
@when(parsers.parse("エンジン回転数が {rpm:d} rpm である"))
def _engine_rpm(ecu, rpm):
    """入力 engine_rpm [rpm]"""
    ecu.set_input("engine_rpm", rpm)


@given(parsers.parse("スロットル開度が {pct:d} % である"))
@when(parsers.parse("スロットル開度が {pct:d} % である"))
def _throttle(ecu, pct):
    """入力 throttle_pct [%]（0 = 全閉）"""
    ecu.set_input("throttle_pct", pct)


@given(parsers.parse("車速が {kmh:d} km/h である"))
@when(parsers.parse("車速が {kmh:d} km/h である"))
def _speed(ecu, kmh):
    """入力 vehicle_speed_kmh [km/h]"""
    ecu.set_input("vehicle_speed_kmh", kmh)


@given(parsers.parse("水温センサ電圧が {mv:d} mV である"))
@when(parsers.parse("水温センサ電圧が {mv:d} mV である"))
def _ect_mv(ecu, mv):
    """入力 ect_sensor_mv [mV]"""
    ecu.set_input("ect_sensor_mv", mv)


@when(parsers.parse("{ms:d} ms 経過する"))
def _elapse(ecu, ms):
    """現在の入力を ECU に渡し、10 ms 周期の ecu_step を ms/10 回まわす。"""
    ecu.run_for_ms(ms)


# ---- ならば: 出力 ----


@then(parsers.parse("目標アイドル回転数が {rpm:d} rpm である"))
def _check_idle(ecu, rpm):
    """出力 target_idle_rpm [rpm]"""
    assert ecu.outputs.target_idle_rpm == rpm


@then(parsers.parse("燃料カットが {state} である"))
def _check_fuel_cut(ecu, state):
    """出力 fuel_cut: ON = 1（噴射カット）/ OFF = 0（噴射）"""
    assert state in ("ON", "OFF"), f"ON か OFF で指定してください: {state}"
    assert ecu.outputs.fuel_cut == (1 if state == "ON" else 0)


@then(parsers.parse("確定DTCが {code} である"))
def _check_dtc(ecu, code):
    """出力 dtc: DTC_CODES の表記で指定（なし = 0）"""
    assert code in DTC_CODES, f"未定義のDTC: {code}"
    assert ecu.outputs.dtc == DTC_CODES[code]


@then(parsers.parse("制御用水温が {temp:d} ℃ である"))
def _check_ect_used(ecu, temp):
    """出力 ect_used_c [℃]: 制御に使う水温（センサ故障時は代替値）"""
    assert ecu.outputs.ect_used_c == temp


@then(parsers.parse("推奨ギアが {gear:d} 速 である"))
def _check_gear(ecu, gear):
    """出力 gear: 推奨ギア 1..4"""
    assert ecu.outputs.gear == gear
