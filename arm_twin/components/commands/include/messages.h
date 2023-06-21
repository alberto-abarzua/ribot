#ifndef MESSAGES_H
#define MESSAGES_H

#include <cstring>
#include <iostream>
#include <stdint.h>

class Message {
   private:
    char op;
    int32_t code;
    int32_t num_args;
    int32_t size;

    float* args;

   public:
    Message(char op, int32_t code, int32_t num_args, float* args);

    Message(char * message_bytes);

    ~Message();

    char get_op();
    int32_t get_code();
    int32_t get_num_args();
    float* get_args();
    int32_t get_size();


    void get_bytes(char* message_bytes);

    void print();


    
};


#endif