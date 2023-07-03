#!/bin/bash

function get_ip() {
    echo $(hostname -I | awk '{print $1}')
}

case "$1" in
build)
    docker compose run firmware build || exit 1
    ;;
build-esp)
    source .env
    CONTROLLER_SERVER_HOST=$(get_ip)
    export CONTROLLER_SERVER_PORT
    ./firmware/entrypoint_esp.sh || exit 1
    ;;
format)
    docker compose run firmware format || exit 1
    docker compose run controller pdm run format || exit 1
    ;;
lint)
    docker compose run controller pdm run lint || exit 1
    ;;
test)
    docker compose up firmware -d
    # FOLLOW LOGS TO SEE WHEN FIRMWARE IS READY
    while ! docker compose logs firmware | grep "Starting controller"; do
        sleep 1
    done
    docker compose logs firmware
    echo "Firmware is ready"
    docker compose run --service-ports --use-aliases controller pdm run test
    EXIT_CODE=$?

    docker compose down --remove-orphans
    exit $EXIT_CODE
    ;;
test-esp)
    source .env
    CONTROLLER_SERVER_HOST=$(get_ip)
    export CONTROLLER_SERVER_PORT
    echo "Requires idf.py to be installed and environment variables to be set"
    if [ -z "$IDF_PATH" ]; then
        echo "IDF_PATH is not set"
        exit 1
    fi
    cd firmware
    rm -rf build
    idf.py build flash || exit 1
    docker compose run --service-ports --use-aliases controller pdm run test
    EXIT_CODE=$?
    docker compose down --remove-orphans
    cd ..
    exit $EXIT_CODE

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
