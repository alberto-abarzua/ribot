#ifndef coms_h
#define coms_h
#include "Arduino.h"

#include <ArduinoQueue.h>
//Statuses
#define READY_STATUS '1'
#define INITIALIZED '0'
#define PRINTED ';'
#define UNK '?'
#define BUSY '2'
#define CONTINUE '3'

#define READING_BUFFER_SIZE  64
#define MAX_ARGS 8
#define MESSAGE_BUFFER_SIZE 50


/**
 * @brief Message class, used to create new messages.
 * 
 */
class Message{
  public:
    char op;
    long code;
    long * args;
    int num_args;
    bool viewed;
    
    Message(long*nargs);
    /**
     * @brief Prints to serial a string representation of this message
     * 
     */
    void show();
    /**
     * @brief Frees the memory used
     * 
     */
    void destroy();
    /**
     * @brief Reassings the variables of the message.
     * 
     * @param nop new operation 
     * @param ncode new code
     * @param nargs new number of args
     * @param nnum_args new array of args.
     */
    void rebuild(char nop,long ncode,long *nargs,int nnum_args);
    
};

/**
 * @brief Gets the message from the buffer buf
 * 
 * @param buf Buffer from where it reads
 * @param m  Message to store the data.
 */
void getMessage(byte * buf,Message *m);

/**
 * @brief Converts the first 4 bytes in buf from offset into an arduino long.  
 * 
 * @param buf byte array 
 * @param offset number from where to start reading
 * @return long stored in the buf array starting from offset
 */
long get_long(byte * buf,int offset);


/**
 * @brief Prints a certain amount of bytes (as chars) from the buffer
 * 
 * @param buf byte array,
 * @param num number of bytes to print.
 */
void printBuf(byte * buf,int num);
/**
 * @brief Used to read from the serial port of the arduino,
 * 
 * @param buf buffer where the read bytes are stored
 * @param max_size Max size of the buffer
 * @param newData Used to indicate if there is new data incoming.
 */
void my_read(byte * buf,int max_size,bool* newData);



/**
 * @brief Runs the reading function to read from serial and stores it in the global message.
 * 
 * @return true if there is data left to read
 * @return false if there is no data incoming (Message can be read properly)
 */
bool run_reader();
/**
 * @brief Cehcks if there are messages to be read.
 * 
 * @return true if there is new data received from the serial.
 * @return false if there are no new messages.
 */
bool new_data();
/**
 * @brief Gets the first message from the message buffer
 * 
 * @return Message* 
 */
Message * getM();
/**
 * @brief Peeks the first message from the message buffer
 * 
 * @return Message* 
 */
Message * peekM();


/**
 * @brief Initializes all the variables used in the comunication logic.
 * 
 */
void init_coms();
/**
 * @brief Sets the current status, and writes it to serial.
 * 
 * @param status 
 */
void set_status(char status);


/**
 * @brief Returns true if the buffer can accept new messages.
 * 
 * @return true if new messages can be accepted
 * @return false if the message buffer ir full
 */
bool can_receive();

/**
 * @brief Enqueues a new move message
 * 
 * @param m message to be enqueued
 */
void queueMove(Message *m);
/**
 * @brief Removes a move message from the move queue.
 * 
 * @return Message* message removed.
 */
Message * unqueueMove();

/**
 * @brief Prints the statuses of the queues to serial.
 * 
 */
void show_queues();
/**
 * @brief Returns M to the queue of fresh messsages (not in use)
 * 
 */
void returnM(Message * M);

/**
 * @brief Toggles debug mode.
 * 
 */
void toggle_debug();

/**
 * @brief checks if the move queue is empty or not.
 * 
 */
bool movesOnQueue();

/**
 * @brief Checks if the arduino is, busy. If it can receive new messages it changes it's state to CONTINUE
 * 
 */
void check_busy();

#endif