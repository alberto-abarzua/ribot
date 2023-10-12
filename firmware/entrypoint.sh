#!/bin/sh

# Check if the first argument is "-c" and execute the remaining arguments
if [ "$1" = "-c" ]; then
    shift
    exec "$@"
fi


build() {
    echo "Building twin"
    cd /app || exit 1
    rm -f ./app
    cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=1 .
    cmake --build . --clean-first
    if ! make; then
        echo "Failed to build twin"
        exit 1
    fi
    # move /app/compile_commands.json to /app/output
}

case "$1" in
build)
    build
    ;;
format)
    echo "Formatting code"
    cd /app || exit 1
    find . \( -iname '*.cpp' -o -iname '*.h' \) -exec clang-format -i {} \;
    ;;
valgrind)
    build
    echo "Running twin with valgrind"
    cd /app || exit 1
    valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes --verbose ./app
    ;;
gdb)
    build
    echo "Running twin with gdb"
    cd /app || exit 1
    gdb ./app
    ;;

run)
    build
    ./app
    ;;
help)
    echo "Available commands:"
    echo "build - build twin"
    echo "format - format code"
    echo "valgrind - run twin with valgrind"
    echo "gdb - run twin with gdb"
    echo "run - run twin"
    echo "help - print this help message"
    ;;
*)
    exec "$@"
    ;;
esac

