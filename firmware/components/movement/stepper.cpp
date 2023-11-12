#include "movement.h"
#include "utils.h"

#ifdef ESP_PLATFORM

#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"

#endif

#ifdef ESP_PLATFORM

void Stepper::hardware_setup() {
    gpio_config_t io_conf;
    io_conf.pin_bit_mask = (1ULL << step_pin) | (1ULL << dir_pin);
    io_conf.mode = GPIO_MODE_OUTPUT;
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    io_conf.pull_up_en = GPIO_PULLUP_DISABLE;

    gpio_config(&io_conf);
}

void Stepper::hardware_step(int8_t step_dir) {
    int8_t dir_val = step_dir > 0 ? 1 : 0;
    gpio_set_level((gpio_num_t)dir_pin, dir_val);
    run_delay_microseconds(10);

    gpio_set_level((gpio_num_t)step_pin, 1);
    run_delay_microseconds(5);
    gpio_set_level((gpio_num_t)step_pin, 0);
    run_delay_microseconds(5);
}

#else

void Stepper::hardware_setup() {}

void Stepper::hardware_step(int8_t) {}

#endif

Stepper::Stepper(int8_t step_pin, int8_t dir_pin) {
    this->step_pin = step_pin;
    this->dir_pin = dir_pin;
    this->set_speed(0.5);
}

Stepper::~Stepper() {
    if (this->end_stop != nullptr) {
        delete this->end_stop;
    }
}
