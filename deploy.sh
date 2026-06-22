#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$(cd "$(dirname "$0")" && pwd)}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
SERVICE_NAME="${SERVICE_NAME:-api}"
ENV_FILE="${ENV_FILE:-.env}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1/health}"
HEALTH_RETRIES="${HEALTH_RETRIES:-20}"
HEALTH_SLEEP_SECONDS="${HEALTH_SLEEP_SECONDS:-3}"
TARGET_IMAGE="${IMAGE_TAG:-${IMAGE:-}}"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1"
    exit 1
  fi
}

wait_for_health() {
  local attempt
  for attempt in $(seq 1 "$HEALTH_RETRIES"); do
    if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
      return 0
    fi
    sleep "$HEALTH_SLEEP_SECONDS"
  done
  return 1
}

set_env_var() {
  local key="$1"
  local value="$2"
  local file="$3"

  if grep -q "^${key}=" "$file"; then
    sed -i "s|^${key}=.*|${key}=${value}|" "$file"
  else
    printf '%s=%s\n' "$key" "$value" >>"$file"
  fi
}

rollback() {
  if [ ! -f "${ENV_FILE}.rollback" ]; then
    echo "No rollback state available."
    return 1
  fi

  echo "Rolling back to previous deployment state..."
  mv "${ENV_FILE}.rollback" "$ENV_FILE"

  if ! docker compose -f "$COMPOSE_FILE" up -d "$SERVICE_NAME"; then
    echo "Rollback restart failed."
    return 1
  fi

  if wait_for_health; then
    echo "Rollback succeeded."
    return 0
  fi

  echo "Rollback health check failed."
  return 1
}

require_command docker
require_command curl

cd "$APP_DIR"

if ! docker compose version >/dev/null 2>&1; then
  echo "Missing required command: docker compose"
  exit 1
fi

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "Missing compose file: $APP_DIR/$COMPOSE_FILE"
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing environment file: $APP_DIR/$ENV_FILE"
  exit 1
fi

if ! grep -q '^DATABASE_URL=' "$ENV_FILE"; then
  echo "DATABASE_URL must be defined in $ENV_FILE"
  exit 1
fi

if [ -z "$TARGET_IMAGE" ]; then
  echo "IMAGE_TAG (or IMAGE) must be provided to deploy.sh"
  exit 1
fi

if [ -n "${DO_API_TOKEN:-}" ]; then
  echo "$DO_API_TOKEN" | docker login registry.digitalocean.com -u doctl --password-stdin
fi

cp "$ENV_FILE" "${ENV_FILE}.rollback"
set_env_var IMAGE "$TARGET_IMAGE" "$ENV_FILE"

if docker compose -f "$COMPOSE_FILE" pull "$SERVICE_NAME" &&
  docker compose -f "$COMPOSE_FILE" up -d "$SERVICE_NAME" &&
  wait_for_health; then
  rm -f "${ENV_FILE}.rollback"
  docker image prune -f >/dev/null 2>&1 || true
  echo "Deployment successful."
  exit 0
fi

echo "Deployment failed health checks. Attempting rollback..."
if rollback; then
  exit 1
fi

exit 1
