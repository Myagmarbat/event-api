from app.service import create_event_object


def fake_uuid():
    return "fixed-id"


def test_create_event_object_happy_path():
    event = create_event_object("signup", "123", id_generator=fake_uuid)

    assert event.id == "fixed-id"
    assert event.event_type == "signup"
    assert event.user_id == "123"


def test_create_event_object_preserves_values():
    event_type = "password_reset"
    user_id = "user-42"

    event = create_event_object(event_type, user_id, id_generator=fake_uuid)

    assert event.event_type == event_type
    assert event.user_id == user_id
