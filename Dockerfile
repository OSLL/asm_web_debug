FROM python:3.9
ENV LC_ALL en_US.UTF-8

ARG RUNMODE='deploy'
ENV RUNMODE=$RUNMODE

RUN apt-get update && apt-get install -y gcc gdb-multiarch qemu-user
RUN python3.9 -m pip install pipenv

ADD . /code
WORKDIR /code
RUN pipenv sync

CMD ./scripts/local_start.sh $RUNMODE
