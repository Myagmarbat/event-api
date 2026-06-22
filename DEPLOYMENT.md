# DigitalOcean deployment

This repository deploys automatically to a DigitalOcean Droplet when code lands on
`main`.

## Required GitHub configuration

Create a GitHub Environment named `production` and store these secrets there:

- `DOCR_REGISTRY` - for example `registry.digitalocean.com/my-registry`
- `DO_API_TOKEN` - DigitalOcean API token with registry access
- `SSH_HOST` - droplet hostname or IP
- `SSH_USER` - SSH user on the droplet
- `SSH_KEY` - private key for the SSH user
- `APP_DIR` - deployment directory on the droplet, for example `/opt/event-api`
- `DATABASE_URL` - optional if you want GitHub to manage it; otherwise keep
  `DATABASE_URL` only in the droplet `.env` file and do not add this secret

The workflow uses the `production` environment directly, so you can add required
reviewers there if you want manual approval before each deployment.

## Droplet prerequisites

Install these packages on the server before the first deployment:

- Docker Engine
- Docker Compose plugin (`docker compose`)
- `curl`
- `doctl` is **not** required on the droplet because the deploy script logs in
  to the registry with Docker using `DO_API_TOKEN`

## One-time bootstrap

1. Create the application directory:

   ```bash
   sudo mkdir -p /opt/event-api
   sudo chown -R "$USER":"$USER" /opt/event-api
   ```

2. Copy deployment artifacts from this repository to the server:

   ```bash
   scp docker-compose.yml deploy.sh your-user@your-host:/opt/event-api/
   ssh your-user@your-host 'chmod +x /opt/event-api/deploy.sh'
   ```

3. Create `/opt/event-api/.env` on the droplet:

   ```env
   DATABASE_URL=******host:25060/event_db?sslmode=require
   IMAGE=registry.digitalocean.com/my-registry/event-api:latest
   ```

   `docker-compose.yml` reads `DATABASE_URL` and `IMAGE` from this file. Future
   deployments only update the `IMAGE` value; the droplet remains the source of
   truth for `DATABASE_URL`.

## Continuous deployment flow

1. Push to `main`.
2. GitHub Actions builds the Docker image.
3. The workflow installs `doctl`, authenticates to DigitalOcean Container
   Registry, and pushes both `${GITHUB_SHA}` and `latest` tags.
4. The workflow opens an SSH session to the droplet and runs `deploy.sh`.
5. `deploy.sh` updates the `IMAGE` entry in `.env`, pulls the new image, restarts
   the `api` service with `docker compose`, and retries `curl http://127.0.0.1/health`.
6. If the health check never succeeds, `deploy.sh` restores the previous `.env`
   state, restarts the old container, and exits non-zero so the workflow fails.

## Notes

- Production deploys are serialized with the workflow concurrency guard
  `production-deploy`.
- The container runs `alembic upgrade head` before starting Uvicorn.
- Port `80` on the droplet maps to port `8000` inside the container.
