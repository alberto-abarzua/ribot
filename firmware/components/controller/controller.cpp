#include "controller.h"

#include "movement.h"
#include "utils.h"

#ifdef ESP_PLATFORM
#include <rom/ets_sys.h>

#include "esp_event.h"
#include "esp_system.h"
#include "esp_task_wdt.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/task.h"
#else

#include "chrono"
#include "thread"

#endif

/**
 * -----------------------------------------------------------------
 * ------------------------ CONTROLLER CLASS ---------------------------
 * -----------------------------------------------------------------
 */

Controller::Controller() {
    this->arm_client = ArmClient();
    this->joints = std::vector<Joint *>();

    this->joints.push_back(new Joint());
    this->joints.push_back(new Joint());
    this->joints.push_back(new Joint());
    this->joints.push_back(new Joint());
    this->joints.push_back(new Joint());
    this->joints.push_back(new Joint());

    this->tool = new Tool(0);

    this->tool->get_movement_driver()->set_speed(1);

    for (uint8_t i = 0; i < this->joints.size(); i++) {
        this->joints[i]->set_movement_driver(new Stepper(0, 0));
        MovementDriver *movement_driver =
            this->joints[i]->get_movement_driver();
        movement_driver->set_homing_direction(1);
        movement_driver->set_speed(0.5);
        movement_driver->set_homing_offset(0);

        this->joints[i]->set_steps_per_revolution_motor_axis(800);
        this->joints[i]->set_conversion_rate_axis_joint(1);
#ifdef ESP_PLATFORM
        this->joints[i]->register_end_stop(new HallEffectSensor(0));
#else

        this->joints[i]->register_end_stop(
            new DummyEndStop(0, movement_driver->get_current_angle_ptr()));

#endif
    }
    // Message handlers
    this->message_op_handler_map[MessageOp::MOVE] =
        &Controller::message_handler_move;
    this->message_op_handler_map[MessageOp::STATUS] =
        &Controller::message_handler_status;
    this->message_op_handler_map[MessageOp::CONFIG] =
        &Controller::message_handler_config;

    // Message qs
    for (auto const &[key, val] : this->message_op_handler_map) {
        this->message_queues[key] = new std::queue<Message *>();
    }
}

Controller::~Controller() {
    this->arm_client.stop();
    // delete queues
    if (!this->stop_flag) {
        this->stop();
    }
    for (auto const &[key, val] : this->message_queues) {
        if (val == nullptr) {
            continue;
        }
        std::queue<Message *> *message_queue = val;
        while (message_queue->size() > 0) {
            Message *msg = message_queue->front();
            delete msg;
            message_queue->pop();
        }
        delete message_queue;
    }

    for (uint8_t i = 0; i < this->joints.size(); i++) {
        delete this->joints[i];
        this->joints[i] = nullptr;
    }
    delete this->tool;
}

bool Controller::recieve_message() {
    Message *msg;
    ArmClientCode ret = this->arm_client.receive_message(&msg);
    if (ret != ArmClientCode::SUCCESS) {
        return false;
    }
    MessageOp op = msg->get_op();
    if (this->message_queues.find(op) == this->message_queues.end()) {
        return false;
    }
    std::queue<Message *> *message_queue = this->message_queues[op];
    message_queue->push(msg);
    return true;
}

bool Controller::is_homed() {
    if (this->homed) {
        return true;
    }

    bool all_homed = true;
    for (uint8_t i = 0; i < this->joints.size(); i++) {
        all_homed &= this->joints[i]->is_homed();
    }
    this->homed = all_homed;
    return all_homed;
}

void Controller::stop() {
    this->stop_flag = true;
    this->arm_client.stop();
    this->stop_step_task();
}

Tool *Controller::get_tool() { return this->tool; }

void Controller::set_tool(Tool *tool) { this->tool = tool; }

void Controller::stop(int signum) {
    std::cout << "Stopping controller " << signum << std::endl;
    this->stop();
}

void Controller::step() {
    for (uint8_t i = 0; i < this->joints.size(); i++) {
        this->joints[i]->step();
    }
    this->tool->step();
}

bool Controller::start() {
    run_delay(1000);
    std::cout << "Starting controller" << std::endl;
    this->hardware_setup();
    std::cout << "Hardware setup complete\n";
    ArmClientCode succesful_setup = this->arm_client.setup();
    std::cout << "Starting Arm Client setup\n";

    if (succesful_setup != ArmClientCode::SUCCESS) {
        std::cout << "Failed to setup arm client, retrying in 3 seconds"
                  << std::endl;
        run_delay(2000);
        return false;
    }
    this->run_step_task();

    std::cout << "Connected to the server" << std::endl;
    task_add();
    uint64_t last_message_time = get_current_time_microseconds();
    while (true) {
        task_feed();
        bool message_received = this->recieve_message();
        if (message_received) {
            last_message_time = get_current_time_microseconds();
        }
        if (get_current_time_microseconds() - last_message_time > 2 * 1000000) {
            std::cout << "No message in 5 seconds, stopping controller"
                      << std::endl;
            break;
        }
        task_feed();
        this->handle_messages();
        // print movequeue size
        run_delay(10);
    }
    task_end();
    return true;
}

