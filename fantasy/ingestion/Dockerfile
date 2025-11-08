# Dockerfile assumes the build context is the parent directory (which contains 'ingestion' and 'common').

FROM python:3.11-slim

ARG POETRY_VERSION=2.2.0

ENV POETRY_NO_INTERACTION=1 \
    PYTHONUNBUFFERED=1

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

COPY common ./common
COPY ingestion/pyproject.toml ingestion/poetry.lock ./ingestion/

WORKDIR /app/ingestion

RUN touch README.md

RUN poetry install --no-root

COPY ingestion/src ./src

ENTRYPOINT ["poetry", "run", "python", "-m", "src.ingestion.ingestion_job"]
