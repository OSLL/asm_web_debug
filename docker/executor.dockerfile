FROM debian:bullseye
ENV LANG en_US.UTF-8

RUN apt-get update
RUN apt-get install -y gdbserver
