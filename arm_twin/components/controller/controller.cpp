#include "controller.h"

/**
 * -----------------------------------------------------------------
 * ------------------------ JOINT CLASS ---------------------------
 * -----------------------------------------------------------------
 */
Joint::Joint(int8_t step_pin, int8_t dir_pin, int8_t homing_direction,
             uint32_t steps_per_revolution) {
    this->current_angle = 0.0;
    this->target_angle = 0.0;
    this->current_steps = 0;
    this->step_pin = step_pin;
    this->dir_pin = dir_pin;
    this->homing_direction = homing_direction;
    this->steps_per_revolution = steps_per_revolution;
    // set epsilon depending to steps_per_revolution
    this->epsilon = this->steps_to_angle(1) / 2;
    // std::cout << "Epsilon: " << this->epsilon << std::endl;
    this->last_step_time = get_current_time_microseconds();
}

Joint::~Joint() {}

void Joint::set_target_angle(float angle) { this->target_angle = angle; }

float Joint::get_current_angle() { return this->current_angle; }

float Joint::get_target_angle() { return this->target_angle; }

bool Joint::home_joint() {
    this->set_target_angle(this->homing_direction * 2 * PI);
    this->homing = true;
    return true;
}

bool Joint::set_home() {
    this->current_angle = this->homing_offset;

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
    if (this->at_target()) {
        return false;
    }

    // std::cout << "Last step time: " << this->last_step_time << std::endl;
    // std::cout << "Step interval: " << this->step_interval << std::endl;
    //  dif
    uint64_t current_time = get_current_time_microseconds();
    if (current_time - this->last_step_time <= this->step_interval) {
        // std::cout << "Current time in false: " << current_time << std::endl;
        return false;
    }

    // std::cout << "Current time: " << current_time << std::endl;

    uint8_t step_direction;
    if (this->target_angle >= this->current_angle) {
        step_direction = 1;
    } else {
        step_direction = 0;
    }

    bool res = this->hardware_step(step_direction);
    this->last_step_time = get_current_time_microseconds();
    if (res) {
        if (step_direction == 1) {
            this->current_steps++;
        } else {
            this->current_steps--;
        }
    }
    this->update_current_angle();

    return res;
}

bool Joint::at_target() {
    return (std::abs(this->current_angle - this->target_angle) <=
            this->epsilon);
}

void Joint::set_speed_steps_per_second(uint32_t speed_steps_per_second) {
    this->speed_steps_per_second = speed_steps_per_second;
    // convert to microseconds
    this->step_interval = std::abs(1000000.0 / this->speed_steps_per_second);
    // std::cout << "Step interval: " << this->step_interval << std::endl;
}

void Joint::set_speed_rad_per_second(float speed_rad_per_second) {
    // Convert speed from radians/second to equivalent in steps/second
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
    return (float)steps / (float)this->steps_per_revolution * 2.0 * PI;
}

int64_t Joint::angle_to_steps(float angle) {
    return (int64_t)(angle / (2 * PI) * this->steps_per_revolution);
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
    for (int i = 0; i < this->joints.size(); i++) {
        this->joints[i]->set_speed_rad_per_second(1.0);
        // std::cout << "Speed joint " << i << ": "
        //<< this->joints[i]->get_speed_steps_per_second() << std::endl;
    }
    this->message_op_handler_map['M'] = &Controller::message_handler_move;
    this->message_op_handler_map['S'] = &Controller::message_handler_status;
}

Controller::~Controller() { this->arm_client.stop(); }

void Controller::send_status_message() {
    /**
     * Status Message
     *
     * op: 'S'
     * code: 1
     * num_args: num_joints + 1
     *
     * args: [joint_1_angle, joint_2_angle, ..., joint_n_angle, QUEUE_SIZE]
     *
     */
    uint64_t current_time = get_current_time_microseconds();
    if (current_time - this->last_status_time <= 500000) {
        return;
    }
    this->last_status_time = current_time;
    int message_size = this->joints.size() + 1;
    float *args = (float *)malloc(sizeof(float) * message_size);
    for (int i = 0; i < this->joints.size(); i++) {
        args[i] = this->joints[i]->get_current_angle();
    }

    args[message_size - 1] = this->message_queue.size();

    Message *status_message = new Message('S', 1, message_size, args);
    // send status
    // print message
    status_message->print();
    this->arm_client.send_message(status_message);
    delete status_message;
}

