#include <iostream>

#include "controller.h"

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

int run_controller(bool loop) {
    do {
        Controller* controller = new Controller();
        global_controller = controller;
        controller->start();  // if controller is stopped, start it
        controller->stop();   // if controller is running, stop it
        delete controller;  // Delete the controller object to release resources
        global_controller = nullptr;
    } while (loop);

    return 0;
}

#ifdef ESP_PLATFORM
extern "C" void app_main() {
    run_controller(false);
    esp_restart();
}
#else

int main() {
    signal(SIGINT, handleSIGINT);

    run_controller(false);
}
#endif