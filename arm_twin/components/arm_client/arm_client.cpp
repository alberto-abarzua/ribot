

#include "arm_client.h"

#define SERVER_IP "arm_controller"  // replace with your server's IP
#define SERVER_PORT 8500            // replace with your server's port

ArmClient::ArmClient() {
    // std::cout << "ArmClient constructor called" << std::endl;
}

ArmClient::~ArmClient() {
    // std::cout << "ArmClient destructor called" << std::endl;
}

#include <netdb.h>
#include <sys/socket.h>
#include <sys/types.h>

#include "messages.h"

int ArmClient::start_socket() {
    struct addrinfo hints, *res, *rp;
    int s;

    memset(&hints, 0, sizeof(struct addrinfo));
    hints.ai_family = AF_UNSPEC;      // Allow IPv4 or IPv6
    hints.ai_socktype = SOCK_STREAM;  // TCP socket

    s = getaddrinfo(SERVER_IP, std::to_string(SERVER_PORT).c_str(), &hints,
                    &res);
    if (s != 0) {
        std::cerr << "getaddrinfo: " << gai_strerror(s) << std::endl;
        return -1;
    }

    for (rp = res; rp != NULL; rp = rp->ai_next) {
        this->clientSocket =
            socket(rp->ai_family, rp->ai_socktype, rp->ai_protocol);
        if (this->clientSocket == -1) continue;
        if (connect(this->clientSocket, rp->ai_addr, rp->ai_addrlen) != -1)
            break;  // success
        close(this->clientSocket);
    }

    if (rp == NULL) {  // No address succeeded
        std::cerr << "Could not connect\n";
        return -1;
    }

    freeaddrinfo(res);  // No longer needed

    return 0;
}

int ArmClient::send_message(Message *msg) {
    char message_bytes[msg->get_size()];
    msg->get_bytes(message_bytes);
    return send(this->clientSocket, message_bytes, msg->get_size(), 0);
}

int ArmClient::receive_message(Message **msg_loc) {
    char buffer[1024] = {0};
    int result = read(this->clientSocket, buffer, 1024);
    if (result < 0) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return 0;
        } else {
            return -1;
        }
    }
    Message *msg = new Message(buffer);
    *msg_loc = msg;
    return 1;
}

int ArmClient::setup() {
    int ret = this->start_socket();
    if (ret == -1) {
        return -1;
    }

    // Set the socket to be non-blocking
    int flags = fcntl(this->clientSocket, F_GETFL, 0);
    if (flags == -1) {
        perror("Unable to get socket flags");
        exit(EXIT_FAILURE);
    }

    flags |= O_NONBLOCK;
    if (fcntl(this->clientSocket, F_SETFL, flags) == -1) {
        perror("Unable to set socket flags");
        exit(EXIT_FAILURE);
    }
    return ret;
}

void ArmClient::stop() {
    // std::cout << "ArmClient stop called" << std::endl;
    close(this->clientSocket);
}