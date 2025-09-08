import pytest
from app.crud import event as crud_event
from app.models.models import Event
from datetime import datetime


def test_create_event(session):
    """Vérifie que la création d'un événement fonctionne."""
    data = {
        "name": "Nouvel événement",
        "contract_id": 5,
        "start_date": datetime.strptime("2023-10-01 10:00:00", "%Y-%m-%d %H:%M:%S"),
        "end_date": datetime.strptime("2023-10-01 12:00:00", "%Y-%m-%d %H:%M:%S"),
        "location": "Salle de conférence",
        "attendees": 10,
        "notes": "Réunion de lancement"
    }

    new_event = crud_event.create_event(
        session,
        data
    )

    assert new_event.id is not None
    assert new_event.name == data["name"]
    assert new_event.start_date == data["start_date"]
    assert new_event.end_date == data["end_date"]
    assert new_event.location == data["location"]
    assert new_event.attendees == data["attendees"]
    assert new_event.notes == data["notes"]


def test_create_event_fail(session):
    """Vérifie que la création d'un événement échoue avec des données invalides."""
    data = {
        "name": "Nouvel événement",
        "contract_id": 5,
        "start_date": datetime.strptime("2023-10-01 10:00:00", "%Y-%m-%d %H:%M:%S"),
        "end_date": datetime.strptime("2023-10-01 12:00:00", "%Y-%m-%d %H:%M:%S"),
        "location": "Salle de conférence",
        "attendees": "a",  # Invalid data
        "notes": "Réunion de lancement"
    }

    with pytest.raises(ValueError):
        crud_event.create_event(
            session,
            data
        )


def test_get_events(session):
    """Vérifie que la récupération d'événements fonctionne."""
    events = crud_event.get_events(session)
    assert events is not None
    assert len(events) == 3


def test_get_events_with_filters(session):
    """Vérifie que la récupération des événements avec des filtres fonctionne."""
    filters = {
        "location": "Parc des Princes",
        "support_contact_id": "3"
    }
    events = crud_event.get_events(session, filters)
    assert events is not None
    assert len(events) == 1
    assert events[0].location == "Parc des Princes"
    assert events[0].support_contact_id == 3


def test_get_events_with_sorts(session):
    """Vérifie que la récupération des événements avec des tris fonctionne."""
    sorts = {
        "start_date": "asc"
    }
    events = crud_event.get_events(session, sorts=sorts)
    assert events is not None
    assert len(events) == 3
    assert events[0].start_date < events[1].start_date < events[2].start_date


def test_get_events_with_filters_and_sorts(session):
    """Vérifie que la récupération des événements avec des filtres et des tris fonctionne."""
    filters = {
        "support_contact_id": "None"
    }
    sorts = {
        "start_date": "asc"
    }
    events = crud_event.get_events(session, filters=filters, sorts=sorts)
    assert events is not None
    assert len(events) == 2
    assert all(event.support_contact_id is None for event in events)
    assert events[0].start_date < events[1].start_date


def test_update_event(session):
    """Vérifie que la mise à jour d'un événement fonctionne."""
    updates = {
        "location": "Nouvelle salle",
        "attendees": "20"
    }

    updated_event = crud_event.update_event(
        session,
        1,
        updates,
        "EMP0003"  # Bob Martin, support contact de l'événement
    )

    assert updated_event is not None
    assert updated_event.location == "Nouvelle salle"
    assert updated_event.attendees == 20


def test_update_event_fail(session):
    """Vérifie que la mise à jour d'un événement échoue avec des données invalides."""
    updates = {
        "location": "Nouvelle salle",
        "attendees": "invalid"  # Invalid data
    }

    with pytest.raises(ValueError):
        crud_event.update_event(
            session,
            1,
            updates,
            "EMP0003"  # Bob Martin, support contact de l'événement
        )


def test_update_event_unauthorized(session):
    """Vérifie que la mise à jour d'un événement échoue si l'utilisateur n'est pas autorisé."""
    updates = {
        "location": "Nouvelle salle",
        "attendees": "20"
    }

    with pytest.raises(ValueError):
        crud_event.update_event(
            session,
            1,
            updates,
            "EMP0004"  # Un autre employé qui n'est pas le contact support ou un manager
        )


def delete_event(session):
    """Vérifie que la suppression d'un événement fonctionne."""
    event = session.query(Event).filter(Event.id == 1).first()
    assert event is not None

    crud_event.delete_event(
        session,
        event,
    )

    deleted_event = session.query(Event).filter(Event.id == 1).first()
    assert deleted_event is None
