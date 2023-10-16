FROM debian:buster

RUN apt-get update && apt-get install -y \
    cmake \
    make \
    clang \
    llvm \
    build-essential \
    clang-format \
    clang-tools \
    valgrind \
    clang-tidy \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN chmod +x /app/entrypoint.sh

RUN rm -rf CMakeCache.txt CMakeFiles cmake_install.cmake Makefile

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["run"]
