"""Application configuration."""

# pragma: no cover
import os

APP_NAME = os.getenv("APP_NAME", "event-api")
DATABASE_URL = os.getenv("DATABASE_URL")

# Path to the CA certificate file for DigitalOcean Managed PostgreSQL.
# In CI/production, write the DO_DB_CA_CERT secret to a temp file and set
# this to that path.
DB_SSL_CA = os.getenv("DB_SSL_CA")
