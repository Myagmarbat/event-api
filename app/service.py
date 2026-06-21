import uuid
from app.models import Event


def create_event_object(event_type: str, user_id: str):
    return Event(
        id=str(uuid.uuid4()),
        event_type=event_type,
        user_id=user_id
    )