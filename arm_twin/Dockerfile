FROM debian:buster

RUN apt-get update && apt-get install -y \
    g++ \
    cmake \
    make

WORKDIR /app
COPY . .

RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
