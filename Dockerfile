FROM ubuntu:18.04
ENV LANG en_US.UTF-8
RUN apt update

ARG RUNMODE='deploy'
ENV RUNMODE=$RUNMODE

# install python3.8
RUN apt install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt install -y python3-pip python3.8-dev 

# install as
RUN apt install -y gcc-arm-linux-gnueabi binutils-avr

# install gdb
RUN apt install -y gdb-multiarch gdb-avr

# install qemu
RUN apt install -y qemu

# install requirements for tests
RUN apt install -y xvfb firefox wget

ADD . /code
WORKDIR /code
RUN python3.8 -m pip install -r src/requirements.txt
CMD ./scripts/local_start.sh $RUNMODE
