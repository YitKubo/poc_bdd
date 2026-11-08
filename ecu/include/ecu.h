#ifndef ECU_H
#define ECU_H

#include <stdint.h>

/* 制御周期 [ms] */
#define ECU_STEP_MS 10

/* ---- パラメータ（docs/specs 配下の仕様書の表と一致させる） ---- */

/* アイドル回転数制御 */
#define IDLE_COLD_BELOW_C 20 /* この温度未満: 冷間 */
#define IDLE_WARM_FROM_C 60  /* この温度以上: 暖機後 */
#define IDLE_COLD_RPM 1200
#define IDLE_MID_RPM 1000
#define IDLE_WARM_RPM 750

/* 減速時燃料カット */
#define DECEL_THROTTLE_CLOSED_PCT 2 /* この開度以下: 全閉 */
#define DECEL_CUT_ABOVE_RPM 1500    /* 超えたらカット */
#define DECEL_RECOVER_RPM 1100      /* 以下で復帰 */

/* レブリミッタ */
#define REV_LIMIT_RPM 6500   /* 以上でカット */
#define REV_RECOVER_RPM 6300 /* 以下で復帰 */

/* 水温センサ故障検出 */
#define ECT_MV_MIN 200  /* 未満: 断線等 (P0117) */
#define ECT_MV_MAX 4800 /* 超え: ショート等 (P0118) */
#define ECT_DEBOUNCE_MS 500
#define ECT_FAILSAFE_C 80
#define DTC_ECT_LOW 0x0117
#define DTC_ECT_HIGH 0x0118

/* AT 変速判定 */
#define SHIFT_THROTTLE_HIGH_PCT 30 /* 以上: 高開度マップ */

/* ---- 入出力 ---- */
typedef struct {
    int32_t coolant_temp_c;
    int32_t engine_rpm;
    int32_t throttle_pct;
    int32_t vehicle_speed_kmh;
    int32_t ect_sensor_mv;
} EcuInputs;

typedef struct {
    int32_t target_idle_rpm;
    int32_t fuel_cut;   /* 0: 噴射 / 1: カット */
    int32_t gear;       /* 推奨ギア 1..4 */
    int32_t ect_used_c; /* 制御に使う水温 */
    int32_t dtc;        /* 確定DTC (0: なし) */
} EcuOutputs;

void ecu_init(void);
void ecu_set_inputs(const EcuInputs *in);
void ecu_step(void); /* ECU_STEP_MS 分進める */
void ecu_get_outputs(EcuOutputs *out);

#endif
