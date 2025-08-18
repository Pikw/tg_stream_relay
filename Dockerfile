# Multi-stage build: base with Python + FFmpeg
FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends     ffmpeg curl ca-certificates tzdata     && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PYTHONUNBUFFERED=1     PYTHONDONTWRITEBYTECODE=1

# Default command (overridden in docker-compose)
ENTRYPOINT ["/entrypoint.sh"]
