#include <iostream>

#include "controller.h"



#ifdef ESP_PLATFORM
extern "C" void app_main() {
    Controller controller = Controller();
    controller.start();
}
#else
int main() {
    Controller controller = Controller();
    controller.start();
    return 0;
}
#endif