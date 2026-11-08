# poc_bdd

パワトレ ECU（C 実装）の振る舞いを、日本語 Gherkin → pytest-bdd で自動テストする PoC。

## 基本ルール

- **1 機能 = 仕様書 1 枚 + feature 1 本**
  - `docs/specs/<名前>.md` — 人が読む仕様。数値（しきい値）はここの表が正
  - `tests/features/<名前>.feature` — 合否を決めるテスト。値は仕様書の表から取る
- `charts/` は feature から自動生成するタイミングチャート。**手で書かない・git 管理しない**
- 合否の判定は feature だけで行う

## コマンド（ホストから。すべて docker compose 経由）

| やりたいこと | コマンド |
|---|---|
| テスト | `docker compose run --rm test`（または `make docker-test`） |
| タイミングチャート生成 | `make docker-chart` |
| 整形 | `docker compose run --rm dev make fmt` |
| 書式チェック | `make docker-lint` |

Dev Container の中では `make test` / `make chart` / `make fmt` / `make lint` を直接使う。

## 構成

- `ecu/` — テスト対象の C。`libecu.so` を `build/` に作る
- `tests/ecu_driver.py` — ctypes ラッパ
- `tests/steps/common_steps.py` — 共通ステップ。`test_*.py` は `scenarios()` で feature を結びつけるだけ
- `tools/gherkin2puml.py` — feature → タイミングチャート

## スキル

- `/spec-to-gherkin` — 仕様書や口頭の説明 → feature
- `/gherkin-to-pytest` — feature → pytest-bdd のステップとテスト

流れ: 仕様 → `/spec-to-gherkin` → feature をレビュー（`make docker-chart` の図も使う）→ `/gherkin-to-pytest` → テスト実行

## 書式

保存時に自動整形する。Python は ruff、C は clang-format、Gherkin は reformat-gherkin。
ステップ文は「`〇〇が 値 単位 である`」「`N ms 経過する`」の形にする（チャート変換のため）。
