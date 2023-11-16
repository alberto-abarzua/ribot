#include "httplib.h"
#include <iostream>
#include <stdexcept>
#include <string>

// Constants for default and additional port numbers
const int DefaultPort = 80;
const int MaxPort = 65535; // Maximum valid port number

int main() {
  httplib::Server svr;

  svr.Get("/", [](const httplib::Request &req, httplib::Response &res) {
    auto path = req.get_header_value("X-Original-URI");

    // Default port number
    int serviceNum = DefaultPort;

    // Check if the path is valid for extraction
    if (path.size() >= 3 && path[1] == 's' && isdigit(path[2])) {
      try {
        // Extract service number and add offset
        int extractedNum = std::stoi(path.substr(2));
        serviceNum = extractedNum;

        // Validate the resulting port number
        if (serviceNum < 0 || serviceNum > MaxPort) {
          throw std::out_of_range("Invalid port number");
        }
      } catch (const std::exception &e) {
        // Handle any exceptions
        std::cerr << "Error processing path: " << e.what() << std::endl;
        res.status = 400; // Bad Request
        res.set_content("Invalid path format or port number", "text/plain");
        return;
      }
    }

    res.set_header("X-Target-Port", std::to_string(serviceNum));
    res.set_content("Port number calculated", "text/plain");
  });

  // Start the server on port 3220
  std::cout << "Starting server on port 3320..." << std::endl;
  svr.listen("0.0.0.0", 3320);

  return 0;
}
