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
    gpio_config_t io_conf;
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.mode = GPIO_MODE_INPUT;
    io_conf.pin_bit_mask = 1ULL << this->pin; // Assuming GPIO23
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
    gpio_config(&io_conf);
}

bool HallEffectSensor::hardware_read_state() {
    int state = gpio_get_level((gpio_num_t)this->pin); // Assuming GPIO23
    return state == 0;
}