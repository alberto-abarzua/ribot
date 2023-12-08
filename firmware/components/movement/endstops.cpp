#include "endstops.h"

#include <cstring>

#ifdef ESP_PLATFORM
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"

#endif

// ================
// EndStop
// ================

EndStop::EndStop(int8_t pin) { this->pin = pin; }

EndStop::EndStop(int8_t pin, const char* name) {
    this->pin = pin;
    this->name = new char[strlen(name) + 1];
    strncpy(this->name, name, strlen(name) + 1);
}

EndStop::~EndStop() {
    if (this->name != nullptr) {
        delete[] this->name;
    }
}

void EndStop::print_state() {
    std::cout << "-----------------------------------------" << std::endl;
    std::cout << "EndStop: " << std::endl;
    std::cout << "\t Pin: " << this->pin << std::endl;
    std::cout << "-----------------------------------------" << std::endl;
}

// ================
// DummyEndStop
// ================
DummyEndStop::DummyEndStop(int8_t pin, float* current_angle)
    : EndStop(pin, "dummyEndstop") {
    this->current_angle = current_angle;
}

DummyEndStop::~DummyEndStop() {}

void DummyEndStop::hardware_setup() {}

bool DummyEndStop::hardware_read_state() {
    if (this->current_angle == nullptr) {
        return false;
    }

    float current_angle_value = *this->current_angle;
    // pinMode(this->pin, INPUT_PULLUP);
    if (current_angle_value >= (float)(PI / 4.0)) {
        return true;
    }
    return false;
    // pinMode(this->pin, INPUT_PULLUP);
}

// ================
// HallEffectSensor
// ================

HallEffectSensor::HallEffectSensor(int8_t pin) : EndStop(pin, "HallSensor") {}

HallEffectSensor::~HallEffectSensor() {}

#ifdef ESP_PLATFORM

void HallEffectSensor::hardware_setup() {
    gpio_config_t io_conf;
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.mode = GPIO_MODE_INPUT;
    io_conf.pin_bit_mask = 1ULL << this->pin;  // Assuming GPIO23
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
    gpio_config(&io_conf);
}

bool HallEffectSensor::hardware_read_state() {
    int state = gpio_get_level((gpio_num_t)this->pin);  // Assuming GPIO23
    return state == 0;
}

#else

void HallEffectSensor::hardware_setup() {}

bool HallEffectSensor::hardware_read_state() { return true; }

#endif

// ================
// NoneEndStop
// ================

NoneEndStop::NoneEndStop() : EndStop(-1, "noneEndstop") {}

NoneEndStop::~NoneEndStop() {}

void NoneEndStop::hardware_setup() {}

bool NoneEndStop::hardware_read_state() { return true; }
