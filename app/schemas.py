from pydantic import BaseModel

class EventCreate(BaseModel):
    event_type: str
    user_id: str

class EventOut(BaseModel):
    id: str
    event_type: str
    user_id: str

    class Config:
        from_attributes = True

class Event(EventCreate):
    id: str