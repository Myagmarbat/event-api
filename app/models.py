"""SQLAlchemy ORM models."""

from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.sql import func
from app.db import Base


class Event(Base):
    """Event model representing an event record in the database.

    Attributes:
        id: Unique event identifier (UUID)
        event_type: Type of event (e.g., 'signup', 'login')
        user_id: User who triggered the event
        created_at: Timestamp when event was created
    """

    __tablename__ = "event"

    id = Column(String(36), primary_key=True, nullable=False)
    event_type = Column(String(100), nullable=False, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)

    # Composite index for efficient queries
    __table_args__ = (Index("idx_user_event_type", "user_id", "event_type"),)

    def __repr__(self):
        """String representation of Event."""
        return f"<Event(id={self.id}, event_type={self.event_type}, user_id={self.user_id})>"
