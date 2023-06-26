FROM python:3.11.4

WORKDIR /app

RUN pip install pdm==2.7.4

ENV PYTHONPATH "${PYTHONPATH}:/app/src"

COPY pyproject.toml .
COPY pdm.lock .
RUN pdm install


COPY . .

CMD ["pdm", "run", "python", "./src/main.py"]

