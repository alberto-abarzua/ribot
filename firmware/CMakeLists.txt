cmake_minimum_required(VERSION 3.13)




set(WIFI_SSID $ENV{WIFI_SSID})
set(WIFI_PASSWORD $ENV{WIFI_PASSWORD})
set(CONTROLLER_SERVER_HOST $ENV{CONTROLLER_SERVER_HOST})
set(CONTROLLER_SERVER_PORT $ENV{CONTROLLER_SERVER_PORT})




# Use the CMake variable in your code
configure_file(config.h.in ${CMAKE_BINARY_DIR}/config.h)

include_directories(${CMAKE_BINARY_DIR})

if(DEFINED ENV{IDF_PATH})
    include($ENV{IDF_PATH}/tools/cmake/project.cmake)
    add_compile_definitions(ESP_PLATFORM)
    project(ArmTwin)
    list(APPEND EXTRA_COMPONENT_DIRS "$ENV{IDF_PATH}/tools/mocks/freertos/")
    list(APPEND EXTRA_COMPONENT_DIRS "./components")
    set(COMPONENTS main arm_client commands controller)
    set(SRCS "main.cpp" )
else()
    project(ArmTwin)
    set(CMAKE_CXX_STANDARD 20)
    # Set compiler warnings
    set(CMAKE_C_COMPILER "/usr/bin/clang")
    set(CMAKE_CXX_COMPILER "/usr/bin/clang++")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra -pedantic -Werror")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -pedantic -Werror")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address -fno-omit-frame-pointer -g -fno-sanitize-recover=all")
    set(CMAKE_CXX_CLANG_TIDY "clang-tidy;-checks=google-runtime-int")
    # Add your source files here
    file(GLOB_RECURSE SOURCES "main/main.cpp" "components/*.cpp")

    # include all directories in components/*/include/
    file(GLOB INCLUDES "components/*/include/")

    # Create an executable named 'app' from the source files
    find_package(Threads REQUIRED)
    add_executable(app ${SOURCES})
    target_link_libraries(app Threads::Threads)

    # Specify the directories that the compiler should look in for include files
    target_include_directories(app PRIVATE ${CMAKE_CURRENT_SOURCE_DIR} ${INCLUDES})
endif()
