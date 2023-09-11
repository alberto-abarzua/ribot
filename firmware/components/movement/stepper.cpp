#include "movement.h"

#ifdef ESP_PLATFORM

#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"

#endif

#ifdef ESP_PLATFORM

void Stepper::hardware_setup() {
    // TODO: SETUP PWM PINS
}

void Stepper::hardware_step(int8_t) {
    // TODO: use pwm to set the angle
}

#else

void Stepper::hardware_setup() {}

void Stepper::hardware_step(int8_t) {}

#endif

Stepper::Stepper(int8_t step_pin, int8_t dir_pin) {
    this->step_pin = step_pin;
    this->dir_pin = dir_pin;
}

Stepper::~Stepper() {
    if (this->end_stop != nullptr) {
        delete this->end_stop;
    }
}
