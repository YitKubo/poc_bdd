#include "ecu.h"
#include "ecu_internal.h"

static int32_t g_decel_cut;
static int32_t g_rev_cut;

void fuel_cut_init(void) {
    g_decel_cut = 0;
    g_rev_cut = 0;
}

void fuel_cut_step(int32_t rpm, int32_t throttle_pct) {
    int32_t closed = throttle_pct <= DECEL_THROTTLE_CLOSED_PCT;

    /* 減速時燃料カット: 全閉かつ高回転で開始、低回転またはアクセル操作で復帰 */
    if (!g_decel_cut) {
        if (closed && rpm > DECEL_CUT_ABOVE_RPM) {
            g_decel_cut = 1;
        }
    } else if (!closed || rpm <= DECEL_RECOVER_RPM) {
        g_decel_cut = 0;
    }

    /* レブリミッタ: 上限で開始、下限まで下がったら復帰 */
    if (!g_rev_cut) {
        if (rpm >= REV_LIMIT_RPM) {
            g_rev_cut = 1;
        }
    } else if (rpm <= REV_RECOVER_RPM) {
        g_rev_cut = 0;
    }
}

int32_t fuel_cut_active(void) {
    return g_decel_cut || g_rev_cut;
}
