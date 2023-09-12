#ifndef JOINT_H

#define JOINT_H

#include <stdint.h>

#include "movement.h"

class Joint {
   private:
    MovementDriver* movement_driver = nullptr;
    EndStop* end_stop = nullptr;
    uint32_t steps_per_revolution_motor_axis = 200;
    uint32_t conversion_rate_axis_joint = 1;

   public:
    Joint();

    ~Joint();

    MovementDriver* get_movement_driver();
    void set_movement_driver(MovementDriver* movement_driver);

    void register_end_stop(EndStop* end_stop);
    EndStop* get_end_stop();

    float set_target_angle(float target_angle);
    float get_target_angle();
    float get_current_angle();

    void set_steps_per_revolution_motor_axis(
        uint32_t steps_per_revolution_motor_axis);

    void set_conversion_rate_axis_joint(uint32_t conversion_rate_axis_joint);

    uint32_t get_steps_per_revolution_motor_axis();
    uint32_t get_conversion_rate_axis_joint();

    void update_steps_per_revolution_driver();

    bool at_target();

    bool is_homed();
    bool home_joint();
    bool set_home();

    void step();
};

#endif