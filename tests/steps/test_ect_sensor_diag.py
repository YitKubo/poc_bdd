"""水温センサ故障検出

仕様（しきい値の根拠）: docs/specs/ect_sensor_diag.md
振る舞い（条件と期待値）: tests/features/ect_sensor_diag.feature
ここには条件・期待値を書かない。ステップの意味は common_steps.py を参照。
"""

from pytest_bdd import scenarios

scenarios("ect_sensor_diag.feature")
