#ifndef MESSAGES_H
#define MESSAGES_H

#include <stdint.h>
#include <cstring>
#include <iostream>

class Message {
   private:
    char op;
    int32_t code;
    int32_t num_args;
    int32_t size;
    float* args;
    bool complete = false;
    bool called = false;

   public:
    static const uint8_t HEADER_SIZE = sizeof(char) + sizeof(int32_t) * 2;
    Message(char op, int32_t code, int32_t num_args, float* args);

    explicit Message(char* message_bytes);

    ~Message();

    char get_op();
    int32_t get_code();
    int32_t get_num_args();
    float* get_args();
    int32_t get_size();

    void get_bytes(char* message_bytes);

    bool is_complete();
    bool was_called();
    bool set_called(bool called);
    void set_complete(bool complete);
    static int parse_headers(char* message_bytes, char* op, int32_t* code,
                             int32_t* num_args);

    void print();
};

#endif