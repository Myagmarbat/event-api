#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$(cd "$(dirname "$0")" && pwd)}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
COMPOSE_ENV_FILE="${COMPOSE_ENV_FILE:-/dev/null}"
SERVICE_NAME="${SERVICE_NAME:-api}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:80/health}"
HEALTH_RETRIES="${HEALTH_RETRIES:-30}"
HEALTH_SLEEP_SECONDS="${HEALTH_SLEEP_SECONDS:-3}"
TARGET_IMAGE="${1:-${IMAGE_TAG:-${IMAGE:-}}}"
PREVIOUS_IMAGE=""

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
      echo "Health check passed."
      return 0
    fi
    echo "Health check attempt ${attempt}/${HEALTH_RETRIES} failed."
    sleep "$HEALTH_SLEEP_SECONDS"
  done
  return 1
}

compose() {
  docker compose --env-file "$COMPOSE_ENV_FILE" -f "$COMPOSE_FILE" "$@"
}

rollback() {
  if [ -z "$PREVIOUS_IMAGE" ]; then
    echo "No previous image available for rollback."
    return 1
  fi

  echo "Rolling back to previous image: $PREVIOUS_IMAGE"

  if ! IMAGE="$PREVIOUS_IMAGE" compose up -d "$SERVICE_NAME"; then
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

if [ -z "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL must be provided to deploy.sh"
  exit 1
fi

if [ -z "$TARGET_IMAGE" ]; then
  echo "IMAGE_TAG (or IMAGE) must be provided to deploy.sh"
  exit 1
fi

echo "Deploying $TARGET_IMAGE to $SERVICE_NAME in $APP_DIR"
PREVIOUS_CONTAINER="$(compose ps -q "$SERVICE_NAME" 2>/dev/null || true)"
if [ -n "$PREVIOUS_CONTAINER" ]; then
  PREVIOUS_IMAGE="$(docker inspect --format '{{.Config.Image}}' "$PREVIOUS_CONTAINER" 2>/dev/null || true)"
fi

if [ -n "$PREVIOUS_IMAGE" ]; then
  echo "Previous image: $PREVIOUS_IMAGE"
else
  echo "No existing container found for rollback."
fi

if [ -n "${DO_API_TOKEN:-}" ]; then
  echo "$DO_API_TOKEN" | docker login registry.digitalocean.com -u doctl --password-stdin
fi

if IMAGE="$TARGET_IMAGE" compose pull "$SERVICE_NAME" &&
  IMAGE="$TARGET_IMAGE" compose up -d "$SERVICE_NAME" &&
  wait_for_health; then
  docker image prune -f >/dev/null 2>&1 || true
  echo "Deployment successful."
  exit 0
fi

echo "Deployment failed health checks. Attempting rollback..."
if rollback; then
  exit 1
fi

exit 1
