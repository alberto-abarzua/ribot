#include "controller.h"


Controller::Controller() {
    this->arm_client = ArmClient();
}


Controller::~Controller() {
    this->arm_client.stop();
}


void Controller::start() {
    int succesful_setup = this->arm_client.setup();
    while(succesful_setup!=0){
        std::cout<<"Trying to connect to the server"<<std::endl;
        succesful_setup = this->arm_client.setup();
    }
    while (true) {
        std::this_thread::sleep_for(std::chrono::seconds(1));

        Message * msg = this->arm_client.receive_message();
        if (msg == nullptr) {
            std::cout << "Error reading message" << std::endl;
            continue;
        }
        std::cout << "Message received!" << std::endl;

        msg->print();
        delete msg;
    }
}


void Controller::stop() {
    this->arm_client.stop();
}

