"""レブリミッタ

仕様（しきい値の根拠）: docs/specs/rev_limiter.md
振る舞い（条件と期待値）: tests/features/rev_limiter.feature
ここには条件・期待値を書かない。ステップの意味は common_steps.py を参照。
"""

from pytest_bdd import scenarios

scenarios("rev_limiter.feature")