/**
 * ----------------------------------------
 * ---------- Message Handlers ------
 * ----------------------------------------
 */
void Controller::handle_messages() {
    for (auto const &[key, val] : this->message_queues) {
        std::queue<Message *> *message_queue = val;
        if (message_queue->size() > 0) {
            Message *msg = message_queue->front();
            MessageOp op = msg->get_op();
            Controller::message_op_handler_t handler =
                this->message_op_handler_map[op];
            (this->*handler)(msg);
            if (msg->is_complete()) {
                message_queue->pop();
                delete msg;
            }
        }
    }
}

void Controller::message_handler_move(Message *message) {
    int32_t code = message->get_code();
    int32_t num_args = message->get_num_args();
    float *args = message->get_args();
    bool called = message->was_called();
    switch (code) {
        case 1: {
            if (!called) {
                for (int i = 0; i < num_args; i++) {
                    this->joints[i]->set_target_angle(args[i]);
                }
                message->set_called(true);
            } else {
                bool all_at_target = true;
                for (int i = 0; i < num_args; i++) {
                    all_at_target &= this->joints[i]->at_target();
                    if (!all_at_target) {
                        break;
                    }
                }

                if (all_at_target) {
                    message->set_complete(true);
                }
            }
        } break;
        case 3: {  // home all joints
            if (!called) {
                for (uint8_t i = 0; i < this->joints.size(); i++) {
                    this->joints[i]->home_joint();
                }
                message->set_called(true);
                this->homed = false;
            } else {
                bool all_homed = true;
                for (int i = 0; i < num_args; i++) {
                    all_homed &= this->joints[i]->is_homed();
                }
                if (all_homed) {
                    message->set_complete(true);
                }
            }

        } break;
        case 5: {  // home joint
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            if (!called) {
                this->joints[joint_idx]->home_joint();
                message->set_called(true);
                this->homed = false;

            } else {
                if (this->joints[joint_idx]->is_homed()) {
                    message->set_complete(true);
                }
            }

        } break;
        case 7: {  // set tool value
            MovementDriver *tool_driver = this->tool->get_movement_driver();
            if (!called) {
                tool_driver->set_target_angle(args[0]);
                message->set_called(true);

            } else {
                if (tool_driver->at_target()) {
                    message->set_complete(true);
                }
            }
        } break;
        default:
            break;
    }
}

void Controller::message_handler_status(Message *message) {
    int32_t code = message->get_code();
    switch (code) {
        case 0: {
            // angles + move_queue_size + homed
            arm_status_t *status = (arm_status_t *)malloc(sizeof(arm_status_t));

            status->tool_value =
                this->tool->get_movement_driver()->get_current_angle();
            status->code = 0;
            status->homed = this->is_homed() ? 1 : 0;
            status->move_queue_size =
                this->message_queues[MessageOp::MOVE]->size();
            for (uint8_t i = 0; i < this->joints.size(); i++) {
                status->joint_angles[i] = this->joints[i]->get_current_angle();
                // print driver read
                this->joints[i]->get_end_stop()->hardware_read_state();
            }
            int32_t num_args = sizeof(arm_status_t) / sizeof(float);

            Message *status_message =
                new Message(MessageOp::STATUS, 1, num_args,
                            reinterpret_cast<float *>(status));

            this->arm_client.send_message(status_message);
            message->set_complete(true);
            message->set_called(true);
            delete status_message;

        }

        break;
        case 3: {
            Message *status_message =
                new Message(MessageOp::STATUS, 4, 0, nullptr);
            this->arm_client.send_message(status_message);
            delete status_message;

        } break;

        case 5: {  // stop all moves
            std::queue<Message *> *move_queue =
                this->message_queues[MessageOp::MOVE];

            while (move_queue->size() > 0) {
                Message *msg = move_queue->front();
                msg->set_complete(true);
                msg->set_called(true);
                move_queue->pop();
                delete msg;
            }

            for (uint8_t i = 0; i < this->joints.size(); i++) {
                float current_angle = this->joints[i]->get_current_angle();
                this->joints[i]->set_target_angle(current_angle);
            }

            Message *status_message =
                new Message(MessageOp::STATUS, 6, 0, nullptr);

            this->arm_client.send_message(status_message);

        } break;

        default:
            break;
    }

    message->set_complete(true);
    message->set_called(true);
}

