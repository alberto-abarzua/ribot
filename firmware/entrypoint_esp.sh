#!/bin/bash

rm -rf $PWD/firmware/build 

docker run --rm \
    -v $PWD/firmware:/project \
    -w /project \
    -e ESP_CONTROLLER_SERVER_HOST \
    -e ESP_CONTROLLER_SERVER_PORT \
    -e ESP_WIFI_SSID \
    -e ESP_WIFI_PASSWORD \
    espressif/idf:release-v5.0 /bin/bash -c "\
       echo \
       \$ESP_CONTROLLER_SERVER_PORT \
       \$ESP_CONTROLLER_SERVER_HOST \
       \$ESP_WIFI_SSID \
       \$ESP_WIFI_PASSWORD; \
       idf.py build"
