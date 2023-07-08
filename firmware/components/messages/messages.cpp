#include "messages.h"

MessageOp Message::get_op_from_char(char op) {
    switch (op) {
        case 'M':
            return MessageOp::MOVE;
        case 'S':
            return MessageOp::STATUS;
        case 'C':
            return MessageOp::CONFIG;
        default:
            throw std::invalid_argument("Invalid character");
    };
};

Message::Message(MessageOp op, int32_t code, int32_t num_args, float *args) {
    this->op = op;
    this->code = code;
    this->num_args = num_args;
    this->args = args;
    int16_t size_args = sizeof(float) * this->num_args;
    this->size = Message::HEADER_SIZE + size_args;
}

Message::Message(char *message_bytes) {
    this->op = Message::get_op_from_char(message_bytes[0]);
    this->code = *(reinterpret_cast<int32_t *>(message_bytes + sizeof(char)));
    this->num_args = *(reinterpret_cast<int32_t *>(
        message_bytes + sizeof(char) + sizeof(int32_t)));
    this->args = static_cast<float *>(malloc(sizeof(float) * this->num_args));
    memcpy(this->args, message_bytes + sizeof(char) + sizeof(int32_t) * 2,
           sizeof(float) * this->num_args);
    int16_t size_headers = sizeof(char) + sizeof(int32_t) * 2;
    int16_t size_args = sizeof(float) * this->num_args;
    this->size = size_headers + size_args;
}

Message::~Message() {
    if (this->args != NULL && this->num_args > 1) {
        free(this->args);
    }
}

MessageOp Message::get_op() { return this->op; }

int32_t Message::get_code() { return this->code; }

int32_t Message::get_num_args() { return this->num_args; }

float *Message::get_args() { return this->args; }

void Message::get_bytes(char *message_bytes) {
    char op = static_cast<char>(this->op);
    memcpy(message_bytes, &op, sizeof(char));
    memcpy(message_bytes + sizeof(char), &this->code, sizeof(int32_t));
    memcpy(message_bytes + sizeof(char) + sizeof(int32_t), &this->num_args,
           sizeof(int32_t));
    memcpy(message_bytes + sizeof(char) + sizeof(int32_t) * 2, this->args,
           sizeof(float) * this->num_args);
}

int32_t Message::get_size() { return this->size; }

void Message::print() {
    std::cout << "Message: ------ " << std::endl;
    std::cout << "op: " << static_cast<char>(this->op) << std::endl;
    std::cout << "code: " << this->code << std::endl;
    std::cout << "num_args: " << this->num_args << std::endl;
    std::cout << "args: ";
    for (int i = 0; i < this->num_args; i++) {
        std::cout << this->args[i] << " ";
    }
    std::cout << "\n------------";
    std::cout << std::endl;
}

bool Message::was_called() { return this->called; }

bool Message::is_complete() { return this->complete; }

bool Message::set_called(bool called) {
    this->called = called;
    return this->called;
}

void Message::set_complete(bool complete) { this->complete = complete; }

int Message::parse_headers(char *message_bytes, MessageOp *op, int32_t *code,
                           int32_t *num_args) {
    char op_char = message_bytes[0];
    *op = Message::get_op_from_char(op_char);
    *code = *(reinterpret_cast<int32_t *>(message_bytes + sizeof(char)));
    *num_args = *(reinterpret_cast<int32_t *>(message_bytes + sizeof(char) +
                                              sizeof(int32_t)));
    return 0;
}