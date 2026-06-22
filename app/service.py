import uuid
from app.models import Event


def _default_id_generator() -> str:
    return str(uuid.uuid4())


def create_event_object(event_type: str, user_id: str, id_generator=None) -> Event:
    if id_generator is None:
        id_generator = _default_id_generator

    return Event(
        id=id_generator(),
        event_type=event_type,
        user_id=user_id,
    )
