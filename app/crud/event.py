from app.models.models import Event
from datetime import datetime

def create_event(session, data):
    try:
        event = Event(**data)
        session.add(event)
        session.commit()
        session.refresh(event)
        return event
    except Exception as e:
        raise ValueError(f"Erreur lors de la création de l'événement : {e}")
    
def get_all_events(session):
    return session.query(Event).all()

def get_events_by(session, attribute, value):
    if not hasattr(Event, attribute):
        raise ValueError(f"L'attribut '{attribute}' n'existe pas dans le modèle Event.")
    
    if value.lower() in ("none", "null"):
        return session.query(Event).filter(getattr(Event, attribute).is_(None)).all()
    else:
        return session.query(Event).filter(getattr(Event, attribute) == value).all()

def update_event_by_id(session, event_id, attribute, value, employee_number):
    if not hasattr(Event, attribute):
        raise ValueError(f"L'attribut '{attribute}' n'existe pas dans le modèle Event.")
    
    if attribute not in ['name', 'start_date', 'end_date', 'location', 'attendees', 'note']:
        raise ValueError(f"L'attribut '{attribute}' ne peut pas être mis à jour directement.")
    
    event = session.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise ValueError(f"Aucun événement trouvé avec l'ID {event_id}.")
    
    if event.support_contact is None:
        raise ValueError("Aucun employé du département support n'est assigné à cet événement.")

    if event.support_contact.employee_number != employee_number:
        raise ValueError(f"Vous n'êtes pas l'employé responsable de cet événement.")

    match attribute:
        case "start_date" | "end_date":
            try:
                value = datetime.strptime(value, "%d/%m/%Y_%H:%M")
            except ValueError:
                raise ValueError(f"La valeur de '{attribute}' doit être une date au format DD/MM/YYYY_HH:MM.")
            value = value.strftime("%Y-%m-%d %H:%M:%S")
            print(value)

        case "attendees":
            try:
                value = int(value)
            except ValueError:
                raise ValueError(f"La valeur de '{attribute}' doit être un entier.")

            if value < 0:
                raise ValueError(f"La valeur de '{attribute}' ne peut pas être négative.")

    setattr(event, attribute, value)
    session.commit()
    session.refresh(event)
    return event

def delete_event_by_id(session, event_id):
    event = session.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise ValueError(f"Aucun événement trouvé avec l'ID {event_id}.")
    
    session.delete(event)
    session.commit()
    return event