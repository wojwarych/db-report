FROM python:3.13.5-slim AS base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN apt-get update -qy && apt-get install -qyy --no-install-recommends curl
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app
COPY uv.lock pyproject.toml .python-version README.md /app
RUN uv sync --locked

COPY ./src /app/src/
WORKDIR /app/src
EXPOSE 8000
ENTRYPOINT ["uv", "run", "main.py"]
