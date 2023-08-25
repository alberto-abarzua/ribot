FROM python:3.11.4

WORKDIR /app

RUN pip install pdm==2.8.2

ENV PYTHONPATH "${PYTHONPATH}:/app/src"

COPY pyproject.toml .
COPY pdm.lock .
RUN pdm install


COPY . .

RUN chmod +x entrypoint.sh

ENTRYPOINT [ "/app/entrypoint.sh" ]

CMD ["pdm", "run", "start"]



