FROM python:3.10-bullseye
ENV LANG en_US.UTF-8

RUN pip install poetry

ARG RUNMODE='test'
ENV RUNMODE=$RUNMODE

COPY pyproject.toml poetry.lock /code/
WORKDIR /code
RUN poetry install --no-interaction --no-ansi

COPY . /code

CMD poetry run python -m app