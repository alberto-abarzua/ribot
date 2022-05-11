#ifndef coms_h
#define coms_h

//Statuses
#define READY_STATUS '1'
#define INITIALIZED '0'
#define PRINTED ';'
#define UNK '?'


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
 * @brief Returns the value of NEW_DATA
 * 
 * @return true if there is new data received from the serial.
 * @return false 
 */
bool new_data();
/**
 * @brief Gets the global message
 * 
 * @return Message* 
 */
Message * getM();

/**
 * @brief Get the Num Args
 * 
 * @return int 
 */
int getNumArgs();
/**
 * @brief Get the arguments of the global Message M
 * 
 * @return long* array of arguments
 */
long * getArgs();
/**
 * @brief Get the Code of the global message
 * 
 * @return int  code
 */
int getCode();
/**
 * @brief Gets the op of the global message
 * 
 * @return char operation
 */
char getOP();
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



#endif