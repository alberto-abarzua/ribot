

#include "arm_client.h"

ArmClient::ArmClient() {}

ArmClient::~ArmClient() {}

#include "messages.h"
ArmClientCode ArmClient::create_socket() {
    struct addrinfo hints, *res, *rp;
    int s;

    memset(&hints, 0, sizeof(struct addrinfo));
    hints.ai_family = AF_UNSPEC;      // Allow IPv4 or IPv6
    hints.ai_socktype = SOCK_STREAM;  // TCP socket

    s = getaddrinfo(CONTROLLER_SERVER_HOST,
                    std::to_string(CONTROLLER_SERVER_PORT).c_str(), &hints,
                    &res);
    if (s != 0) {
        std::cerr << "getaddrinfo error: " << s << CONTROLLER_SERVER_HOST
                  << "\n";
        return ArmClientCode::ADDR_INFO_ERROR;
    }

    for (rp = res; rp != NULL; rp = rp->ai_next) {
        this->clientSocket =
            socket(rp->ai_family, rp->ai_socktype, rp->ai_protocol);
        if (this->clientSocket == -1) {
            perror("socket creation failed");
            continue;
        }
        break;
    }

    freeaddrinfo(res);

    if (this->clientSocket == -1) {  // No address succeeded
        return ArmClientCode::SOCKET_CREATION_ERROR;
    } else {
        return ArmClientCode::SUCCESS;
    }
}

ArmClientCode ArmClient::attempt_connection() {
    struct addrinfo hints, *res, *rp;
    int s;

    memset(&hints, 0, sizeof(struct addrinfo));
    hints.ai_family = AF_UNSPEC;      // Allow IPv4 or IPv6
    hints.ai_socktype = SOCK_STREAM;  // TCP socket

    s = getaddrinfo(CONTROLLER_SERVER_HOST,
                    std::to_string(CONTROLLER_SERVER_PORT).c_str(), &hints,
                    &res);
    if (s != 0) {
        std::cerr << "getaddrinfo error: " << s << "when connecting to"
                  << CONTROLLER_SERVER_HOST << ":" << CONTROLLER_SERVER_PORT
                  << "\n";
        return ArmClientCode::ADDR_INFO_ERROR;
    }

    for (rp = res; rp != NULL; rp = rp->ai_next) {
        if (connect(this->clientSocket, rp->ai_addr, rp->ai_addrlen) != -1) {
            break;  // success
        }

        perror("connection attempt failed");
    }
    freeaddrinfo(res);

    if (rp == NULL) {  // No address succeeded
        std::cerr << "Could not connect to host -> " << CONTROLLER_SERVER_HOST
                  << "\n";
        return ArmClientCode::CONNECTION_ERROR;
    } else {
        return ArmClientCode::SUCCESS;
    }
}

ArmClientCode ArmClient::setup() {
    if (!this->socket_created) {
        ArmClientCode socket_creation_result = this->create_socket();
        if (socket_creation_result == ArmClientCode::SUCCESS) {
            this->socket_created = true;
        } else {
            return socket_creation_result;
        }
    }

    if (this->clientSocket == -1) {
        std::cerr << "Invalid socket\n";
        return ArmClientCode::SOCKET_CREATION_ERROR;
    }
    ArmClientCode attempt_connection_result = this->attempt_connection();

    if (attempt_connection_result != ArmClientCode::SUCCESS) {
        return attempt_connection_result;
    }

    // Set the socket to be non-blocking
    int flags = fcntl(this->clientSocket, F_GETFL, 0);
    if (flags == -1) {
        perror("Unable to get socket flags");
        return ArmClientCode::SOCKET_CREATION_ERROR;
    }

    flags |= O_NONBLOCK;
    if (fcntl(this->clientSocket, F_SETFL, flags) == -1) {
        perror("Unable to set socket flags");
        return ArmClientCode::SOCKET_CREATION_ERROR;
    }

    return ArmClientCode::SUCCESS;
}
ArmClientCode ArmClient::send_message(Message *msg) {
    char *message_bytes = new char[msg->get_size()];
    msg->get_bytes(message_bytes);
    int ret = send(this->clientSocket, message_bytes, msg->get_size(), 0);
    delete[] message_bytes;
    if (ret == -1) {
        return ArmClientCode::FAILED_TO_SEND;
    }
    return ArmClientCode::SUCCESS;
}

ArmClientCode ArmClient::receive_message(Message **msg_loc) {
    char buffer[1024] = {0};

    int result = read(this->clientSocket, buffer, Message::HEADER_SIZE);
    if (result < 0) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return ArmClientCode::NO_NEW_DATA;
        } else {
            return ArmClientCode::FAILED_TO_RECEIVE;
        }
    }
    if (result != Message::HEADER_SIZE) {
        return ArmClientCode::FAILED_TO_RECEIVE_HEADER;
    }
    MessageOp op;
    int32_t code, num_args;
    Message::parse_headers(buffer, &op, &code, &num_args);
    int32_t size_args = sizeof(float) * num_args;
    if (size_args > 0) {
        result =
            read(this->clientSocket, buffer + Message::HEADER_SIZE, size_args);
        if (result < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                return ArmClientCode::NO_NEW_DATA;
            } else {
                return ArmClientCode::FAILED_TO_RECEIVE_ARGS;
            }
        }
    }
    *msg_loc = new Message(buffer);
    return ArmClientCode::SUCCESS;
}

void ArmClient::stop() { close(this->clientSocket); }