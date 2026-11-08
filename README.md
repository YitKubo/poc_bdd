# poc_bdd

パワトレ ECU の振る舞いを **日本語 Gherkin → pytest-bdd** で自動テストする仕組みの PoC です。
pytest は Docker（compose）上で動かします。

```
仕様書(md) ─spec-to-gherkin→ feature ─gherkin-to-pytest→ pytest ─docker compose→ 合否レポート
                                │
                                └─ make chart → タイミングチャート（期待波形）
```

## 使い方

```bash
docker compose run --rm test     # ビルド + 全シナリオ実行（reports/ にHTMLとcucumber.json）
make docker-chart                # feature からタイミングチャート(SVG)を charts/ に生成
make docker-lint                 # 書式チェック
```

VSCode では「Dev Containers: Reopen in Container」で開くと、拡張機能（Cucumber、Python、Ruff、
clang-format、PlantUML など）が入った状態で、同じ compose の `dev` サービスの中で作業できます。

## 題材（テスト対象の ECU）

| 機能 | 仕様書 | feature |
|---|---|---|
| アイドル回転数制御 | [idle_speed.md](docs/specs/idle_speed.md) | [idle_speed.feature](tests/features/idle_speed.feature) |
| 減速時燃料カット | [decel_fuel_cut.md](docs/specs/decel_fuel_cut.md) | [decel_fuel_cut.feature](tests/features/decel_fuel_cut.feature) |
| レブリミッタ | [rev_limiter.md](docs/specs/rev_limiter.md) | [rev_limiter.feature](tests/features/rev_limiter.feature) |
| 水温センサ故障検出 | [ect_sensor_diag.md](docs/specs/ect_sensor_diag.md) | [ect_sensor_diag.feature](tests/features/ect_sensor_diag.feature) |
| AT 変速判定 | [at_shift.md](docs/specs/at_shift.md) | [at_shift.feature](tests/features/at_shift.feature) |

詳しいルールは [CLAUDE.md](CLAUDE.md) を参照してください。
