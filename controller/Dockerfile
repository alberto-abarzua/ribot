FROM python:3.11.4

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install pdm==2.8.2

ENV PYTHONPATH "${PYTHONPATH}:/app/src"

COPY pyproject.toml .
COPY pdm.lock .
RUN pdm install


COPY . .

