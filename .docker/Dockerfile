FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for MySQL client
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
 && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
RUN pip install --upgrade pip && pip install .

COPY cli ./cli
RUN pip install -e .

# Create non-root user
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

USER appuser

ENTRYPOINT ["dealer-report"]
CMD ["--help"]
