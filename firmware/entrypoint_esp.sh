#!/bin/bash

docker run --rm \
    -v $PWD/firmware:/project \
    -w /project \
    -e CONTROLLER_SERVER_PORT \
    -e CONTROLLER_SERVER_HOST \
    -e WIFI_SSID \
    -e WIFI_PASSWORD \
    espressif/idf:release-v5.0 /bin/bash -c \
    "export CONTROLLER_SERVER_PORT=\$CONTROLLER_SERVER_PORT; \
    export CONTROLLER_SERVER_HOST=\$CONTROLLER_SERVER_HOST; \
    export WIFI_SSID=\$WIFI_SSID;\
    export WIFI_PASSWORD=\$WIFI_PASSWORD; \
       echo \
       \$CONTROLLER_SERVER_PORT \
       \$CONTROLLER_SERVER_HOST \
       \$WIFI_SSID \
       \$WIFI_PASSWORD; \
       idf.py build"
