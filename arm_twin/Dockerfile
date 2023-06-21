FROM debian:buster

RUN apt-get update && apt-get install -y \
    g++ \
    cmake \
    make

WORKDIR /app

COPY . .

RUN cmake .
RUN make

CMD ["./app"]
