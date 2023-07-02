#include "controller.h"

/**
 * -----------------------------------------------------------------
 * ------------------------ JOINT CLASS ---------------------------
 * -----------------------------------------------------------------
 */
Joint::Joint(int8_t step_pin, int8_t dir_pin, int8_t homing_direction,
             uint32_t steps_per_revolution_motor_axis) {
    this->current_angle = 0.0;
    this->target_angle = 0.0;
    this->current_steps = 0;
    this->step_pin = step_pin;
    this->dir_pin = dir_pin;
    this->homing_direction = homing_direction;
    this->steps_per_revolution_motor_axis = steps_per_revolution_motor_axis;
    this->convertion_rate_axis_joint = 1.0;
    this->steps_per_revolution = this->steps_per_revolution_motor_axis *
                                 this->convertion_rate_axis_joint;
    this->epsilon = this->steps_to_angle(1);
    this->last_step_time = get_current_time_microseconds();
    this->homing_offset = (PI * this->homing_direction) / 4;  // 45 degrees
    this->homed = false;
}

Joint::~Joint() {}

void Joint::set_target_angle(float angle) {
    this->last_step_time = get_current_time_microseconds();
    this->target_angle = angle;
}

uint32_t Joint::steps_to_take(uint64_t current_time) {
    // gets the number of steps that should be taken
    uint64_t dif = current_time - this->last_step_time;
    uint64_t steps = std::floor(dif / this->step_interval);
    uint64_t steps_to_target =
        std::abs(this->angle_to_steps(this->target_angle) -
                 this->angle_to_steps(this->current_angle));
    return std::min(steps, steps_to_target);
}

float Joint::get_current_angle() { return this->current_angle; }

float Joint::get_target_angle() { return this->target_angle; }

bool Joint::home_joint() {
    this->set_target_angle(this->homing_direction * 2 * PI);
    this->homing = true;
    this->homed = false;
    return true;
}

bool Joint::set_home() {
    this->current_angle = this->homing_offset;
    this->target_angle = 0;
    this->current_steps = this->angle_to_steps(this->current_angle);
    this->homed = true;
    return true;
}

bool Joint::step() {
    if (this->homing) {
        if (this->hardware_end_stop_read()) {
            this->set_home();
            this->homing = false;
            return false;
        }
    }
    uint64_t current_time = get_current_time_microseconds();
    uint32_t steps_to_take = this->steps_to_take(current_time);
    int8_t step_dir;
    if (steps_to_take > 0) {
        step_dir = this->target_angle > this->current_angle ? 1 : -1;
        for (uint16_t i = 0; i < steps_to_take; i++) {
            this->hardware_step(step_dir > 0 ? 1 : 0);
            this->current_steps += step_dir;
            this->current_angle = this->steps_to_angle(this->current_steps);
            this->last_step_time = get_current_time_microseconds();
        }
        return true;
    }
    return false;
}

bool Joint::at_target() {
    return (std::abs(this->current_angle - this->target_angle) <=
            this->epsilon);
}

void Joint::set_speed_steps_per_second(uint32_t speed_steps_per_second) {
    this->speed_steps_per_second = speed_steps_per_second;
    // convert to microseconds
    this->step_interval = std::abs(1000000.0 / this->speed_steps_per_second);
}

void Joint::set_speed_rad_per_second(float speed_rad_per_second) {
    this->set_speed_steps_per_second(
        this->angle_to_steps(speed_rad_per_second));
}

int32_t Joint::get_speed_steps_per_second() {
    return this->speed_steps_per_second;
}

void Joint::update_current_angle() {
    this->current_angle = this->steps_to_angle(this->current_steps);
}

float Joint::steps_to_angle(int64_t steps) {
    return static_cast<float>(steps) /
           static_cast<float>(this->steps_per_revolution) * 2.0 * PI;
}

int64_t Joint::angle_to_steps(float angle) {
    return static_cast<int64_t>(angle / (2 * PI) * this->steps_per_revolution);
}

