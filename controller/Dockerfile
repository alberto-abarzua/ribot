FROM python:3.11.4

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir pdm==2.10.4

ENV PYTHONPATH "${PYTHONPATH}:/app/src"

COPY pyproject.toml .
COPY pdm.lock .

COPY . .

RUN pdm install



