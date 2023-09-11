#include "movement.h"

#include "utils.h"

void MovementDriver::set_target_angle(float angle) {
    this->last_step_time = get_current_time_microseconds();
    this->target_angle = angle;
}

void MovementDriver::set_current_angle(float angle) {
    this->current_angle = angle;
    this->target_angle = angle;
    this->current_steps = this->angle_to_steps(angle);
}

float MovementDriver::get_current_angle() { return this->current_angle; }

float MovementDriver::get_target_angle() { return this->target_angle; }

void MovementDriver::set_steps_per_revolution(uint32_t steps_per_revolution) {
    this->steps_per_revolution = steps_per_revolution;
}

uint32_t MovementDriver::get_steps_per_revolution() {
    return this->steps_per_revolution;
}

bool MovementDriver::at_target() {
    return (this->target_angle - this->current_angle) < this->epsilon;
}

void MovementDriver::set_speed(float speed) {
    int64_t steps_per_second = this->angle_to_steps(speed);
    this->speed = speed;
    this->step_interval = std::abs(1000000 / steps_per_second);
}

float MovementDriver::get_speed() { return this->speed; }

int64_t MovementDriver::angle_to_steps(float angle) {
    return static_cast<int64_t>(angle / (2 * PI) * this->steps_per_revolution);
}

uint32_t MovementDriver::steps_to_take(uint64_t current_time) {
    uint64_t dif = current_time - this->last_step_time;
    uint64_t steps = std::floor(dif / this->step_interval);
    uint64_t steps_to_target =
        std::abs(this->angle_to_steps(this->target_angle) -
                 this->angle_to_steps(this->current_angle));

    
    return std::min(steps, steps_to_target);
}

bool MovementDriver::is_homed() { return this->homed; }

void MovementDriver::set_homing_direction(int8_t homing_direction) {
    this->homing_direction = homing_direction;
}

void MovementDriver::set_homing_offset(float homing_offset) {
    this->homing_offset = homing_offset;
}

int8_t MovementDriver::get_homing_direction() { return this->homing_direction; }

float MovementDriver::get_homing_offset() { return this->homing_offset; }

bool MovementDriver::step() {
    if (this->at_target()) {
        return false;
    }
    
    uint64_t current_time = get_current_time_microseconds();

    uint32_t steps_to_take = this->steps_to_take(current_time);
    if (steps_to_take > 0) {
        int8_t step_dir = this->target_angle > this->current_angle ? 1 : -1;
        for (uint16_t i = 0; i < steps_to_take; i++) {
            this->hardware_step(step_dir > 0 ? 1 : 0);
            this->current_steps += step_dir;
            this->current_angle = this->steps_to_angle(this->current_steps);
            this->last_step_time = get_current_time_microseconds();
            if (!this->homed && this->end_stop != nullptr) {
                if (this->end_stop->hardware_read_state()) {
                    this->set_home();
                    return false;
                }
            }
        }
        return true;
    }
    return false;
}

void MovementDriver::register_end_stop(EndStop* end_stop) {
    this->end_stop = end_stop;
}

void MovementDriver::set_home() {
    this->homed = true;
    this->current_angle = this->homing_offset;
    this->target_angle = 0;
    this->current_steps = this->angle_to_steps(this->current_angle);
}

float MovementDriver::steps_to_angle(int64_t steps) {
    return static_cast<float>(steps) /
           static_cast<float>(this->steps_per_revolution) * 2.0 * PI;
}