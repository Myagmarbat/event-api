# GitHub Actions Workflow Setup Guide

## Overview

This repository uses GitHub Actions for pull request checks, Docker image
verification, and staged DigitalOcean deployments.

## Workflows

### 1. **test.yml** - PR Checks
- **Trigger:** Pull requests and pushes to main
- **What it does:**
  - Runs Ruff
  - Runs Flake8
  - Runs unit tests in `tests/unit/`
- **No secrets required**

### 2. **build.yml** - Docker Image Build
- **Trigger:** Pull requests and pushes to main
- **What it does:**
  - Sets up Docker Buildx
  - Builds Docker image
  - Tags with commit SHA
- **No secrets required** because it does not push

### 3. **deploy.yml** - Stage and Production Deployment
- **Trigger:** Pushes to main and manual `workflow_dispatch`
- **What it does:**
  1. Builds and pushes Docker image to DigitalOcean Container Registry
  2. Deploys the image SHA to the stage Droplet
  3. Runs integration checks against the stage URL
  4. Waits for GitHub Environment approval on `production`
  5. Deploys the same image SHA to the production Droplet
- **Secrets required:**
  - Repository: `DOCR_REGISTRY`, `DO_API_TOKEN`
  - `stage` environment: `SSH_HOST`, `SSH_USER`, `SSH_KEY`, `APP_DIR`,
    `STAGE_BASE_URL`
  - `production` environment: `SSH_HOST`, `SSH_USER`, `SSH_KEY`, `APP_DIR`

## Setup Instructions

### Step 1: Add Repository Secrets

Go to `Settings > Secrets and variables > Actions` and add:

| Secret Name | Value | Notes |
|-------------|-------|-------|
| `DOCR_REGISTRY` | DO Container Registry URL | e.g., `registry.digitalocean.com/my-registry` |
| `DO_API_TOKEN` | DigitalOcean API token | Needs registry access |

### Step 2: Create GitHub Environments

Create environments named `stage` and `production`.

Add these environment secrets to both:

| Secret Name | Value | Notes |
|-------------|-------|-------|
| `SSH_HOST` | Droplet IP/hostname | Environment-specific |
| `SSH_USER` | SSH username | e.g., `deploy` |
| `SSH_KEY` | Private SSH key | Multiline private key |
| `APP_DIR` | App directory | e.g., `/opt/event-api` |

Add this only to `stage`:

| Secret Name | Value | Notes |
|-------------|-------|-------|
| `STAGE_BASE_URL` | Public stage API URL | e.g., `https://stage-api.example.com` |

Configure required reviewers on the `production` environment for manual
approval.

### Step 3: Generate SSH Key for Deployment

On your local machine:

```bash
# Generate a new SSH key (if you don't have one)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/github_deploy -N ""

# Copy public key to production server
ssh-copy-id -i ~/.ssh/github_deploy.pub user@production-server

# Add private key as SSH_KEY secret
cat ~/.ssh/github_deploy
# Copy entire output and paste into GitHub secret
```

### Step 4: Configure Each Droplet

On each server:

```bash
# Create app directory
sudo mkdir -p /opt/event-api
sudo chown $USER:$USER /opt/event-api

# Copy deployment files from this repository
scp docker-compose.yml deploy.sh user@server:/opt/event-api/

# Create and configure environment
nano .env

# Required values:
# DATABASE_URL=postgresql://...
# IMAGE=registry.digitalocean.com/my-registry/event-api:latest
```

## Workflow Triggers

### Automatic Triggers

- **test.yml** and **build.yml**: Pull requests and pushes to main
- **deploy.yml**: Main branch pushes only

### Manual Triggers

`deploy.yml` supports manual trigger via the "Actions" tab:

1. Go to `Actions` tab
2. Select workflow
3. Click "Run workflow"
4. Select branch and click "Run workflow"

## Viewing Results

### Test Results
- Go to `Actions` tab
- Click on workflow run
- View logs in "Run tests" step
- Download test artifacts

### Deployment Logs
- Go to `Actions` tab
- Click deploy.yml workflow run
- View stage, stage integration test, and production deploy logs

## Troubleshooting

### Tests Failing

```bash
# Run locally to debug
pytest tests/ -v
```

### Deploy Failing

**Check secrets are set:**
```bash
# In GitHub: Settings > Secrets and variables
# Verify repository secrets and environment secrets exist
```

**Check SSH access:**
```bash
ssh -i ~/.ssh/github_deploy user@production-server
```

**Check DigitalOcean token and registry:**
```bash
# Verify DO_API_TOKEN can access DOCR_REGISTRY
doctl registry login
```

### Slow Builds

- Docker layer caching should speed up builds
- Pip caching reduces dependency installation time
- Check "Actions" settings for runner specs

### Workflows Not Running

1. Check if branch is protected
2. Verify workflow YAML is valid
3. Check if branch matches trigger conditions
4. Manually trigger workflow to test

## Best Practices

1. **Test locally before pushing**
   ```bash
   pytest tests/ -v
   ruff check .
   flake8 app tests --max-line-length=88 --extend-ignore=E203,W503
   ```

2. **Keep secrets secure**
   - Never commit secrets to repository
   - Regenerate access tokens periodically
   - Rotate SSH keys annually

3. **Monitor workflow runs**
   - Check Actions tab regularly
   - Set up GitHub notifications
   - Review failed workflow logs

4. **Update dependencies**
   - Run `safety check` before major updates
   - Test dependency updates in separate PR
   - Review security advisories

## CI/CD Badge

Add this to your README.md to show CI status:

```markdown
![Tests](https://github.com/Myagmarbat/event-api/actions/workflows/test.yml/badge.svg)
![Build](https://github.com/Myagmarbat/event-api/actions/workflows/build.yml/badge.svg)
![Deploy](https://github.com/Myagmarbat/event-api/actions/workflows/deploy.yml/badge.svg)
```

## Support

For issues with workflows:

1. Check GitHub Actions logs
2. Review workflow YAML syntax
3. Verify all secrets are set
4. Test workflow locally with `act` (GitHub Actions locally):
   ```bash
   brew install act
   act push -j test
   ```

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Buildx Documentation](https://docs.docker.com/build/architecture/)
- [Python GitHub Actions](https://github.com/actions/setup-python)
- [SSH Deploy Action](https://github.com/appleboy/ssh-action)
