"""全 feature で共有するステップ定義。

ステップの文は「〇〇が 値 [単位] である」「N ms 経過する」の形に揃える。
この形は tools/gherkin2puml.py がタイミングチャートへ変換する際にも使われる。
"""

import pytest
from ecu_driver import EcuDriver
from pytest_bdd import given, parsers, then, when

DTC_CODES = {"なし": 0, "P0117": 0x0117, "P0118": 0x0118}


@pytest.fixture
def ecu() -> EcuDriver:
    return EcuDriver()


# ---- 前提 / もし: 入力 ----


@given("ECUが初期化されている")
def _init(ecu):
    ecu.reset()


@given(parsers.parse("水温が {temp:d} ℃ である"))
@when(parsers.parse("水温が {temp:d} ℃ である"))
def _coolant_temp(ecu, temp):
    ecu.set_input("coolant_temp_c", temp)


@given(parsers.parse("エンジン回転数が {rpm:d} rpm である"))
@when(parsers.parse("エンジン回転数が {rpm:d} rpm である"))
def _engine_rpm(ecu, rpm):
    ecu.set_input("engine_rpm", rpm)


@given(parsers.parse("スロットル開度が {pct:d} % である"))
@when(parsers.parse("スロットル開度が {pct:d} % である"))
def _throttle(ecu, pct):
    ecu.set_input("throttle_pct", pct)


@given(parsers.parse("車速が {kmh:d} km/h である"))
@when(parsers.parse("車速が {kmh:d} km/h である"))
def _speed(ecu, kmh):
    ecu.set_input("vehicle_speed_kmh", kmh)


@given(parsers.parse("水温センサ電圧が {mv:d} mV である"))
@when(parsers.parse("水温センサ電圧が {mv:d} mV である"))
def _ect_mv(ecu, mv):
    ecu.set_input("ect_sensor_mv", mv)


@when(parsers.parse("{ms:d} ms 経過する"))
def _elapse(ecu, ms):
    ecu.run_for_ms(ms)


# ---- ならば: 出力 ----


@then(parsers.parse("目標アイドル回転数が {rpm:d} rpm である"))
def _check_idle(ecu, rpm):
    assert ecu.outputs.target_idle_rpm == rpm


@then(parsers.parse("燃料カットが {state} である"))
def _check_fuel_cut(ecu, state):
    assert state in ("ON", "OFF"), f"ON か OFF で指定してください: {state}"
    assert ecu.outputs.fuel_cut == (1 if state == "ON" else 0)


@then(parsers.parse("確定DTCが {code} である"))
def _check_dtc(ecu, code):
    assert code in DTC_CODES, f"未定義のDTC: {code}"
    assert ecu.outputs.dtc == DTC_CODES[code]


@then(parsers.parse("制御用水温が {temp:d} ℃ である"))
def _check_ect_used(ecu, temp):
    assert ecu.outputs.ect_used_c == temp


@then(parsers.parse("推奨ギアが {gear:d} 速 である"))
def _check_gear(ecu, gear):
    assert ecu.outputs.gear == gear
