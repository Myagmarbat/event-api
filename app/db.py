"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


def get_database_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is required")
    return url


def get_engine():
    url = get_database_url()
    connect_args = {}

    # For DigitalOcean Managed PostgreSQL: set DB_SSL_CA to the path of the CA cert file.
    # In production, write the secret to a temp file and point DB_SSL_CA at it.
    ssl_ca = os.getenv("DB_SSL_CA")
    if ssl_ca and url.startswith("postgresql"):
        connect_args = {
            "sslmode": "require",
            "sslrootcert": ssl_ca,
        }

    return create_engine(url, connect_args=connect_args)


engine = get_engine()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()
