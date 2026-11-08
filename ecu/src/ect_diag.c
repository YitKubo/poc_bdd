#include "ecu.h"
#include "ecu_internal.h"

static int32_t g_pending; /* 判定中の故障コード */
static int32_t g_fault_ms;
static int32_t g_ok_ms;
static int32_t g_dtc;

void ect_diag_init(void) {
    g_pending = 0;
    g_fault_ms = 0;
    g_ok_ms = 0;
    g_dtc = 0;
}

void ect_diag_step(int32_t sensor_mv) {
    int32_t fault = 0;
    if (sensor_mv < ECT_MV_MIN) {
        fault = DTC_ECT_LOW;
    } else if (sensor_mv > ECT_MV_MAX) {
        fault = DTC_ECT_HIGH;
    }

    if (fault) {
        g_ok_ms = 0;
        if (fault != g_pending) {
            g_pending = fault;
            g_fault_ms = 0;
        }
        g_fault_ms += ECU_STEP_MS;
        if (g_fault_ms >= ECT_DEBOUNCE_MS) {
            g_dtc = fault;
        }
    } else {
        g_pending = 0;
        g_fault_ms = 0;
        if (g_dtc) {
            g_ok_ms += ECU_STEP_MS;
            if (g_ok_ms >= ECT_DEBOUNCE_MS) {
                g_dtc = 0;
                g_ok_ms = 0;
            }
        }
    }
}

int32_t ect_diag_dtc(void) {
    return g_dtc;
}
