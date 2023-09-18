#include "joint.h"

Joint::Joint() {
    this->movement_driver = nullptr;
    this->end_stop = nullptr;
}

Joint::~Joint() {
    if (this->movement_driver != nullptr) {
        delete this->movement_driver;
        this->movement_driver = nullptr;
    }
}

MovementDriver* Joint::get_movement_driver() { return this->movement_driver; }

void Joint::set_movement_driver(MovementDriver* movement_driver) {
    this->movement_driver = movement_driver;
}

float Joint::set_target_angle(float target_angle) {
    this->movement_driver->set_target_angle(target_angle);
    return this->movement_driver->get_target_angle();
}

float Joint::get_target_angle() {
    return this->movement_driver->get_target_angle();
}

bool Joint::at_target() { return this->movement_driver->at_target(); }

bool Joint::is_homed() { return this->movement_driver->is_homed(); }

bool Joint::home_joint() {
    this->movement_driver->home();
    return this->movement_driver->is_homed();
}

bool Joint::set_home() {
    this->movement_driver->set_home();
    return this->movement_driver->is_homed();
}

float Joint::get_current_angle() {
    return this->movement_driver->get_current_angle();
}

void Joint::register_end_stop(EndStop* end_stop) {
    this->end_stop = end_stop;
    this->movement_driver->register_end_stop(end_stop);
}

EndStop* Joint::get_end_stop() { return this->end_stop; }

void Joint::step() { this->movement_driver->step(); }

void Joint::set_steps_per_revolution_motor_axis(
    uint32_t steps_per_revolution_motor_axis) {
    this->steps_per_revolution_motor_axis = steps_per_revolution_motor_axis;
    this->update_steps_per_revolution_driver();
}

void Joint::set_conversion_rate_axis_joint(
    uint32_t conversion_rate_axis_joint) {
    this->conversion_rate_axis_joint = conversion_rate_axis_joint;
    this->update_steps_per_revolution_driver();
}

void Joint::update_steps_per_revolution_driver() {
    this->movement_driver->set_steps_per_revolution(
        this->steps_per_revolution_motor_axis *
        this->conversion_rate_axis_joint);
}

uint32_t Joint::get_steps_per_revolution_motor_axis() {
    return this->steps_per_revolution_motor_axis;
}

uint32_t Joint::get_conversion_rate_axis_joint() {
    return this->conversion_rate_axis_joint;
}
