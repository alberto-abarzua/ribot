#!/bin/sh

# if $TEST is set, run tests
echo "TEST: $TEST"
if [ "$TEST" = "true" ]; then
    echo "Running tests"
    pdm run test
    exit 0
fi

exec "$@"

