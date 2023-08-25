FROM python:3.11.4


WORKDIR /app

# pythonenvbuffer

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1



RUN pip install pdm==2.8.2

COPY ./pyproject.toml ./pyproject.toml
COPY ./pdm.lock ./pdm.lock

RUN pdm install



COPY . .


CMD ["pdm", "run","src/main.py"]