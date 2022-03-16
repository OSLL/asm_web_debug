FROM debian:bullseye
ENV LANG en_US.UTF-8

RUN apt-get update && apt-get install -y gcc gdb
