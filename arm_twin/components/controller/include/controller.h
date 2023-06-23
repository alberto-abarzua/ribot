#ifndef CONTROLLER_H

#define CONTROLLER_H
#include <chrono>
#include <deque>
#include <map>
#include <thread>
#include <vector>

#include "arm_client.h"
#include "messages.h"
#define PI 3.14159265358979323846

class Joint {
   private:
    float current_angle;
    float target_angle;
    int8_t step_pin;
    int8_t dir_pin;
    int8_t homing_direction;
    uint32_t steps_per_revolution;
    int64_t current_steps;
    int32_t speed_steps_per_second;
    int64_t last_step_time;
    int32_t step_interval;
    float homing_offset;
    bool homing;
    bool homed;
    float epsilon = 0.0001;

   public:
    Joint(int8_t step_pin, int8_t dir_pin, int8_t homing_direction,
          uint32_t steps_per_revolution);
    ~Joint();

    void set_target_angle(float angle);
    float get_current_angle();
    float get_target_angle();
    bool at_target();
    bool step();
    bool home_joint();
    bool set_home();

    void update_current_angle();
    float steps_to_angle(int64_t steps);
    int64_t angle_to_steps(float angle);

    void set_speed_steps_per_second(uint32_t speed_steps_per_second);
    void set_speed_rad_per_second(float speed_rad_per_second);

    int32_t get_speed_steps_per_second();

    // Hardware dependant functions
    bool hardware_step(uint8_t step_dir);
    bool hardware_end_stop_read();
};

// typef to funtions that return void and take a Message *

class Controller {
   private:
    ArmClient arm_client;
    std::vector<Joint *> joints;
    std::deque<Message *> message_queue;
    typedef void (Controller::*message_op_handler_t)(Message *);
    uint64_t last_status_time;
    int32_t status_interval = 0.1 * 1000000;// 0.5 seconds

    std::map<char, message_op_handler_t> message_op_handler_map;

   public:
    Controller();
    ~Controller();
    void start();
    void stop();
    void send_status_message();
    void step();
    void recieve_message();
    void handle_messages();
    void message_handler_move(Message *message);
    void message_handler_status(Message *message);
    bool skip_message(Message *message);
    void print_status();
    void run_step_task();
    void step_target_fun();
};

void run_delay(uint32_t delay_ms);
uint64_t get_current_time_microseconds();

#endif
