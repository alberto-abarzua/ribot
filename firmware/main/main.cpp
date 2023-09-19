#include <iostream>

#include "controller.h"
#include "movement.h"
Controller* global_controller = nullptr;

#if defined(ESP_PLATFORM)

#include "esp_system.h"

#pragma message("Current platform: ESP32")
#else
#pragma message("Current platform: Linux")
#endif

#ifndef ESP_PLATFORM
#include <signal.h>

void handleSIGINT(int) {
    std::cout << "Caught SIGINT" << std::endl;
    if (global_controller) {
        global_controller->stop();
    }
}
#endif

int run_test_servo() {
    // global_setup_hardware();
    Servo* servo = new Servo(26);
    servo->hardware_setup();
    servo->set_target_angle(1.5);
    servo->set_speed(0.8);
    task_add();
    bool changed_dir = false;
    while (true) {
        task_feed();
        servo->step();
        if (servo->get_current_angle() > 1.4) {
            // std::cout<<"current_angle, target_angle:
            // "<<servo->get_current_angle()<<",
            // "<<servo->get_target_angle()<<std::endl;
            if (!changed_dir) {
                servo->set_target_angle(-1.5);
                changed_dir = true;
            }
        } else if (servo->get_current_angle() < -1.4) {
            if (changed_dir) {
                servo->set_target_angle(1.5);
                changed_dir = false;
            }
        }
        task_feed();
        std::cout << "current_angle, target_angle: "
                  << servo->get_current_angle() << ", "
                  << servo->get_target_angle() << std::endl;
        run_delay(10);
    }
    task_end();
}

int run_controller(bool loop) {
    do {
        Controller* controller = new Controller();
        global_controller = controller;
        bool exited = controller->start();
        delete controller;
        global_controller = nullptr;
        if (exited) {
            break;
        }
    } while (loop);

    return 0;
}

#ifdef ESP_PLATFORM
extern "C" void app_main() {
    run_test_servo();
    // run_controller(false);
    // esp_restart();
}
#else

int main() {
    signal(SIGINT, handleSIGINT);

    run_controller(true);
}
#endif