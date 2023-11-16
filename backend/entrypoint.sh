#!/bin/sh


# check if BACKEND_UPDATE_RIBOT_CONTROLLER is set to 'true'
# if [ "$EDITABLE_PACKAGES" = "true" ]; then
#     pdm remove ribot-controller || true
#     pdm add -e ./controller --dev
#     pdm install
# fi


exec "$@"
