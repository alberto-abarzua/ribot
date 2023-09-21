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
    run_controller(false);
    esp_restart();
}
#else

int main() {
    signal(SIGINT, handleSIGINT);

    run_controller(true);
}
#endif