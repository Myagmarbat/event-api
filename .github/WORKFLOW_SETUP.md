# GitHub Actions Workflow Setup Guide

## Overview

This repository uses 6 GitHub Actions workflows for continuous integration, testing, security scanning, and deployment.

## Workflows

### 1. **test.yml** - Unit & Integration Tests
- **Trigger:** Every push to main/develop and all PRs
- **What it does:**
  - Installs Python 3.13 and dependencies
  - Runs unit tests (tests/unit/)
  - Runs integration tests with PostgreSQL (tests/integration/)
  - Generates code coverage report
  - Uploads coverage to Codecov
- **No secrets required**

### 2. **lint.yml** - Code Quality Checks
- **Trigger:** Every push to main/develop and all PRs
- **What it does:**
  - Checks code formatting with Black
  - Validates import sorting with isort
  - Lints with flake8
  - Reports any style violations
- **No secrets required**

### 3. **build.yml** - Docker Image Build
- **Trigger:** Every push to main/develop and all PRs
- **What it does:**
  - Sets up Docker Buildx
  - Builds Docker image
  - Uses GitHub Actions cache for faster builds
  - Tags with commit SHA
- **No secrets required** (doesn't push to registry)

### 4. **deploy.yml** - Full Deployment Pipeline
- **Trigger:** Pushes to main branch only (manual trigger via `workflow_dispatch`)
- **What it does:**
  1. Runs full test suite
  2. Builds and pushes Docker image to Docker Hub
  3. SSHes into production server
  4. Pulls latest image and restarts services
- **Secrets required:**
  - `DOCKER_USERNAME` - Docker Hub username
  - `DOCKER_PASSWORD` - Docker Hub access token
  - `DEPLOY_HOST` - Production server hostname/IP
  - `DEPLOY_USER` - SSH user for production
  - `DEPLOY_SSH_KEY` - Private SSH key for authentication

### 5. **security.yml** - Security Scanning
- **Trigger:** 
  - Every push to main/develop and all PRs
  - Weekly schedule (Sundays at midnight UTC)
- **What it does:**
  - Runs Bandit for Python security issues
  - Checks dependencies with Safety
  - Scans filesystem with Trivy
  - Uploads SARIF report to GitHub Security tab
- **No secrets required**

### 6. **performance.yml** - Performance Benchmarks
- **Trigger:**
  - Pushes to main and all PRs
  - Daily schedule (2 AM UTC)
- **What it does:**
  - Runs performance benchmark tests
  - Generates JSON report
  - Uploads artifacts for analysis
- **No secrets required**

## Setup Instructions

### Step 1: Add GitHub Secrets (Required for Deploy)

Only needed if you plan to use the deploy workflow:

1. Go to: `Settings > Secrets and variables > Actions`
2. Click "New repository secret"
3. Add the following secrets:

| Secret Name | Value | Notes |
|-------------|-------|-------|
| `DOCKER_USERNAME` | Your Docker Hub username | e.g., `myusername` |
| `DOCKER_PASSWORD` | Docker Hub access token | Create at docker.com/settings/security |
| `DEPLOY_HOST` | Production server IP/hostname | e.g., `192.168.1.100` or `prod.example.com` |
| `DEPLOY_USER` | SSH username | e.g., `deploy` |
| `DEPLOY_SSH_KEY` | Private SSH key | Multiline - copy entire key including `-----BEGIN PRIVATE KEY-----` |

### Step 2: Generate Docker Hub Token

1. Go to https://hub.docker.com/settings/security
2. Click "New Access Token"
3. Name it (e.g., "GitHub Actions")
4. Copy the token
5. Add as `DOCKER_PASSWORD` secret

### Step 3: Generate SSH Key for Deployment

On your local machine:

```bash
# Generate a new SSH key (if you don't have one)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/github_deploy -N ""

# Copy public key to production server
ssh-copy-id -i ~/.ssh/github_deploy.pub user@production-server

# Add private key as DEPLOY_SSH_KEY secret
cat ~/.ssh/github_deploy
# Copy entire output and paste into GitHub secret
```

### Step 4: Configure Production Server

On your production server:

```bash
# Create app directory
sudo mkdir -p /app/event-api
sudo chown $USER:$USER /app/event-api

# Clone repository
cd /app/event-api
git clone https://github.com/Myagmarbat/event-api.git .

# Copy and configure environment
cp .env.example .env
# Edit .env with production values
nano .env

# Start services
docker-compose up -d
```

## Workflow Triggers

### Automatic Triggers

- **test.yml** & **lint.yml**: Every push/PR
- **security.yml**: Every push/PR + Weekly Sunday midnight
- **performance.yml**: Main branch + Daily 2 AM UTC
- **deploy.yml**: Main branch pushes only

### Manual Triggers

All workflows support manual trigger via "Actions" tab:

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

### Security Reports
- Go to `Security > Code scanning`
- View Trivy results in SARIF format
- Review Bandit reports in artifacts

### Coverage Reports
- Go to https://codecov.io/
- Sign in with GitHub
- View coverage trends

### Deployment Logs
- Go to `Actions` tab
- Click deploy.yml workflow run
- View "Deploy to production" step logs

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
# Verify all 5 secrets exist
```

**Check SSH access:**
```bash
ssh -i ~/.ssh/github_deploy user@production-server
```

**Check Docker Hub token:**
```bash
# Verify token hasn't expired
# Regenerate if needed at docker.com/settings/security
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
   black --check app/ tests/
   flake8 app/ tests/
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
![Lint](https://github.com/Myagmarbat/event-api/actions/workflows/lint.yml/badge.svg)
![Security](https://github.com/Myagmarbat/event-api/actions/workflows/security.yml/badge.svg)
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
