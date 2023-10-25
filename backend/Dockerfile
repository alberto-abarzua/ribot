FROM python:3.11.6-alpine

WORKDIR /app


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV PYTHONPATH=/app/src


RUN pip install pdm==2.9.3

COPY ./pyproject.toml ./pyproject.toml
COPY ./pdm.lock ./pdm.lock

COPY . .


RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["pdm","run","start"]
