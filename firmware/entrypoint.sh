#!/bin/sh

# Check if the first argument is "-c" and execute the remaining arguments
if [ "$1" = "-c" ]; then
    shift
    exec "$@"
fi

if [ "$RUN_TWIN_ON_HOST" = "true" ]; then
    echo "Running twin on host"

    case "$1" in
    build)
        echo "Building twin"
        cd /app || exit 1
        rm -f ./app
        cmake .
        if ! make; then
            echo "Failed to build twin"
            exit 1
        fi
        ;;
    format)
        echo "Formatting code"
        cd /app || exit 1
        find . \( -iname '*.cpp' -o -iname '*.h' \) -exec clang-format -i {} \;
        ;;

    *)
        echo "Building twin"
        cd /app || exit 1
        rm -f ./app
        cmake .
        if ! make; then
            echo "Failed to build twin"
            exit 1
        fi
        ./app
        ;;
    esac
else
    echo "Not running twin on host"
fi
