# poc_bdd

パワトレ ECU（C 実装）の振る舞いを、日本語 Gherkin → pytest-bdd で自動テストする PoC。

## 基本ルール

- **1 機能 = 仕様書 1 枚 + feature 1 本**
  - `docs/specs/<名前>.md` — 人が読む仕様。数値（しきい値）はここの表が正
  - `tests/features/<名前>.feature` — 合否を決めるテスト。値は仕様書の表から取る
- `charts/` は feature から自動生成するタイミングチャート。**手で書かない**。`.puml` / `.svg` / `.png` はレビュー用に git 管理する（feature を変えたら再生成して一緒にコミット）
- 合否の判定は feature だけで行う

## コマンド（ホストから。すべて docker compose 経由）

| やりたいこと | コマンド |
|---|---|
| テスト | `docker compose run --rm test`（または `make docker-test`） |
| タイミングチャート生成（.puml/.svg/.png） | `make docker-chart` |
| 整形 | `docker compose run --rm dev make fmt` |
| 書式チェック | `make docker-lint` |

Dev Container の中では `make test` / `make chart` / `make fmt` / `make lint` を直接使う。

## 言語ルール

- **Gherkin のキーワードは英語**: `# language: en`、`Feature` `Background` `Scenario` `Scenario Outline` `Examples` `Given` `When` `Then` `And`
- **記述は日本語**: ステップ文、シナリオ名、Feature の説明文、タグ、コメントは日本語（例: `Given 車速が 40 km/h である`）
- 仕様書（`docs/specs/*.md`）も日本語

## 構成

- `ecu/` — テスト対象の C。`libecu.so` を `build/` に作る
- `tests/ecu_driver.py` — ctypes ラッパ
- `tests/steps/common_steps.py` — 共通ステップ。`test_*.py` は `scenarios()` で feature を結びつけるだけ
- `tools/gherkin2puml.py` — feature → タイミングチャート

## スキル

- `/spec-to-gherkin` — 仕様書や口頭の説明 → feature
- `/gherkin-to-pytest` — feature → pytest-bdd のステップとテスト
- `/chart-review` — 生成したチャートを AI が画像として見て、仕様・feature との食い違いと見にくさを確認する

流れ: 仕様 → `/spec-to-gherkin` → feature をレビュー（`make docker-chart` の図も使う）→ `/chart-review` → `/gherkin-to-pytest` → テスト実行

## 書式

保存時に自動整形する。Python は ruff、C は clang-format、Gherkin は reformat-gherkin。
ステップ文は「`〇〇が "値 単位" である`」「`"N ms" 経過する`」の形にする（値はダブルクォートで囲む。例: `エンジン回転数が "1200 rpm" である` / `燃料カットが "ON" である` / `"10 ms" 経過する`）（チャート変換のため）。
