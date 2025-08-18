#!/usr/bin/env bash
set -euo pipefail

# Allow services to discover Redis URL through env
if [[ -n "${REDIS_HOST:-}" ]]; then
  if [[ -n "${REDIS_PASSWORD:-}" ]]; then
    export REDIS_URL="redis://:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT:-6379}/${REDIS_DB:-0}"
  else
    export REDIS_URL="redis://${REDIS_HOST}:${REDIS_PORT:-6379}/${REDIS_DB:-0}"
  fi
fi

exec "$@"
