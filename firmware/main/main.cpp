#include <iostream>

#include "controller.h"

Controller* global_controller = nullptr;

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
    Controller controller = Controller();
    global_controller = &controller;

    // Register the signal handler
    while (true) {
        controller.start();  // if controller is stopped, start it
        run_delay(500);
    }
    return 0;
}

#ifdef ESP_PLATFORM
extern "C" void app_main() { run_controller(); }
#else

int main() { 
    signal(SIGINT, handleSIGINT);

    run_controller(); }
#endif