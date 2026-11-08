---
name: gherkin-to-pytest
description: tests/features/ の Gherkin(feature) から pytest-bdd のテストコードを生成する。足りないステップ定義と、feature に対応する test_*.py を作り、docker compose で実行して通す。「featureをpytestにして」「テストコードを作って」と頼まれたときに使う。
---

# Gherkin → pytest-bdd

入力は **feature ファイルだけ**。仕様書やチャートからテストの判定を作らない。

## 手順

1. **対象の feature を読む**（パスが無ければ、`tests/features/<名前>.feature` のうち `tests/steps/test_<名前>.py` が無いものを探す。名前は拡張子を除いて対応させる）
   - **すべてにテストがあるとき**は、ステップが足りるかを手順 6 の実行で確かめて終わる（手順 2〜5 は、実行して失敗したときだけ行う）
2. **ステップを洗い出す**: 背景・シナリオ・アウトラインのステップ文を全部集める
   （アウトラインの文には `<列名>` がそのまま残っている。照合するときは、例の値を入れた形に自分で置き換えて考える）
3. **既存の定義と照合する**: `tests/steps/common_steps.py` を読み、一致するものは再利用する
4. **足りないステップだけ追加する**（`tests/steps/common_steps.py` に書く）
   - 入力: `@given(parsers.parse(...))` と `@when(parsers.parse(...))` を重ねて付け、`ecu.set_input("<フィールド名>", 値)` を呼ぶ
   - 出力: `@then(parsers.parse(...))` で `ecu.outputs.<フィールド名>` を `assert` する
   - 数値は `{名前:d}`（`-10` のような負の数も通る）、ON/OFF などの文字列は `{名前}` で受ける
   - ステップ文の形は CLAUDE.md の書式ルールに従う（`〇〇が "値 単位" である`。値はダブルクォート）。
     この形は `tools/gherkin2puml.py` のチャート変換が前提にしているので、崩さない
   - 関数には `"""入力 <フィールド名> [単位]"""` / `"""出力 <フィールド名> ..."""` の docstring を付け、
     `common_steps.py` 冒頭の対応表にも 1 行足す（Python だけで信号の意味が分かるように）
   - 入力・出力のフィールドが ECU に無ければ、`ecu/include/ecu.h` と `tests/ecu_driver.py` の両方に足す。
     C のコードを変えることになるので、**対話できるときは先にユーザーに知らせて了承を得る**。
     非対話で動いているときは、足さずに「必要なフィールドとその理由」を報告して、**その feature の分だけ**止める
     （止めた feature のテストファイルは作らない。他の feature の手順 6・7 は続ける。報告に、止めた feature と必要なものを書く）
5. **テストファイルを作る**: `tests/steps/test_<feature名>.py`

   ```python
   """機能名

   仕様（しきい値の根拠）: docs/specs/<feature名>.md（仕様書が無い feature は「仕様書なし」と書く）
   振る舞い（条件と期待値）: tests/features/<feature名>.feature
   ここには条件・期待値を書かない。ステップの意味は common_steps.py を参照。
   """

   from pytest_bdd import scenarios

   scenarios("<feature名>.feature")
   ```

   （`bdd_features_base_dir` が `tests/features` なので、ファイル名だけでよい）
6. **実行する**: `docker compose run --rm test`
   - 成功の基準は、**全件通過**し、件数が全 feature のシナリオ数の合計と一致すること。
     `Scenario Outline` は `Examples` の**データ行**の数（列名の行は数えない）。数え方の例:

     ```bash
     for f in tests/features/*.feature; do
       awk -v f="$(basename "$f")" '
         /^[[:space:]]*Scenario:/ { n++ }
         /^[[:space:]]*Examples:/ { e=1; h=1; next }
         /^[[:space:]]*Scenario/ { e=0 }
         e && /^[[:space:]]*\|/ { if (h) h=0; else n++ }
         END { print f, n }' "$f"
     done
     ```
   - `StepDefinitionNotFoundError` が出たら、ステップ文との不一致を直す。**feature の文を変えるのは最後の手段**（変えるなら理由を伝える）。
     アウトラインでは、`<列名>` を例の値に置き換えた文と、ステップの書式（`{ms:d}` の後ろの ` ms"` など）が合っているかを見る
   - 失敗したテストは、feature・ステップ・ECU のどれが原因かを切り分けて報告する。**合格させるために期待値を書き換えない**
7. **整形する**: `docker compose run --rm dev make fmt` → `make docker-lint`（ホストの `make lint` は動かない。
   `fmt` は Python・C に加えて **feature も整形する**。変わるのは空白や `# language: en` の削除などの書式だけで、ステップの文は変わらない。
   手順 6 の「feature の文を変えない」は、テストを通すために文を書き換えないという意味）
8. 結果（通ったシナリオ数、追加したステップ）を短く報告する

## 注意

- 「経過する」は `ecu.run_for_ms(ms)` を呼ぶ。ECU の周期は 10 ms
- 各シナリオは新しい `ecu` fixture（`ecu.reset()` 済み）で始まる
- ステップ名は日本語のまま。関数名は `_` 始まりの英語でよい
