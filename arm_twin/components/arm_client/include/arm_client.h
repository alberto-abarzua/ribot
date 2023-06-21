#ifndef ARM_CLIENT_H  
                
#define ARM_CLIENT_H


#include <arpa/inet.h>   
#include <sys/socket.h>  
#include <unistd.h>     
#include <cstring>  
#include <netdb.h>
#include <sys/types.h>
#include <iostream>
#include "messages.h"



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

    Message * receive_message();

    int setup();

    void stop();

};

#endif