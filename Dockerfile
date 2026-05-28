FROM python:3.9-slim AS builder

WORKDIR /app
RUN pip install poetry
COPY pyproject.toml ./
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

FROM python:3.9-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r lineage && useradd -r -g lineage lineage

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . /app

RUN chown -R lineage:lineage /app
USER lineage

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "lineage_platform.api.app:app", "--host", "0.0.0.0", "--port", "8000"]