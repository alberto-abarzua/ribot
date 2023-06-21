cmake_minimum_required(VERSION 3.10)

project(ArmTwin)

set(CMAKE_CXX_STANDARD 20)

# Add your source files here
file(GLOB_RECURSE SOURCES "main.cpp" "components/*.cpp")

# include all directories in components/*/include/
file(GLOB INCLUDES "components/*/include/")

# Create an executable named 'app' from the source files
add_executable(app ${SOURCES})

# Specify the directories that the compiler should look in for include files
target_include_directories(app PRIVATE ${CMAKE_CURRENT_SOURCE_DIR} ${INCLUDES})
