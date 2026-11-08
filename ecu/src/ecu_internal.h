#ifndef ECU_INTERNAL_H
#define ECU_INTERNAL_H

#include <stdint.h>

void idle_init(void);
int32_t idle_target_rpm(int32_t ect_c);

void fuel_cut_init(void);
void fuel_cut_step(int32_t rpm, int32_t throttle_pct);
int32_t fuel_cut_active(void);

void ect_diag_init(void);
void ect_diag_step(int32_t sensor_mv);
int32_t ect_diag_dtc(void);

int32_t shift_gear(int32_t speed_kmh, int32_t throttle_pct);

#endif