bool Controller::recieve_message() {
    Message *msg;
    int ret = this->arm_client.receive_message(&msg);
    if (ret == -1) {
        std::cout << "Error receiving message,con lsot" << std::endl;
        return false;
    }else if(ret == 0){
        return true;
    }

    char op = msg->get_op();
    Controller::message_op_handler_t handler = this->message_op_handler_map[op];
    (this->*handler)(msg);
    bool skip = this->skip_message(msg);
    if (!skip) {
        this->message_queue.push_back(msg);
    }
    return true;
}

bool Controller::skip_message(Message *msg) {
    char op = msg->get_op();
    int32_t code = msg->get_code();
    if (op == 'S' && code == 0) {
        return true;
    }
    return false;
}

void Controller::handle_messages() {
    // std::cout << "Messages on queue: " << this->message_queue.size()
    //    << std::endl;
    if (this->message_queue.size() > 0) {
        Message *msg = this->message_queue.front();
        char op = msg->get_op();
        Controller::message_op_handler_t handler =
            this->message_op_handler_map[op];
        (this->*handler)(msg);
        if (msg->is_complete()) {
            this->message_queue.pop_front();
            delete msg;
        }
    }
}

void Controller::message_handler_move(Message *message) {
    // std::cout << "Handling message move" << std::endl;
    message->print();
    int32_t code = message->get_code();
    int32_t num_args = message->get_num_args();
    float *args = message->get_args();
    bool complete = message->is_complete();
    bool called = message->was_called();
    if (code == 1) {
        if (!called) {
            // std::cout << "Setting all joints to target angles" << std::endl;
            for (int i = 0; i < num_args; i++) {
                this->joints[i]->set_target_angle(args[i]);
            }
            message->set_called(true);
        } else {
            // check if all joints are at target angles
            bool all_at_target = true;
            for (int i = 0; i < num_args; i++) {
                all_at_target &= this->joints[i]->at_target();
            }
            if (all_at_target) {
                message->set_complete(true);
            }
        }
    }
}

void Controller::message_handler_status(Message *message) {
    // std::cout << "Handling message status" << std::endl;
    message->print();
    int32_t code = message->get_code();
    int32_t num_args = message->get_num_args();
    float *args = message->get_args();
    bool complete = message->is_complete();
    bool called = message->was_called();
    if (code == 0) {
        message->set_complete(true);
        message->set_called(true);
    } else if (code == 3) {
        Message *status_message = new Message('S', 4, 0, nullptr);
        this->arm_client.send_message(status_message);
        delete status_message;
        message->set_complete(true);
        message->set_called(true);
    }
}

void Controller::print_status() {
    // print all angles and current steps
    for (int i = 0; i < this->joints.size(); i++) {
        // std::cout << "Joint " << i
        //  << " angle: " << this->joints[i]->get_current_angle()
        //  << std::endl;
        // std::cout << "Joint " << i << " steps: "
        //  << this->joints[i]->angle_to_steps(
        //        this->joints[i]->get_current_angle())
        // << std::endl;
    }
}

void Controller::stop() { this->arm_client.stop(); }

void Controller::step() {
    for (int i = 0; i < this->joints.size(); i++) {
        this->joints[i]->step();
    }
}

// Main loop
void Controller::start() {
    run_delay(1000);
    int succesful_setup = this->arm_client.setup();
    while (succesful_setup != 0) {
        std::cout << "Trying to connect to the server" << std::endl;
        run_delay(50);
        succesful_setup = this->arm_client.setup();
    }
    //
    this->run_step_task();
    std::cout << "Connected to the server" << std::endl;
    while (true) {
        if (!this->recieve_message()){
            break;
        }
        this->handle_messages();      // handles messages on queue
        this->print_status();         // prints status
        this->send_status_message();  // sends status message
    }
}
