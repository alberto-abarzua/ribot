#!/bin/bash

function get_ip() {
    echo $(hostname -I | awk '{print $1}')
}

case "$1" in
build)
    docker compose run firmware build
    ;;
build-esp)
    source .env
    CONTROLLER_SERVER_HOST=$(get_ip)
    export CONTROLLER_SERVER_PORT
    ./firmware/entrypoint_esp.sh
    ;;
format)
    docker compose run firmware format
    docker compose run controller pdm run format
    ;;
test)
    docker compose up firmware -d
    TEST=true docker compose up controller
    docker compose down --remove-orphans
    ;;
test-esp)
    source .env
    CONTROLLER_SERVER_HOST=$(get_ip)
    # export CONTROLLER_SERVER_HOST
    export CONTROLLER_SERVER_PORT
    echo "Requires idf.py to be installed and environment variables to be set"
    # check if IDF_PATH IS SET
    if [ -z "$IDF_PATH" ]; then
        echo "IDF_PATH is not set"
        exit 1
    fi
    cd firmware
    # remove build directory
    rm -rf build
    idf.py build flash || exit 1
    TEST=true docker compose up controller
    docker compose down --remove-orphans
    cd ..
    ;;
valgrind)
    docker compose run firmware valgrind
    ;;
gdb)
    docker compose run firmware gdb
    ;;
*)
    docker compose up
    ;;
esac
