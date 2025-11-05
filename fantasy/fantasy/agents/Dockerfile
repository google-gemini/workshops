# Dockerfile assumes the build context is the parent directory (which contains 'agents' and 'common').

FROM python:3.11-slim AS cert-extractor

RUN pip install certifi
RUN cp $(python -c "import certifi; print(certifi.where())") /tmp/cacert.pem

FROM python:3.11-slim

ARG PORT=5000
ARG POETRY_VERSION=2.2.0

EXPOSE ${PORT}

ENV POETRY_NO_INTERACTION=1 \
    PYTHONUNBUFFERED=1

RUN pip install "poetry==${POETRY_VERSION}"

COPY --from=cert-extractor /tmp/cacert.pem /usr/local/share/ca-certificates/cacert.pem
ENV SSL_CERT_FILE=/usr/local/share/ca-certificates/cacert.pem

WORKDIR /app

COPY common ./common
COPY agents/pyproject.toml agents/poetry.lock ./agents/

WORKDIR /app/agents

RUN touch README.md
RUN poetry install --no-root

COPY agents/src ./src
