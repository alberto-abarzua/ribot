

#include "arm_client.h"

ArmClient::ArmClient() {}

ArmClient::~ArmClient() {}

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

    s = getaddrinfo(CONTROLLER_SERVER_HOST,
                    std::to_string(CONTROLLER_SERVER_PORT).c_str(), &hints,
                    &res);
    if (s != 0) {
        return -1;
    }

    for (rp = res; rp != NULL; rp = rp->ai_next) {
        this->clientSocket =
            socket(rp->ai_family, rp->ai_socktype, rp->ai_protocol);
        if (this->clientSocket == -1) {
            continue;
        }
        if (connect(this->clientSocket, rp->ai_addr, rp->ai_addrlen) != -1) {
            break;  // success
        }

        close(this->clientSocket);
        this->clientSocket =
            -1;  // invalidate the socket descriptor after closing it
    }

    if (this->clientSocket == -1) {  // No address succeeded
        std::cerr << "Could not connect to host -> " << CONTROLLER_SERVER_HOST
                  << "\n";
        return -1;
    }

    freeaddrinfo(res);  // No longer needed

    return 0;
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
int ArmClient::send_message(Message *msg) {
    char *message_bytes = new char[msg->get_size()];
    msg->get_bytes(message_bytes);
    int ret = send(this->clientSocket, message_bytes, msg->get_size(), 0);
    if (ret == -1) {
        std::cout << "Error sending message\n";
    }
    delete[] message_bytes;
    return ret;
}

int ArmClient::receive_message(Message **msg_loc) {
    char buffer[1024] = {0};

    int result = read(this->clientSocket, buffer, Message::HEADER_SIZE);
    if (result < 0) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return 0;
        } else {
            return -1;
        }
    }
    if (result!= Message::HEADER_SIZE) {
        return -1;
    }
    char op;
    int32_t code, num_args;
    int ret = Message::parse_headers(buffer, &op, &code, &num_args);
    if (ret == -1) {
        return -1;
    }
    int32_t size_args = sizeof(float) * num_args;
    if (size_args > 0) {
        result =
            read(this->clientSocket, buffer + Message::HEADER_SIZE, size_args);
        if (result < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                return 0;
            } else {
                return -1;
            }
        }
    }
    *msg_loc = new Message(buffer);
    return 1;
}

void ArmClient::stop() { close(this->clientSocket); }