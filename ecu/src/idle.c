#include "ecu.h"
#include "ecu_internal.h"

void idle_init(void) {}

int32_t idle_target_rpm(int32_t ect_c) {
    if (ect_c < IDLE_COLD_BELOW_C) {
        return IDLE_COLD_RPM;
    }
    if (ect_c < IDLE_WARM_FROM_C) {
        return IDLE_MID_RPM;
    }
    return IDLE_WARM_RPM;
}
