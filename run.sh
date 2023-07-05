#!/bin/bash

function get_ip() {
    echo $(hostname -I | awk '{print $1}')
}

case "$1" in
build)
    docker compose run --rm firmware build || exit 1
    ;;
build-esp)
    source .env
    CONTROLLER_SERVER_HOST=$(get_ip)
    export CONTROLLER_SERVER_PORT
    ./firmware/entrypoint_esp.sh || exit 1
    ;;
format)
    docker compose run --rm firmware format || exit 1
    docker compose run --rm controller pdm run format || exit 1
    ;;
lint)
    docker compose run --rm controller pdm run lint || exit 1
    ;;
test)
    # build firmware
    docker compose run --rm firmware build || exit 1

    docker compose up firmware -d
    # FOLLOW LOGS TO SEE WHEN FIRMWARE IS READY
    # start timestamp
    START_TIMESTAMP=$(date +%s)
    while ! docker compose logs firmware | grep "Hardware setup complete"; do
        sleep 1
        # timeout after 2 minute
        if [ $(($(date +%s) - $START_TIMESTAMP)) -gt 120 ]; then
            echo "Firmware failed to start"
            docker compose logs firmware
            docker compose down --remove-orphans
            exit 1
        fi
    done
    sleep 5
    docker compose logs firmware
    echo "Firmware is ready"
    docker compose run --rm --service-ports --use-aliases controller pdm run test
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ]; then
        echo "Tests passed"
    else
        echo "Tests failed"
        docker compose logs firmware
    fi
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
    docker compose run --rm --service-ports --use-aliases controller pdm run test
    EXIT_CODE=$?
    docker compose down --remove-orphans
    cd ..
    exit $EXIT_CODE

    ;;
valgrind)
    docker compose run --rm firmware valgrind
    ;;
gdb)
    docker compose run --rm firmware gdb
    ;;
*)
    docker compose up
    ;;
esac
