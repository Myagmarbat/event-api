import uuid

events = {}

def create_event(data):
    event_id = str(uuid.uuid4())
    event = {
        "id": event_id,
        **data
    }
    events[event_id] = event
    return event

def get_event(event_id):
    return events.get(event_id)

def list_events():
    return list(events.values())

def delete_event(event_id):
    return events.pop(event_id, None)