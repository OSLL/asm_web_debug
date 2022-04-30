FROM python:3.10-bullseye
ENV LANG en_US.UTF-8
WORKDIR /code

RUN pip install poetry
COPY pyproject.toml poetry.lock /code/
RUN poetry install --no-interaction --no-ansi --no-dev

RUN apt-get update && apt-get install -y gcc gdb gcc-avr gdb-avr avr-libc

COPY . /code

CMD poetry run python -m runner
