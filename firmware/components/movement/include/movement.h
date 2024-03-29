#ifndef MOVEMENT_H
#define MOVEMENT_H

#include <stdint.h>

#include <cstdint>

#include "endstops.h"
#include "utils.h"

#ifdef ESP_PLATFORM
#include "driver/mcpwm_prelude.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#endif

class MovementDriver {
   protected:
    float epsilon = 0.1;
    int64_t current_steps = 0;
    float current_angle = 0;
    float target_angle = 0;
    float speed = 0.1;  // rad per second
    float prev_speed = 0.1;

    uint64_t last_step_time = 0;
    uint32_t step_interval = 0;
    uint32_t steps_per_revolution = 200;

    bool homed = false;
    int8_t homing_direction = 1;
    float homing_offset = 0;
    float homing_speed = 0.25;
    int8_t dir_inverted = 1;

    EndStop* end_stop = nullptr;

   public:
    void set_target_angle(float angle);
    void set_current_angle(float angle);
    float get_current_angle();
    float get_target_angle();
    float* get_current_angle_ptr();
    bool at_target();
    void set_speed(float speed);
    void update_speed();
    float get_speed();
    int64_t angle_to_steps(float angle);
    float steps_to_angle(int64_t steps);
    int8_t get_dir_inverted();
    void set_dir_inverted(int8_t dir_inverted);

    void set_steps_per_revolution(uint32_t steps_per_revolution);
    uint32_t get_steps_per_revolution();
    uint32_t steps_to_take(uint64_t current_time);
    bool is_homed();
    bool home();
    void set_homing_direction(int8_t homing_direction);
    void set_homing_offset(float homing_offset);
    int8_t get_homing_direction();
    float get_homing_offset();
    bool step();
    void print_state();

    void register_end_stop(EndStop* end_stop);
    void set_home();
    virtual ~MovementDriver() = default;
    virtual void hardware_setup() = 0;
    virtual void hardware_step(int8_t step_dir) = 0;
};

class Stepper : public MovementDriver {
   private:
    int8_t step_pin;
    int8_t dir_pin;

   public:
    Stepper(int8_t step_pin, int8_t dir_pin);
    ~Stepper();
    void hardware_setup() override;
    void hardware_step(int8_t step_dir) override;
};

class Servo : public MovementDriver {
   private:
    int8_t pin;
#ifdef ESP_PLATFORM
    mcpwm_cmpr_handle_t comparator = NULL;
#endif
   public:
    Servo(int8_t pin);
    ~Servo();

    void hardware_setup();

    void hardware_step(int8_t step_dir);
    uint32_t angle_to_compare(int32_t angle);
    bool home();
};

#endif
