FROM python:3.10-bullseye
ENV LANG en_US.UTF-8
WORKDIR /code

RUN pip install poetry
COPY pyproject.toml poetry.lock /code/
RUN poetry install --no-interaction --no-ansi --no-dev

ARG RUNMODE='test'
ENV RUNMODE=$RUNMODE

COPY . /code

CMD poetry run python -m app
