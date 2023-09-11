#ifndef TOOL_H

#define TOOL_H

#include <stdint.h>

#include "movement.h"


class Tool{

    MovementDriver *movement_driver = nullptr;


    public:
        Tool(int8_t pin);
        ~Tool();

        MovementDriver *get_movement_driver();

        float set_target_value(float target_value);
        float get_target_value();
        float get_current_value();

        bool at_target();

        void step();
};

#endif