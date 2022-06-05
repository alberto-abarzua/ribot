#ifndef coms_h
#define coms_h
#include "Arduino.h"
#include <ArduinoQueue.h>


/**
 * @brief author Alberto Abarzua
 * 
 */

//Statuses
#define READY_STATUS '1'
#define INITIALIZED '0'
#define PRINTED ';'
#define UNK '?'
#define BUSY '2'
#define CONTINUE '3'

#define READING_BUFFER_SIZE  64
#define MAX_ARGS 8
#define MESSAGE_BUFFER_SIZE 100


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

class ComsManager{
  private:
    char status; //Current status
    bool NEW_DATA;
    byte * BUF;
    int max_val;
    bool DEBUG;
    ArduinoQueue<Message*> * q_fresh; //Queue to store unused messages.
    ArduinoQueue<Message*> * q_run; // Queue to store messages that need to be executed.
    unsigned long avg_loop_time =0; //Rolling average.
    unsigned long last_dt=0;

    Message * cur_message;

    /**
     * @brief Reads from serial, and stores it in BUF.
     * 
     * @param buf 
     * @param max_size 
     * @param newData 
     */
    void read();
    /**
     * @brief Interpretes the bytes stored in BUF as a message and stores it in m.
     * 
     * @param m Message object where the contents of buf are going to be stored.
     */
    void getMessage(Message *m);

    /**
     * @brief Checks if the run queue is almost emtpy
     * 
     * @return true if there are few elements in q_run
     * @return false ...
     */
    bool almostEmpty();
    /**
     * @brief Checks if the ComsManager is busy. If it is not it updates the status to CONTINUE.
     * 
     */
    void check_busy();


      /**
     * @brief Cehcks if there are messages to be read.
     * 
     * @return true if there is new data received from the serial.
     * @return false if there are no new messages.
     */
    bool new_data();
    /**
   * @brief Gets the message from the buffer buf
   * 
   * @param buf Buffer from where it reads
   * @param m  Message to store the data.
   */
  void getMessage(byte * buf,Message *m);

  /**
     * @brief Determines if the ComsManager can receive new messages.
     * 
     * @return true if new messages can be received.
     * @return false if no new messages can be received.
     */
    bool can_receive();


        /**
     * @brief Used to read from the serial port of the arduino,
     * 
     * @param buf buffer where the read bytes are stored
     * @param max_size Max size of the buffer
     * @param newData Used to indicate if there is new data incoming.
     */
    void my_read(byte * buf,int max_size,bool* newData);
  public:
  /**
   * @brief Initializes all the variables used during comunication.
   * 
   */
    void init_coms();

    
    /**
     * @brief Runs the ComsManager. Reads from serial and interprets new messages. Must be called as often as possible (every loop)
     * 
     * @return true If there is a new message ready to be read.
     * @return false If there is no new message.
     */
    bool run_coms();
    
    /**
     * @brief Gets the current message
     * 
     * @return cur_message
     */
    Message* getCurrentMessage();
    

    /**
     * @brief Sets the current status, and writes it to serial.
     * 
     * @param status 
     */
    void set_status(char new_status);
    
    /**
     * @brief Adds a new message m to the run queue.
     * 
     * @param m new message to be added.
     */
    void addRunQueue(Message *m);


    /**
     * @brief Removes a message from the run queue and returns it.
     * 
     * @return Message* Message removed from q_run
     */
    Message * popRunQueue();
    /**
     * @brief Checks if the run queue is empty or not
     * 
     * @return true if run queue is emtpy
     * @return false if runQueue is not empty
     */
    bool isEmptyRunQueue();
    /**
     * @brief Peeks the run queue
     * 
     * @return Message* peeks the first message form the run queue (does not remove it) 
     */
    Message * peekRunQueue();


  

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
   * @brief Prints the statuses of the queues to serial.
   * 
   */
  void show_queues();



};

#endif