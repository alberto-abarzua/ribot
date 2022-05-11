#ifndef coms_h
#define coms_h

//Statuses
#define READY_STATUS '1'
#define INITIALIZED '0'
#define PRINTED ';'


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
  
    Message(char nop,long ncode,long *nargs,int nnum_args);
    Message(long*nargs);
    void show();
    void destroy();
    void rebuild(char nop,long ncode,long *nargs,int nnum_args);
    
};

/**
 * @brief Gets the message from the buffer buf
 * 
 * @param buf Buffer from where it reads
 * @param m  Message to store the data.
 */
void getMessage(byte * buf,Message *m);

long get_long(byte * buf,int offset);
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
bool new_data();
Message * getM();
int getNumArgs();
long * getArgs();
int getCode();
char getOP();
void init_coms();
void set_status(char status);



#endif