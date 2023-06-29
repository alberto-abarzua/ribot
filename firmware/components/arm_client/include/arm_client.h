#include <unistd.h>     
#include <cstring>  
#include <sys/types.h>
#include <iostream>
#include "messages.h"
#include <fcntl.h>
#include <errno.h>
#include "config.h"







/**
 * @brief ArmClient class, This class is used to create a TCP socket to comunicate with the python controller
 * This is completely independent from the rest of the code, this is portion is going to be reprogramed for the 
 * esp32 version of the arm
 * 
 */
class ArmClient {
   private:
    int clientSocket;
    int start_socket();

   public:
    ArmClient();

    ~ArmClient();


    int send_message(Message *msg);

    int receive_message(Message **msg);

    int setup();

    void stop();

};

