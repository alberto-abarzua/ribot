#include "movement.h"

#ifdef ESP_PLATFORM
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"

#endif

#ifdef ESP_PLATFORM

void Servo::hardware_setup() {
    //
}

void Servo::hardware_step(int8_t step_dir) {
    // float target_angle_in_rads = this->get_target_angle();
    // TODO: use pwm to set the angle
}

#else

void Servo::hardware_setup() {}

void Servo::hardware_step(int8_t) {}

#endif

Servo::Servo(int8_t pin) : MovementDriver() {
    this->pin = pin;

    this->homed = true;
}

Servo::~Servo() {
    if (this->end_stop != nullptr) {
        delete this->end_stop;
    }
}
