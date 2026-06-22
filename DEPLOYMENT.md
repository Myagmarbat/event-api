# DigitalOcean deployment

This repository deploys automatically through stage and production DigitalOcean
Droplets when code lands on `main`.

## Required GitHub configuration

Create these GitHub Actions repository secrets:

- `DOCR_REGISTRY` - for example `registry.digitalocean.com/my-registry`
- `DO_API_TOKEN` - DigitalOcean API token with registry access

Create two GitHub Environments named `stage` and `production`. Store these
environment secrets in both environments, with values for the matching Droplet:

- `SSH_HOST` - droplet hostname or IP
- `SSH_USER` - SSH user on the droplet
- `SSH_KEY` - private key for the SSH user, use a separate key per environment
- `APP_DIR` - deployment directory on the droplet, for example `/opt/event-api`
- `DATABASE_URL` - Managed PostgreSQL connection string for that environment,
  for example `postgresql://...:25060/defaultdb?sslmode=require`
- `DO_DB_CA_CERT` - DigitalOcean Managed PostgreSQL CA certificate PEM text

Store this additional environment secret in `stage`:

- `STAGE_BASE_URL` - public base URL for the stage API, for example
  `https://stage-api.example.com`

Add required reviewers to the `production` environment to create the manual
approval gate before production deployment.

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

3. Do not create `/opt/event-api/.env`. The deploy workflow copies
   `docker-compose.yml` and `deploy.sh` to the Droplet, then passes
   `DATABASE_URL` and `DO_DB_CA_CERT` from GitHub Environment secrets directly
   to `deploy.sh`. `docker-compose.yml` passes both values to the container as
   runtime environment variables. Stage and production should use separate
   `DATABASE_URL` values.

## Continuous deployment flow

1. Open a pull request.
2. GitHub Actions runs Ruff/Flake8, unit tests, and a Docker image build.
3. Merge to `main`.
4. GitHub Actions builds the Docker image.
5. The workflow installs `doctl`, authenticates to DigitalOcean Container
   Registry, and pushes both `${GITHUB_SHA}` and `latest` tags.
6. The workflow deploys the image to the stage Droplet.
7. GitHub Actions runs integration checks against `STAGE_BASE_URL`.
8. The `production` environment approval gate pauses the workflow.
9. After approval, the workflow deploys the same image SHA to the production
   Droplet.
10. The workflow syncs `docker-compose.yml` and `deploy.sh` to the Droplet,
    passes GitHub Environment secrets over SSH as runtime environment
    variables, then `deploy.sh` verifies them, pulls the new image, restarts
    the `api` service with `docker compose`, and retries
    `curl http://127.0.0.1/health`.
11. If the health check never succeeds, `deploy.sh` restarts the previous image
    and exits non-zero so the workflow fails.

## Notes

- Main-branch deploys are serialized with the workflow concurrency guard
  `main-deploy`.
- The container runs `alembic upgrade head` before starting Uvicorn.
- Port `80` on the droplet maps to port `8000` inside the container.
