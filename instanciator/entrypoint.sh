#!/bin/sh


# check if BACKEND_UPDATE_RIBOT_CONTROLLER is set to 'true'
if [ "$BACKEND_UPDATE_RIBOT_CONTROLLER" = "true" ]; then
    
    echo "Updating ribot-controller to latest"
    echo "Updating ribot-controller to latest"
    pdm update ribot-controller
fi


exec "$@"
