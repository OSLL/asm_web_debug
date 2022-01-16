FROM python:3.10-bullseye
ENV LANG en_US.UTF-8

RUN pip install poetry
RUN apt-get update && apt-get install -y gcc gdb

COPY pyproject.toml poetry.lock /code/
WORKDIR /code
RUN poetry install --no-interaction --no-ansi

COPY . /code

CMD poetry run python -m runner
