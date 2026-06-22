"""Database configuration and session management."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Base is just a class — no DB connection needed at import time.
Base = declarative_base()

engine = None
SessionLocal = None


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is required")
    return url


def init_engine():
    """Call this once at app startup before any DB operations."""
    global engine, SessionLocal
    if engine is not None:
        return

    url = get_database_url()
    connect_args = {}

    ssl_ca = os.getenv("DB_SSL_CA")
    if ssl_ca and url.startswith("postgresql"):
        connect_args = {
            "sslmode": "require",
            "sslrootcert": ssl_ca,
        }

    engine = create_engine(url, connect_args=connect_args)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
