"""Dependency injection utilities."""

from sqlalchemy.orm import Session
import app.db as _db


def get_db() -> Session:
    """
    Get database session dependency.

    Yields:
        SQLAlchemy Session object

    Note:
        Automatically closes the session after request completion.
        Rolls back any uncommitted changes on error.
    """
    # SessionLocal is initialized by init_engine(), called in app/main.py
    if _db.SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_engine() first.")

    db = _db.SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
