FROM python:3.11-slim-buster

ARG EDITABLE_PACKAGES
ENV EDITABLE_PACKAGES=${EDITABLE_PACKAGES}

WORKDIR /app

# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential coreutils && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV PYTHONPATH=/app/src

RUN pip install --no-cache-dir pdm==2.10.3

COPY ./pyproject.toml ./pyproject.toml
COPY ./pdm.lock ./pdm.lock

COPY . .

RUN ls -la && sleep 5

RUN if [ "$EDITABLE_PACKAGES" = "true" ]; then \
        echo "Installing editable packages"; \
        pdm remove ribot-controller || true; \
        pdm remove ribot-controller --dev || true; \
        pdm add -e ./controller --dev; \
    else \
        echo "Installing non-editable packages"; \
        pdm remove ribot-controller --dev; \
        pdm add ribot-controller; \
    fi

RUN pdm install
RUN chmod +x ./entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["pdm","run","start"]

