#include "messages.h"

Message::Message(char op, int32_t code, int32_t num_args, float *args) {
    this->op = op;
    this->code = code;
    this->num_args = num_args;
    this->args = args;
    int16_t size_headers = sizeof(char) + sizeof(int32_t) * 2;
    int16_t size_args = sizeof(float) * this->num_args;
    this->size = size_headers + size_args;
}

Message::Message(char *message_bytes) {
    this->op = message_bytes[0];
    this->code = *((int32_t *)(message_bytes + sizeof(char)));
    this->num_args =
        *((int32_t *)(message_bytes + sizeof(char) + sizeof(int32_t)));
    this->args = (float *)malloc(sizeof(float) * this->num_args);
    memcpy(this->args, message_bytes + sizeof(char) + sizeof(int32_t) * 2,
           sizeof(float) * this->num_args);
}

Message::~Message() {
    if (this->args != NULL) free(this->args);
}

char Message::get_op() { return this->op; }

int32_t Message::get_code() { return this->code; }

int32_t Message::get_num_args() { return this->num_args; }

float *Message::get_args() { return this->args; }

void Message::get_bytes(char *message_bytes) {
    memcpy(message_bytes, &this->op, sizeof(char));
    memcpy(message_bytes + sizeof(char), &this->code, sizeof(int32_t));
    memcpy(message_bytes + sizeof(char) + sizeof(int32_t), &this->num_args,
           sizeof(int32_t));
    memcpy(message_bytes + sizeof(char) + sizeof(int32_t) * 2, this->args,
           sizeof(float) * this->num_args);
}

int32_t Message::get_size() { return this->size; }

void Message::print() {
    std::cout << "Message: ------ " << std::endl;
    std::cout << "op: " << this->op << std::endl;
    std::cout << "code: " << this->code << std::endl;
    std::cout << "num_args: " << this->num_args << std::endl;
    std::cout << "args: ";
    for (int i = 0; i < this->num_args; i++) {
        std::cout << this->args[i] << " ";
    }
    std::cout << "\n------------";
    std::cout << std::endl;
}