"""ECU 共有ライブラリ (libecu.so) を ctypes で呼ぶ薄いラッパ。"""

import ctypes
import os
from pathlib import Path

ECU_STEP_MS = 10
DEFAULT_LIB = Path(__file__).resolve().parent.parent / "build" / "libecu.so"


class EcuInputs(ctypes.Structure):
    """ecu/include/ecu.h の EcuInputs と同じ並び。"""

    _fields_ = [
        ("coolant_temp_c", ctypes.c_int32),  # 水温 [℃]
        ("engine_rpm", ctypes.c_int32),  # エンジン回転数 [rpm]
        ("throttle_pct", ctypes.c_int32),  # スロットル開度 [%]（0 = 全閉）
        ("vehicle_speed_kmh", ctypes.c_int32),  # 車速 [km/h]
        ("ect_sensor_mv", ctypes.c_int32),  # 水温センサ電圧 [mV]
    ]


class EcuOutputs(ctypes.Structure):
    """ecu/include/ecu.h の EcuOutputs と同じ並び。"""

    _fields_ = [
        ("target_idle_rpm", ctypes.c_int32),  # 目標アイドル回転数 [rpm]
        ("fuel_cut", ctypes.c_int32),  # 燃料カット 0: 噴射 / 1: カット
        ("gear", ctypes.c_int32),  # 推奨ギア 1..4
        ("ect_used_c", ctypes.c_int32),  # 制御用水温 [℃]（センサ故障時は代替値）
        ("dtc", ctypes.c_int32),  # 確定DTC（0: なし、0x0117 など）
    ]


class EcuDriver:
    """入力を保持し、時間を進めて出力を読む。"""

    def __init__(self, lib_path: str | os.PathLike | None = None):
        path = lib_path or os.environ.get("ECU_LIB") or DEFAULT_LIB
        self._lib = ctypes.CDLL(str(path))
        self._lib.ecu_set_inputs.argtypes = [ctypes.POINTER(EcuInputs)]
        self._lib.ecu_get_outputs.argtypes = [ctypes.POINTER(EcuOutputs)]
        self.reset()

    def reset(self) -> None:
        self._lib.ecu_init()
        # 平常状態: 暖機済み・停止・センサ正常
        self.inputs = EcuInputs(
            coolant_temp_c=90,
            engine_rpm=0,
            throttle_pct=0,
            vehicle_speed_kmh=0,
            ect_sensor_mv=2000,
        )
        self.elapsed_ms = 0

    def set_input(self, name: str, value: int) -> None:
        if not hasattr(self.inputs, name):
            raise AttributeError(f"未定義の入力: {name}")
        setattr(self.inputs, name, int(value))

    def run_for_ms(self, ms: int) -> None:
        if ms % ECU_STEP_MS:
            raise ValueError(f"{ms} ms は制御周期 {ECU_STEP_MS} ms の倍数にしてください")
        self._lib.ecu_set_inputs(ctypes.byref(self.inputs))
        for _ in range(ms // ECU_STEP_MS):
            self._lib.ecu_step()
        self.elapsed_ms += ms

    @property
    def outputs(self) -> EcuOutputs:
        out = EcuOutputs()
        self._lib.ecu_get_outputs(ctypes.byref(out))
        return out
