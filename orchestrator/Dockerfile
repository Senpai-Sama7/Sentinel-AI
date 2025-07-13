# orchestrator/Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-root

FROM python:3.11-slim
WORKDIR /app
RUN addgroup --system app && adduser --system --group app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY ./orchestrator /app/orchestrator
USER app
EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "orchestrator.main:app", "--bind", "0.0.0.0:8000"]