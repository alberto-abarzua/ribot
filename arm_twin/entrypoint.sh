#!/bin/sh

if [ "$RUN_TWIN_ON_HOST" = "true" ]; then
    echo "Running twin on host"

    cd /app
    rm ./app
    cmake .
    if ! make; then
        echo "Failed to build twin"
        exit 1
    fi
    ./app
else
    echo "Not running twin on host"
fi
