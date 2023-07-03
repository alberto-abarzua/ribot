#include <iostream>

#include "controller.h"

Controller* global_controller = nullptr;

#if defined(ESP_PLATFORM)
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

int run_controller() {
    

    // Register the signal handler
    while (true) {
        Controller controller = Controller();
        global_controller = &controller;
        controller.start();  // if controller is stopped, start it
        controller.stop();   // if controller is running, stop it
        global_controller = nullptr;
    }
    return 0;
}

#ifdef ESP_PLATFORM
extern "C" void app_main() { run_controller(); }
#else

int main() {
    signal(SIGINT, handleSIGINT);

    run_controller();
}
#endif