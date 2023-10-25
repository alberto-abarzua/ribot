#!/bin/sh


echo "Installing dependecies (required for editable mode)"
pdm install --dev


exec "$@"
