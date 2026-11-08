---
name: spec-to-gherkin
description: 仕様書(docs/specs/*.md)または口頭・チャットで説明された ECU の振る舞いから、Gherkin の feature（キーワードは英語、記述は日本語）の ファイルを tests/features/ に生成する。「仕様をGherkinにして」「このふるまいのシナリオを書いて」と頼まれたときに使う。
---

# 仕様 → Gherkin

仕様書や口頭の説明から、`tests/features/<名前>.feature` を作る。
合否を決めるテストなので、**具体的な値**で書く。

## 手順

1. **入力を読む**
   - 仕様書のパスが渡されたら読む。無ければ会話の内容を元にする
   - 既存の `tests/features/*.feature` と `tests/steps/common_steps.py` を読み、使えるステップを把握する
2. **あいまいな点を質問する**（推測で埋めない）
   - 数値のしきい値と単位、「以上」か「超え」か（境界を含むか）
   - 時間条件（何 ms 続いたら、連続か累計か）
   - 異常時・復帰時の振る舞い
   - 仕様書が無い場合は、ここで決まった内容を `docs/specs/<名前>.md` の下書き（目的・振る舞い・パラメータ表）にして先に作る
3. **シナリオを設計する**
   - 代表的な流れ 1 本（時間で状態が変わる機能だけ。`@代表動作` タグを付ける）
   - 境界値・異常系は `Scenario Outline` + `Examples:` の表にする（境界の両側 2 値ずつ）
   - 1 シナリオ 1 振る舞い。「経過する」が 3 回以上出る長い流れは、分割する
4. **feature を書く**（下のルールに従う）
5. **整形して確認する**: `docker compose run --rm dev make fmt` → `docker compose run --rm dev make chart`
   （チャートが出れば、ステップの形が正しい）
6. 作った feature の一覧と、足りないステップがあれば知らせる（→ `gherkin-to-pytest` を案内）

## 書き方のルール

- 1 行目は `# language: en`（キーワードは英語、ステップ文・シナリオ名・説明文は日本語）、2 行目に `# 仕様: docs/specs/<名前>.md`
- キーワード: `Feature` `Background` `Scenario` `Scenario Outline` `Examples` `Given` `When` `Then` `And`
- **ステップの形を揃える**（そのままタイミングチャートに変換されるため）
  - 信号: `〇〇が "値 単位" である`（例: `エンジン回転数が "3000 rpm" である`、`燃料カットが "ON" である`）
  - 時間: `"N ms" 経過する`（N は 10 の倍数）
  - **値（数値・単位・ON/OFF・DTC）は必ずダブルクォートで囲む**。数値と単位の間は半角スペース。アウトラインは `"<rpm> rpm"`
- `Given`/`When` は入力、`Then` は出力の確認にだけ使う
- 出力の確認の前に、必ず `"10 ms" 経過する` 以上の時間を進める
- 値はすべて仕様書のパラメータ表から取る。仕様書に無い数値を作らない
- 既存のステップの言い回しを優先する。新しい信号が必要なら、言い回しを同じ形にして新しく作る

## 例

```gherkin
# language: en
# 仕様: docs/specs/rev_limiter.md
Feature: レブリミッタ
  エンジン回転数が上限に達したら燃料をカットする。

  Background:
    Given ECUが初期化されている

  Scenario Outline: カット開始条件
    Given エンジン回転数が "<rpm> rpm" である
    When "10 ms" 経過する
    Then 燃料カットが "<state>" である

    Examples:
      | rpm  | state |
      | 6499 | OFF   |
      | 6500 | ON    |
```
