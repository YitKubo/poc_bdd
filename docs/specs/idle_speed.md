# アイドル回転数制御

テスト: [idle_speed.feature](../../tests/features/idle_speed.feature)

## 目的

エンジンが冷えているときはアイドル回転数を上げて安定させ、暖まったら下げて燃費を良くする。

## 振る舞い

制御用水温から目標アイドル回転数を決める。

## パラメータ

| 名前 | 値 | 意味 |
|---|---|---|
| IDLE_COLD_BELOW_C | 20 ℃ | これ未満は冷間 |
| IDLE_WARM_FROM_C | 60 ℃ | これ以上は暖機後 |
| IDLE_COLD_RPM | 1200 rpm | 冷間の目標 |
| IDLE_MID_RPM | 1000 rpm | 20 ℃ 以上 60 ℃ 未満の目標 |
| IDLE_WARM_RPM | 750 rpm | 暖機後の目標 |

## 補足

水温センサが故障しているときの制御用水温は [ect_sensor_diag.md](ect_sensor_diag.md) を参照。
