#include "movement.h"

#include "utils.h"

void MovementDriver::set_target_angle(float angle) {
    this->last_step_time = get_current_time_microseconds();
    this->target_angle = angle;
}

void MovementDriver::set_current_angle(float angle) {
    this->current_angle = angle;
    this->current_steps = this->angle_to_steps(angle);
}

float MovementDriver::get_current_angle() { return this->current_angle; }

float MovementDriver::get_target_angle() { return this->target_angle; }

void MovementDriver::set_steps_per_revolution(uint32_t steps_per_revolution) {
    this->steps_per_revolution = steps_per_revolution;
    this->epsilon = this->steps_to_angle(3);
    this->update_speed();
}

uint32_t MovementDriver::get_steps_per_revolution() {
    return this->steps_per_revolution;
}

bool MovementDriver::at_target() {
    float diff = std::abs(this->target_angle - this->current_angle);
    return diff < this->epsilon;
}

void MovementDriver::set_speed(float speed) {
    int64_t steps_per_second =
        std::max((int64_t)1, this->angle_to_steps(speed));
    this->speed = speed;
    this->step_interval = std::abs(1000000.0 / (float)steps_per_second);
    this->homing_speed = speed * 0.6;
}

void MovementDriver::update_speed() {
    float speed = this->speed;
    int64_t steps_per_second =
        std::max((int64_t)1, this->angle_to_steps(speed));
    this->step_interval = std::abs(1000000.0 / (float)steps_per_second);
}

void MovementDriver::print_state() {
    std::cout << "epsilon: " << this->epsilon << std::endl;
    std::cout << "current_steps: " << this->current_steps << std::endl;
    std::cout << "current_angle: " << this->current_angle << std::endl;
    std::cout << "target_angle: " << this->target_angle << std::endl;
    std::cout << "speed: " << this->speed << std::endl;
    std::cout << "last_step_time: " << this->last_step_time << std::endl;
    std::cout << "step_interval: " << this->step_interval << std::endl;
    std::cout << "steps_per_revolution: " << this->steps_per_revolution
              << std::endl;
    std::cout << "homed: " << this->homed << std::endl;
    std::cout << "homing_direction: "
              << static_cast<int>(this->homing_direction) << std::endl;
    std::cout << "homing_offset: " << this->homing_offset << std::endl;
    std::cout << "end_stop: " << this->end_stop << std::endl;
}

float MovementDriver::get_speed() { return this->speed; }

int64_t MovementDriver::angle_to_steps(float angle) {
    return static_cast<int64_t>(angle / (2 * PI) * this->steps_per_revolution);
}

bool MovementDriver::is_homed() { return this->homed; }

bool MovementDriver::home() {
    this->prev_speed = this->speed;
    this->set_speed(this->homing_speed);
    int8_t homing_dir = this->homing_direction;
    float target_angle = homing_dir * 2 * PI;
    this->set_target_angle(target_angle);
    this->homed = false;
    return this->is_homed();
}
void MovementDriver::set_homing_direction(int8_t homing_direction) {
    this->homing_direction = homing_direction;
}

void MovementDriver::set_homing_offset(float homing_offset) {
    this->homing_offset = homing_offset;
}

int8_t MovementDriver::get_homing_direction() { return this->homing_direction; }

float MovementDriver::get_homing_offset() { return this->homing_offset; }

uint32_t MovementDriver::steps_to_take(uint64_t current_time) {
    if (this->at_target()) {
        return 0;
    }
    uint64_t dif = current_time - this->last_step_time;
    uint64_t steps = std::floor(dif / this->step_interval);
    uint64_t steps_to_target =
        std::abs(this->angle_to_steps(this->target_angle) -
                 this->angle_to_steps(this->current_angle));
    return std::min(steps, steps_to_target);
}
bool MovementDriver::step() {
    uint64_t current_time = get_current_time_microseconds();
    uint32_t steps_to_take = this->steps_to_take(current_time);

    if (steps_to_take > 0) {
        std::cout << "steps_to_take: " << steps_to_take << std::endl;
        int8_t step_dir = this->target_angle > this->current_angle ? 1 : -1;

        for (uint16_t i = 0; i < steps_to_take; i++) {
            this->current_steps += step_dir;

            this->hardware_step(step_dir > 0 ? 1 : 0);

            if (!this->homed && this->end_stop != nullptr) {
                this->current_angle = this->steps_to_angle(this->current_steps);
                if (this->end_stop->hardware_read_state()) {
                    this->set_home();
                    this->last_step_time = get_current_time_microseconds();
                    return false;
                }
                run_delay_microseconds(50);
            } else {
                run_delay_microseconds(100);
            }
        }

        this->last_step_time = get_current_time_microseconds();
        this->current_angle = this->steps_to_angle(this->current_steps);
        return true;
    }
    return false;
}

void MovementDriver::register_end_stop(EndStop* end_stop) {
    this->end_stop = end_stop;
}

void MovementDriver::set_home() {
    this->homed = true;
    this->set_current_angle(this->homing_offset);
    this->set_target_angle(0.0);
    this->set_speed(this->prev_speed);
}

float MovementDriver::steps_to_angle(int64_t steps) {
    return static_cast<float>(steps) /
           static_cast<float>(this->steps_per_revolution) * 2.0 * PI;
}

float* MovementDriver::get_current_angle_ptr() { return &this->current_angle; }
