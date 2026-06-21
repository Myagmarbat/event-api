"""FastAPI application with event CRUD endpoints."""
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app import models, schemas
from app.db import Base, engine
from app.deps import get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Event API",
    description="API for managing events",
    version="0.1.0"
)


@app.get("/health", tags=["Health"])
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post(
    "/events",
    response_model=schemas.EventOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Events"]
)
def create_event(
    event: schemas.EventCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new event.
    
    Args:
        event: Event creation data
        db: Database session
        
    Returns:
        Created event object
        
    Raises:
        HTTPException: 400 if validation fails
    """
    # Validate input
    if not event.event_type.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="event_type cannot be empty"
        )
    if not event.user_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id cannot be empty"
        )
    
    db_event = models.Event(
        id=str(uuid.uuid4()),
        event_type=event.event_type.strip(),
        user_id=event.user_id.strip()
    )

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return db_event


@app.get(
    "/events",
    response_model=list[schemas.EventOut],
    tags=["Events"]
)
def list_events(db: Session = Depends(get_db)):
    """
    List all events.
    
    Args:
        db: Database session
        
    Returns:
        List of all events
    """
    return db.query(models.Event).all()


@app.get(
    "/events/{event_id}",
    response_model=schemas.EventOut,
    tags=["Events"]
)
def get_event(
    event_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific event by ID.
    
    Args:
        event_id: The event ID
        db: Database session
        
    Returns:
        Event object
        
    Raises:
        HTTPException: 404 if event not found
    """
    event = db.query(models.Event).filter(models.Event.id == event_id).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return event


@app.delete(
    "/events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Events"]
)
def delete_event(
    event_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete an event by ID.
    
    Args:
        event_id: The event ID
        db: Database session
        
    Raises:
        HTTPException: 404 if event not found
    """
    event = db.query(models.Event).filter(models.Event.id == event_id).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    db.delete(event)
    db.commit()
