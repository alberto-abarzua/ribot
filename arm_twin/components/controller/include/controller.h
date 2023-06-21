#ifndef CONTROLLER_H

#define CONTROLLER_H
#include "arm_client.h"
#include "messages.h"
#include <chrono>
#include <thread>
class Controller {
   private:
    ArmClient arm_client;

   public:
    Controller();
    ~Controller();
    void start();
    void stop();

};

#endif
