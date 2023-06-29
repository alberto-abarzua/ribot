#!/bin/bash

docker run --rm \
    -v $PWD/firmware:/project \
    -w /project \
    -e CONTROLLER_SERVER_PORT \
    -e CONTROLLER_SERVER_HOST \
    -e WIFI_SSID \
    -e WIFI_PASSWORD \
    espressif/idf:release-v5.0 /bin/bash -c "\
       echo \
       \$CONTROLLER_SERVER_PORT \
       \$CONTROLLER_SERVER_HOST \
       \$WIFI_SSID \
       \$WIFI_PASSWORD; \
       idf.py build"
