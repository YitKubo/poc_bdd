"""アイドル回転数制御

仕様（しきい値の根拠）: docs/specs/idle_speed.md
振る舞い（条件と期待値）: tests/features/idle_speed.feature
ここには条件・期待値を書かない。ステップの意味は common_steps.py を参照。
"""

from pytest_bdd import scenarios

scenarios("idle_speed.feature")
