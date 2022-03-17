FROM python:3.10-bullseye
ENV LANG en_US.UTF-8
WORKDIR /code

RUN pip install poetry
COPY pyproject.toml poetry.lock /code/
RUN poetry install --no-interaction --no-ansi --no-dev

ENV FLASK_SKIP_DOTENV 1

COPY . /code

CMD poetry run flask run -p 80 -h 0.0.0.0
