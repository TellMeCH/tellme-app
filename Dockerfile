FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/root/.local/bin:$PATH"

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    netcat-openbsd \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /app

COPY pyproject.toml uv.lock* /app/

RUN uv sync --frozen --no-cache

COPY . /app/

EXPOSE 8080

ENV DJANGO_SETTINGS_MODULE=tellme.settings

CMD ["uv", "run", "daphne", "-b", "0.0.0.0", "-p", "8080", "tellme.asgi:application"]