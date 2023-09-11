#ifndef CONTROLLER_H

#define CONTROLLER_H

#include <algorithm>
#include <map>
#include <queue>

#include "arm_client.h"
#include "joint.h"
#include "messages.h"
#include "tool.h"
#ifndef ESP_PLATFORM

#include <thread>
#endif

#pragma pack(push, 1)
typedef struct arm_status {
    float joint_angles[6];
    float tool_value;
    float move_queue_size;
    float homed;
    float code;

} arm_status_t;
#pragma pack(pop)
class Controller {
   private:
    ArmClient arm_client;

    std::vector<Joint *> joints;
    Tool * tool = nullptr;
    std::queue<Message *> message_queue;

    typedef void (Controller::*message_op_handler_t)(Message *);

    std::map<MessageOp, std::queue<Message *> *> message_queues;
    std::map<MessageOp, message_op_handler_t> message_op_handler_map;

    bool homed = false;
    bool stop_flag = false;

#ifndef ESP_PLATFORM
    std::thread *step_thread = nullptr;
#endif

   public:
    Controller();
    ~Controller();
    void start();
    void stop();
    void stop(int signum);
    void step();
    bool recieve_message();
    void handle_messages();
    void run_step_task();
    void stop_step_task();
    void step_target_fun();

    bool is_homed();
    Tool * get_tool();
    void set_tool(Tool * tool);
    void message_handler_status(Message *message);
    void message_handler_move(Message *message);
    void message_handler_config(Message *message);
    bool hardware_setup();
};




#endif
