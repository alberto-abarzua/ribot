#ifndef MESSAGES_H
#define MESSAGES_H

#include <stdint.h>

#include <cstring>
#include <iostream>

enum class MessageOp { MOVE = 'M', STATUS = 'S', CONFIG = 'C' };

class Message {
   private:
    MessageOp op;
    int32_t code;
    int32_t num_args;
    int32_t size;
    float* args;
    bool complete = false;
    bool called = false;

   public:
    static const uint8_t HEADER_SIZE = sizeof(char) + sizeof(int32_t) * 2;
    Message(MessageOp op, int32_t code, int32_t num_args, float* args);

    explicit Message(char* message_bytes);

    ~Message();

    MessageOp get_op();
    int32_t get_code();
    int32_t get_num_args();
    float* get_args();
    int32_t get_size();

    void get_bytes(char* message_bytes);

    bool is_complete();
    bool was_called();
    bool set_called(bool called);
    void set_complete(bool complete);
    static int parse_headers(char* message_bytes, MessageOp* op, int32_t* code,
                             int32_t* num_args);
    static MessageOp get_op_from_char(char op);

    void print();
};

#endif