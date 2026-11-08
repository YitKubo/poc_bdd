"""AT 変速判定

仕様（しきい値の根拠）: docs/specs/at_shift.md
振る舞い（条件と期待値）: tests/features/at_shift.feature
ここには条件・期待値を書かない。ステップの意味は common_steps.py を参照。
"""

from pytest_bdd import scenarios

scenarios("at_shift.feature")
