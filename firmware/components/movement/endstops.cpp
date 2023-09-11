#include "movement.h"

#ifdef ESP_PLATFORM
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"

#endif
EndStop::EndStop(int8_t pin) { this->pin = pin; }

DummyEndStop::DummyEndStop(int8_t pin) : EndStop(pin) {}

DummyEndStop::~DummyEndStop() {}

void DummyEndStop::hardware_setup() {}

bool DummyEndStop::hardware_read_state() {
    uint64_t current_time = get_current_time_microseconds();

    if (last_time_read == 0) {
        last_time_read = current_time;
        return false;
    }
    uint64_t time_difference = current_time - last_time_read;

    if (time_difference > 2000000) {
        this->was_triggered = true;
        return true;
    } else {
        return false;
    }
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