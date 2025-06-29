FROM python:3.13.5-slim AS base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local' \
    POETRY_VERSION=2.1.3

RUN apt-get update -qy && apt-get install -qyy --no-install-recommends curl
RUN curl -sSl https://install.python-poetry.org | python3 -

WORKDIR /app
COPY poetry.lock pyproject.toml README.md /app
RUN poetry install --no-interaction --no-ansi --no-root

COPY ./src /app/
EXPOSE 8000
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
