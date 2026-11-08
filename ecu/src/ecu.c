#include "ecu.h"

#include <string.h>

#include "ecu_internal.h"

static EcuInputs g_in;
static EcuOutputs g_out;

void ecu_init(void) {
    memset(&g_in, 0, sizeof g_in);
    memset(&g_out, 0, sizeof g_out);
    idle_init();
    fuel_cut_init();
    ect_diag_init();
}

void ecu_set_inputs(const EcuInputs *in) {
    g_in = *in;
}

void ecu_step(void) {
    ect_diag_step(g_in.ect_sensor_mv);
    g_out.dtc = ect_diag_dtc();
    g_out.ect_used_c = g_out.dtc ? ECT_FAILSAFE_C : g_in.coolant_temp_c;

    g_out.target_idle_rpm = idle_target_rpm(g_out.ect_used_c);

    fuel_cut_step(g_in.engine_rpm, g_in.throttle_pct);
    g_out.fuel_cut = fuel_cut_active();

    g_out.gear = shift_gear(g_in.vehicle_speed_kmh, g_in.throttle_pct);
}

void ecu_get_outputs(EcuOutputs *out) {
    *out = g_out;
}
