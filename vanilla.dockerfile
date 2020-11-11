FROM python:3.8

RUN apt-get update \
 && apt-get install nano \
 && pip install pip poetry --upgrade

WORKDIR "/root/pipper/"

COPY pyproject.toml /root/pipper/pyproject.toml
COPY poetry.lock /root/pipper/poetry.lock

RUN poetry config virtualenvs.create false \
 && poetry install
