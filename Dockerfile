FROM ubuntu:18.04
ENV LANG en_US.UTF-8
RUN apt-get update
RUN apt-get install -y python3-dev python3-pip build-essential
ADD . /code
WORKDIR /code
RUN python3 -m pip install -r src/requirements.txt
CMD ./scripts/local_start.sh
