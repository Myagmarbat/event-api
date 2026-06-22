"""Dependency injection utilities."""

from app.db import SessionLocal
from sqlalchemy.orm import Session


def get_db() -> Session:
    """
    Get database session dependency.

    Yields:
        SQLAlchemy Session object

    Note:
        Automatically closes the session after request completion.
        Rolls back any uncommitted changes on error.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
