FROM python:3.10-bullseye
ENV LANG en_US.UTF-8
WORKDIR /code

RUN pip install poetry
RUN pip uninstall dotenv
RUN pip uninstall python-dotenv
RUN pip install python-dotenv
COPY pyproject.toml poetry.lock /code/
RUN poetry install --no-interaction --no-ansi --no-dev

RUN apt-get update && apt-get install -y gcc gdb

COPY . /code

CMD poetry run python -m runner
