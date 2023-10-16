#ifndef UTILS_H

#define UTILS_H
#define PI 3.14159265358979323846
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <cmath>
#include <iostream>

#include "config.h"

void run_delay(uint32_t delay_ms);
void run_delay_microseconds(uint32_t delay_us);
uint64_t get_current_time_microseconds();
void task_add();
void task_feed();
void task_end();

void wifi_init_sta();
void nvs_init();

void global_setup_hardware();

#endif
