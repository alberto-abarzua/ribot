FROM debian:buster

RUN apt-get update && apt-get install -y \
    cmake \
    make \
    clang \
    llvm \
    build-essential \
    clang-format \
    clang-tools \
    clang-tidy \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