/**
 * -----------------------------------------------------------------
 * ------------------------ CONTROLLER CLASS ---------------------------
 * -----------------------------------------------------------------
 */

Controller::Controller() {
    this->arm_client = ArmClient();
    this->joints = std::vector<Joint *>();
    this->joints.push_back(new Joint(0, 0, 1, 8000));
    this->joints.push_back(new Joint(0, 0, 1, 8000));
    this->joints.push_back(new Joint(0, 0, 1, 8000));
    this->joints.push_back(new Joint(0, 0, 1, 8000));
    this->joints.push_back(new Joint(0, 0, 1, 8000));
    this->joints.push_back(new Joint(0, 0, 1, 5000));

    // set speeds
    for (uint16_t i = 0; i < this->joints.size(); i++) {
        this->joints[i]->set_speed_rad_per_second(1.0);
    }
    // Message handlers
    this->message_op_handler_map['M'] = &Controller::message_handler_move;
    this->message_op_handler_map['S'] = &Controller::message_handler_status;
    this->message_op_handler_map['C'] = &Controller::message_handler_config;

    // Message qs
    for (auto const &[key, val] : this->message_op_handler_map) {
        this->message_queues[key] = new std::queue<Message *>();
    }
}

Controller::~Controller() { this->arm_client.stop(); }

bool Controller::recieve_message() {
    Message *msg;
    int ret = this->arm_client.receive_message(&msg);
    if (ret == -1) {
        return false;
    } else if (ret == 0) {
        return true;
    }

    char op = msg->get_op();
    // check if op key exists
    if (this->message_queues.find(op) == this->message_queues.end()) {
        std::cout << "Ret " << ret << " Invalid op code: " << op << std::endl;
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
        all_homed &= this->joints[i]->homed;
    }
    this->homed = all_homed;
    return all_homed;
}

void Controller::stop() {
    this->stop_flag = true;
    this->arm_client.stop();
    this->stop_step_task();
    // delete queues
    for (auto const &[key, val] : this->message_queues) {
        std::queue<Message *> *message_queue = val;
        while (message_queue->size() > 0) {
            Message *msg = message_queue->front();
            message_queue->pop();
            delete msg;
        }
        delete message_queue;
    }
    // delete joints
    for (uint8_t i = 0; i < this->joints.size(); i++) {
        delete this->joints[i];
    }
}

void Controller::stop(int signum) {
    std::cout << "Stopping controller "<<signum << std::endl;
    this->stop();
}

void Controller::step() {
    for (uint8_t i = 0; i < this->joints.size(); i++) {
        this->joints[i]->step();
    }
}

