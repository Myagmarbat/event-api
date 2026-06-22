"""FastAPI application with event CRUD endpoints."""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app import models, schemas
from app.db import Base, init_engine
from app.deps import get_db

# Initialize engine before any DB operations
init_engine()

import app.db as _db  # noqa: E402

Base.metadata.create_all(bind=_db.engine)

app = FastAPI(
    title="Event API",
    description="API for managing events",
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post(
    "/events",
    response_model=schemas.EventOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Events"],
)
def create_event(
    event: schemas.EventCreate,
    db: Session = Depends(get_db),
):
    if not event.event_type.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="event_type cannot be empty",
        )
    if not event.user_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id cannot be empty",
        )

    db_event = models.Event(
        id=str(uuid.uuid4()),
        event_type=event.event_type.strip(),
        user_id=event.user_id.strip(),
    )

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return db_event


@app.get(
    "/events",
    response_model=list[schemas.EventOut],
    tags=["Events"],
)
def list_events(db: Session = Depends(get_db)):
    return db.query(models.Event).all()


@app.get(
    "/events/{event_id}",
    response_model=schemas.EventOut,
    tags=["Events"],
)
def get_event(
    event_id: str,
    db: Session = Depends(get_db),
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return event


@app.delete(
    "/events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Events"],
)
def delete_event(
    event_id: str,
    db: Session = Depends(get_db),
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    db.delete(event)
    db.commit()
