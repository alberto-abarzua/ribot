# Use an official C++ runtime as a parent image
FROM gcc:latest

# Set the working directory in the container
WORKDIR /usr/src/router

# Install git
RUN apt-get update && apt-get install -y git

# Clone the cpp-httplib repository
RUN git clone https://github.com/yhirose/cpp-httplib.git

COPY . .

# Include the cpp-httplib header in the include path
RUN mv cpp-httplib/httplib.h /usr/local/include


# Compile the application
RUN g++ -o router main.cpp

# Run the application when the container launches
CMD ["./router"]

