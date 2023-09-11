#include "tool.h"


Tool::Tool(int8_t pin) {
    this->movement_driver = new Servo(pin);
    

}

Tool::~Tool() {
    delete this->movement_driver;
}



MovementDriver* Tool::get_movement_driver() {
    return this->movement_driver;
}

float Tool::set_target_value(float target_value) {
    this->movement_driver->set_target_angle(target_value);
    return this->movement_driver->get_target_angle();
}

float Tool::get_target_value() {
    return this->movement_driver->get_target_angle();
}

float Tool::get_current_value() {
    return this->movement_driver->get_current_angle();
}

bool Tool::at_target() {
    return this->movement_driver->at_target();
}

void Tool::step() {
    this->movement_driver->step();
}