void Controller::start() {
    run_delay(1000);
    std::cout << "Starting controller" << std::endl;
    this->hardware_setup();
    int succesful_setup = this->arm_client.setup();
    uint64_t timeout = 1;
    while (succesful_setup != 0) {
        run_delay(timeout);
        timeout *= 2;
        succesful_setup = this->arm_client.setup();
    }
    this->run_step_task();
    std::cout << "Connected to the server" << std::endl;
    uint64_t last_message_time = get_current_time_microseconds();
    while (true) {
        if (this->recieve_message()) {
            this->handle_messages();  // handles messages on queue
            last_message_time = get_current_time_microseconds();
        }else{
            // if more than 5 seconds since last message
            if (get_current_time_microseconds() - last_message_time > 5*1000000) {
                std::cout << "No message in 5 seconds, stopping controller" << std::endl;
                this->stop();
                break;
            }
        }
        run_delay(10);
    }
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
            char op = msg->get_op();
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
                }
                if (all_at_target) {
                    message->set_complete(true);
                }
            }
        } break;
        case 3: {  // home all joints
            if (!called) {
                std::cout << "Homing all joints\n";
                for (uint8_t i = 0; i < this->joints.size(); i++) {
                    this->joints[i]->home_joint();
                }
                message->set_called(true);
                this->homed = false;
            } else {
                bool all_homed = true;
                for (int i = 0; i < num_args; i++) {
                    all_homed &= this->joints[i]->homed;
                }
                if (all_homed) {
                    message->set_complete(true);
                    std::cout << "All joints homed\n";
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
                if (this->joints[joint_idx]->homed) {
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
            int message_size = this->joints.size() + 2;
            float *args =
                static_cast<float *>(malloc(sizeof(float) * message_size));
            for (uint8_t i = 0; i < this->joints.size(); i++) {
                args[i] = this->joints[i]->get_current_angle();
            }
            int move_message_queue_size = this->message_queues['M']->size();
            // queue size
            args[message_size - 2] = move_message_queue_size;
            // homed
            args[message_size - 1] = this->is_homed() ? 1 : 0;

            Message *status_message = new Message('S', 1, message_size, args);
            this->arm_client.send_message(status_message);
            message->set_complete(true);
            message->set_called(true);
            delete status_message;
        } break;
        case 3: {
            Message *status_message = new Message('S', 4, 0, nullptr);
            this->arm_client.send_message(status_message);
            delete status_message;

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
            this->joints[joint_idx]->homing_direction = homing_direction;
        } break;
        case 3: {  // get homing_direction
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            int8_t homing_direction = this->joints[joint_idx]->homing_direction;
            float homing_direction_float = static_cast<float>(homing_direction);
            Message *config_message =
                new Message('C', 4, 1, &homing_direction_float);
            this->arm_client.send_message(config_message);
            delete config_message;

        } break;
        case 5: {  // set seeed rad/s
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            float speed_rad_per_second = args[1];
            this->joints[joint_idx]->set_speed_rad_per_second(
                speed_rad_per_second);
        } break;
        case 7: {  // get speed rad/s
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            float speed_rad_per_second =
                this->joints[joint_idx]->get_speed_steps_per_second();
            Message *config_message =
                new Message('C', 8, 1, &speed_rad_per_second);
            this->arm_client.send_message(config_message);
            delete config_message;
        } break;

        case 9: {  // set steps_per_revolution_axis
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            uint32_t steps_per_revolution_motor_axis =
                static_cast<uint32_t>(args[1]);
            this->joints[joint_idx]->steps_per_revolution_motor_axis =
                steps_per_revolution_motor_axis;
        } break;
        case 11: {  // get steps_per_revolution_axis
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            uint32_t steps_per_revolution_motor_axis =
                this->joints[joint_idx]->steps_per_revolution_motor_axis;
            float steps_per_revolution_motor_axis_float =
                static_cast<float>(steps_per_revolution_motor_axis);

            Message *config_message =
                new Message('C', 12, 1, &steps_per_revolution_motor_axis_float);
            this->arm_client.send_message(config_message);
            delete config_message;
        } break;

        case 13: {  // set convertion_rate_axis_joint
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            float convertion_rate_axis_joint = args[1];
            this->joints[joint_idx]->convertion_rate_axis_joint =
                convertion_rate_axis_joint;
        } break;

        case 15: {  // get convertion_rate_axis_joint
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            float convertion_rate_axis_joint =
                this->joints[joint_idx]->convertion_rate_axis_joint;
            Message *config_message =
                new Message('C', 16, 1, &convertion_rate_axis_joint);
            this->arm_client.send_message(config_message);
            delete config_message;
        } break;

        case 17: {  // set homing offset rads
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            float homing_offset = args[1];
            this->joints[joint_idx]->homing_offset = homing_offset;

        } break;

        case 19: {
            uint8_t joint_idx = static_cast<uint8_t>(args[0]);
            float homing_offset = this->joints[joint_idx]->homing_offset;
            Message *config_message = new Message('C', 20, 1, &homing_offset);
            this->arm_client.send_message(config_message);
            delete config_message;
        } break;
        default:
            break;
    }

    message->set_complete(true);
    message->set_called(true);
}
