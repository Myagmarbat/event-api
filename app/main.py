from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app import models, schemas
from app.db import Base, engine
from app.deps import get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/events", response_model=schemas.EventOut)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    db_event = models.Event(
        id=str(uuid.uuid4()),
        event_type=event.event_type,
        user_id=event.user_id
    )

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return db_event


@app.get("/events", response_model=list[schemas.EventOut])
def list_events(db: Session = Depends(get_db)):
    return db.query(models.Event).all()


@app.get("/events/{event_id}", response_model=schemas.EventOut)
def get_event(event_id: str, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return event


@app.delete("/events/{event_id}")
def delete_event(event_id: str, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    db.delete(event)
    db.commit()

    return {"deleted": True}