#include "movement.h"

#ifdef ESP_PLATFORM
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"

#endif
EndStop::EndStop(int8_t pin) { this->pin = pin; }

DummyEndStop::DummyEndStop(int8_t pin, float* current_angle) : EndStop(pin) {
    this->current_angle = current_angle;
}

DummyEndStop::~DummyEndStop() {}

void DummyEndStop::hardware_setup() {}

bool DummyEndStop::hardware_read_state() {
    if (this->current_angle == nullptr) {
        return false;
    }

    float current_angle_value = *this->current_angle;
    if (current_angle_value >= (float)(PI / 4.0)) {
        return true;
    }
    return false;
}

HallEffectSensor::HallEffectSensor(int8_t pin) : EndStop(pin) {}

HallEffectSensor::~HallEffectSensor() {}

void HallEffectSensor::hardware_setup() {
    // pinMode(this->pin, INPUT_PULLUP);
}

bool HallEffectSensor::hardware_read_state() {
    // int8_t state = digitalRead(this->pin);
    // if (state != this->last_state) {
    //     this->last_state = state;
    //     return true;
    // }
    // return false;
    return true;
}