void Controller::message_handler_config(Message *message) {
    int32_t code = message->get_code();
    float *args = message->get_args();
    switch (code) {
        case 1: {  // set homing_direction
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            int8_t homing_direction = static_cast<int8_t>(args[1]);
            MovementDriver *movement_driver =
                this->joints[joint_idx]->get_movement_driver();

            movement_driver->set_homing_direction(homing_direction);
        } break;
        case 3: {  // get homing_direction
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            MovementDriver *movement_driver =
                this->joints[joint_idx]->get_movement_driver();
            int8_t homing_direction = movement_driver->get_homing_direction();
            float homing_direction_float = static_cast<float>(homing_direction);
            float *args_buff = static_cast<float *>(malloc(2 * sizeof(float)));
            args_buff[0] = args[0];
            args_buff[1] = homing_direction_float;
            Message *config_message =
                new Message(MessageOp::CONFIG, 4, 2, args_buff);
            this->arm_client.send_message(config_message);
            delete config_message;

        } break;
        case 5: {  // set seeed rad/s
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            float speed_rad_per_second = args[1];
            MovementDriver *movement_driver =
                this->joints[joint_idx]->get_movement_driver();

            movement_driver->set_speed(speed_rad_per_second);
        } break;
        case 7: {  // get speed rad/s
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            MovementDriver *movement_driver =
                this->joints[joint_idx]->get_movement_driver();
            float speed_rad_per_second = movement_driver->get_speed();
            float *args_buff = static_cast<float *>(malloc(2 * sizeof(float)));
            args_buff[0] = args[0];
            args_buff[1] = speed_rad_per_second;
            Message *config_message =
                new Message(MessageOp::CONFIG, 8, 2, args_buff);
            this->arm_client.send_message(config_message);
            delete config_message;
        } break;

        case 9: {  // set steps_per_revolution_axis
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            uint32_t steps_per_revolution_motor_axis =
                static_cast<uint32_t>(args[1]);
            this->joints[joint_idx]->set_steps_per_revolution_motor_axis(
                steps_per_revolution_motor_axis);

        } break;
        case 11: {  // get steps_per_revolution_axis
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            uint32_t steps_per_revolution_motor_axis =
                this->joints[joint_idx]->get_steps_per_revolution_motor_axis();
            float steps_per_revolution_motor_axis_float =
                static_cast<float>(steps_per_revolution_motor_axis);

            float *args_buff = static_cast<float *>(malloc(2 * sizeof(float)));
            args_buff[0] = args[0];
            args_buff[1] = steps_per_revolution_motor_axis_float;
            Message *config_message =
                new Message(MessageOp::CONFIG, 12, 2, args_buff);
            this->arm_client.send_message(config_message);
            delete config_message;
        } break;

        case 13: {  // set convertion_rate_axis_joint
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            float convertion_rate_axis_joint = args[1];
            this->joints[joint_idx]->set_conversion_rate_axis_joint(
                convertion_rate_axis_joint);
        } break;

        case 15: {  // get convertion_rate_axis_joint
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            float convertion_rate_axis_joint =
                this->joints[joint_idx]->get_conversion_rate_axis_joint();
            float *args_buff = static_cast<float *>(malloc(2 * sizeof(float)));
            args_buff[0] = args[0];
            args_buff[1] = convertion_rate_axis_joint;
            Message *config_message =
                new Message(MessageOp::CONFIG, 16, 2, args_buff);
            this->arm_client.send_message(config_message);
            delete config_message;
        } break;

        case 17: {  // set homing offset rads
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            float homing_offset = args[1];
            MovementDriver *movement_driver =
                this->joints[joint_idx]->get_movement_driver();
            movement_driver->set_homing_offset(homing_offset);

        } break;

        case 19: {  // get homing offset rads
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            MovementDriver *movement_driver =
                this->joints[joint_idx]->get_movement_driver();

            float homing_offset = movement_driver->get_homing_offset();

            float *args_buff = static_cast<float *>(malloc(2 * sizeof(float)));
            args_buff[0] = args[0];
            args_buff[1] = homing_offset;
            Message *config_message =
                new Message(MessageOp::CONFIG, 20, 2, args_buff);
            this->arm_client.send_message(config_message);
            delete config_message;
        } break;
        default:
            break;
    }

    message->set_complete(true);
    message->set_called(true);
}

bool Controller::hardware_setup() {  // every function here should be defined
                                     // for every platform
    std::cout << "Setting up hardware" << std::endl;
    global_setup_hardware();
    for (uint8_t i = 0; i < this->joints.size(); i++) {
        MovementDriver *movement_driver =
            this->joints[i]->get_movement_driver();

        movement_driver->hardware_setup();
    }
    Tool *tool = this->get_tool();

    tool->get_movement_driver()->hardware_setup();

    return true;
}

// Hardware related methods

#ifdef ESP_PLATFORM

void Controller::step_target_fun() {
    task_add();
    while (this->stop_flag == false) {
        task_feed();
        this->step();
        task_feed();
        run_delay(10);
    }
    task_end();
}

static void step_target_fun_adapter(void *pvParameters) {
    Controller *instance = static_cast<Controller *>(pvParameters);
    instance->step_target_fun();
}

void Controller::run_step_task() {
    xTaskCreate(&step_target_fun_adapter, "step_task", 2048, this,
                configMAX_PRIORITIES - 1, NULL);
}

void Controller::stop_step_task() {}

#else

void Controller::step_target_fun() {
    while (this->stop_flag == false) {
        this->step();
    }
}

void Controller::run_step_task() {
    this->step_thread = new std::thread(&Controller::step_target_fun, this);
}

void Controller::stop_step_task() {
    if (this->step_thread == nullptr) {
        return;
    }

    if (this->step_thread->joinable()) {
        this->step_thread->join();
    }

    delete this->step_thread;
    this->step_thread = nullptr;
}
#endif
