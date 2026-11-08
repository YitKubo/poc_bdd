#include "ecu.h"
#include "ecu_internal.h"

/* 各ギアへ上がる車速 [km/h]: 2速, 3速, 4速 */
static const int32_t k_up_low[3] = {20, 40, 60};  /* 低開度 */
static const int32_t k_up_high[3] = {30, 60, 90}; /* 高開度 */

int32_t shift_gear(int32_t speed_kmh, int32_t throttle_pct) {
    const int32_t *up = throttle_pct >= SHIFT_THROTTLE_HIGH_PCT ? k_up_high : k_up_low;
    int32_t gear = 1;
    for (int i = 0; i < 3; i++) {
        if (speed_kmh >= up[i]) {
            gear = i + 2;
        }
    }
    return gear;
}
