#include "controller.h"

#include <thread>
// Functions depending on the hardware

bool Joint::hardware_step(uint8_t step_dir) {
    // pis to set are stored in this->step_pin and this->dir_pin
    // set dir pin according to step_dir
    // set step pin high
    // wait for min_pulse_width
    // set step pin low
    return true;
}



bool Joint::hardware_end_stop_read() {
    // In a real implementation this would be a digital read
    if (std::abs(this->current_angle - this->homing_direction * PI) < 0.1) {
        return true;
    }
    return false;
}


void Controller::step_target_fun(){
    while(1){
        this->step();
    }
}

void Controller::run_step_task(){
    std::thread step_thread(&Controller::step_target_fun, this);
    step_thread.detach();
}

void run_delay(uint32_t delay_ms) {
    std::this_thread::sleep_for(std::chrono::milliseconds(delay_ms));
}

uint64_t get_current_time_microseconds() {
    auto now = std::chrono::system_clock::now().time_since_epoch();
    return std::chrono::duration_cast<std::chrono::microseconds>(now).count();
}