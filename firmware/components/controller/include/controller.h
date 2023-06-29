#ifndef CONTROLLER_H

#define CONTROLLER_H
#include <map>
#include <queue>
#include <thread>
#include <vector>

#include "arm_client.h"
#include "config.h"
#include "messages.h"
#define PI 3.14159265358979323846

#ifdef ESP_PLATFORM
#include <rom/ets_sys.h>
#include <string.h>

#include "driver/gpio.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_system.h"
#include "esp_task_wdt.h"
#include "esp_timer.h"
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/task.h"
#include "lwip/err.h"
#include "lwip/sys.h"
#include "nvs_flash.h"
#else

#include "chrono"
#include "thread"

#endif

class Joint {
   private:
    float current_angle;
    float target_angle;
    int64_t current_steps;
    int64_t last_step_time;
    int32_t step_interval;

    int8_t step_pin;
    int8_t dir_pin;
    bool homing;

    // config
   public:
    bool homed;
    int8_t homing_direction;
    uint32_t steps_per_revolution_motor_axis;
    float convertion_rate_axis_joint;
    uint32_t steps_per_revolution;
    int32_t speed_steps_per_second;
    int32_t min_pulse_width = 1;
    float homing_offset;
    float epsilon = 0.0001;

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
    uint32_t steps_to_take(uint64_t current_time);
};

// typef to funtions that return void and take a Message *

class Controller {
   private:
    ArmClient arm_client;
    std::vector<Joint *> joints;
    std::queue<Message *> message_queue;
    typedef void (Controller::*message_op_handler_t)(Message *);
    uint64_t last_status_time;
    std::map<char, std::queue<Message *> *> message_queues;
    std::map<char, message_op_handler_t> message_op_handler_map;
    bool homed = false;

   public:
    Controller();
    ~Controller();
    void start();
    void stop();
    void step();
    bool recieve_message();
    void handle_messages();
    void run_step_task();
    void step_target_fun();
    bool hardware_setup();
    bool is_homed();

    void message_handler_status(Message *message);
    void message_handler_move(Message *message);
    void message_handler_config(Message *message);
};

void run_delay(uint32_t delay_ms);
uint64_t get_current_time_microseconds();
void task_add();
void task_feed();
void task_end();
#endif
