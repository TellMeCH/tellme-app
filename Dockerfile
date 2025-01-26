FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.4.2 \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/root/.local/bin:$PATH"

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    netcat-openbsd \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install --upgrade pip setuptools

RUN poetry install

COPY . /app/

EXPOSE 8080

ENV DJANGO_SETTINGS_MODULE=tell_me.settings

CMD ["daphne", "-b", "0.0.0.0", "-p", "8080", "tell_me.asgi:application"]