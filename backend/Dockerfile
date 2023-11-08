FROM python:3.11-slim-buster

WORKDIR /app

# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV PYTHONPATH=/app/src


RUN pip install --no-cache-dir pdm==2.10

COPY ./pyproject.toml ./pyproject.toml
COPY ./pdm.lock ./pdm.lock


COPY . .


RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["pdm","run","start"]
