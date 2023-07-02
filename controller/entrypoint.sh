#!/bin/sh

# if $TEST is set, run tests
if [ "$TEST" = "true" ]; then
    echo "Running tests"
    pdm run test || exit 1
    exit 0
fi

if [ "$1" = "test" ]; then
    pdm run test || exit 1
fi

exec "$@"

