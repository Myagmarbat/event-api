from app.service import create_event_object

def fake_uuid():
    return "fixed-id"

def test_create_event_object():
    event = create_event_object("signup", "123", id_generator=fake_uuid)

    assert event.id == "fixed-id"
    assert event.event_type == "signup"
    assert event.user_id == "123"