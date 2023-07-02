#include <iostream>

#include "controller.h"

#ifdef ESP_PLATFORM
extern "C" void app_main() {
    Controller controller = Controller();
    controller.start();
}
#else
#include <signal.h>  // Add this line at the top of your file

Controller* global_controller = nullptr;
void handleSIGINT(int) {
    std::cout << "Caught SIGINT" << std::endl;
    if (global_controller) {
        global_controller->stop();
    }
}

int main() {
    Controller controller = Controller();
    global_controller = &controller;

    // Register the signal handler
    signal(SIGINT, handleSIGINT);

    controller.start();

    return 0;
}
#endif