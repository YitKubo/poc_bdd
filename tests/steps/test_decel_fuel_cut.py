"""減速時燃料カット

仕様（しきい値の根拠）: docs/specs/decel_fuel_cut.md
振る舞い（条件と期待値）: tests/features/decel_fuel_cut.feature
ここには条件・期待値を書かない。ステップの意味は common_steps.py を参照。
"""

from pytest_bdd import scenarios

scenarios("decel_fuel_cut.feature")
