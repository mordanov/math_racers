FROM python:3.12-slim AS builder

RUN pip install uv

WORKDIR /build
COPY pyproject.toml .
RUN uv pip install --system --no-cache -r pyproject.toml

FROM python:3.12-slim AS runtime

ARG VERSION=dev
ENV VERSION=${VERSION}
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

RUN useradd --no-create-home --shell /bin/false appuser && \
    chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
