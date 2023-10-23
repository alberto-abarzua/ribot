#include <errno.h>
#include <fcntl.h>
#include <netdb.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#include <cstring>
#include <iostream>

#include "config.h"
#include "messages.h"
/**
 * @brief ArmClient class, This class is used to create a TCP socket to
 * comunicate with the python controller This is completely independent from the
 * rest of the code, this is portion is going to be reprogramed for the esp32
 * version of the arm
 *
 */

enum class ArmClientCode {
    SUCCESS = 0,
    SOCKET_CREATION_ERROR = -1,
    CONNECTION_ERROR = -2,
    SEND_ERROR = -3,
    RECEIVE_ERROR = -4,
    UNKNOWN_ERROR = -5,
    NO_NEW_DATA = -6,
    ADDR_INFO_ERROR = -7,
    FAILED_TO_SEND = -8,
    FAILED_TO_RECEIVE = -9,
    FAILED_TO_RECEIVE_HEADER = -10,
    FAILED_TO_RECEIVE_ARGS = -11
};

class ArmClient {
   private:
    bool socket_created = false;

    int clientSocket;
    ArmClientCode create_socket();
    ArmClientCode attempt_connection();

   public:
    ArmClient();
    ~ArmClient();

    ArmClientCode setup();
    ArmClientCode send_message(Message *msg);
    ArmClientCode receive_message(Message **msg);
    void stop();
};