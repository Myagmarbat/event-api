"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class EventCreate(BaseModel):
    """Schema for creating a new event.
    
    Attributes:
        event_type: Type of event (required, non-empty string)
        user_id: ID of user who triggered event (required, non-empty string)
    """
    event_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Type of event"
    )
    user_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="ID of the user"
    )


class EventOut(BaseModel):
    """Schema for event response.
    
    Attributes:
        id: Unique event identifier
        event_type: Type of event
        user_id: ID of user who triggered event
        created_at: Timestamp when event was created
    """
    id: str = Field(..., description="Unique event ID")
    event_type: str = Field(..., description="Type of event")
    user_id: str = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Event creation timestamp")
    model_config = ConfigDict(from_attributes=True)

class Event(EventCreate):
    """Complete event schema combining creation and output fields."""
    id: str
    created_at: Optional[datetime] = None
