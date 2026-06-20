from sqlalchemy import Column, String
from app.db import Base

class Event(Base):
    __tablename__ = "event"
    id = Column(String, primary_key=True)
    event_type = Column(String, nullable=False)
    user_id = Column(String, nullable=False)