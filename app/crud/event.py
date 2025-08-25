from app.models.models import Event, Employee
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
    
def get_events(session, filters, sorts):
    query = session.query(Event)
    
    for attr, value in filters.items():
        if not hasattr(Event, attr):
            raise ValueError(f"L'attribut '{attr}' n'existe pas dans le modèle Event.")

        column = getattr(Event, attr)

        if value.lower() in ("none", "null"):
            query = query.filter(column.is_(None))
            continue
        
        if value.lower() in ("true", "false"):
            query = query.filter(column.is_(value.lower() == "true"))
            continue
        
        query = query.filter(column.contains(value))

    if sorts:
        for attr, order in sorts.items():
            if not hasattr(Event, attr):
                raise ValueError(f"L'attribut '{attr}' n'existe pas dans le modèle Event.")
            
            column = getattr(Event, attr)
            
            if order == "asc":
                query = query.order_by(column.asc())
            elif order == "desc":
                query = query.order_by(column.desc())

    return query.all()

def update_event(session, event_id, updates, req_emp_num):
    event = session.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise ValueError(f"Aucun événement trouvé avec l'ID {event_id}.")
    
    employee = session.query(Employee).filter(Employee.employee_number == req_emp_num).first()
    
    if event.support_contact.employee_number != req_emp_num or employee.role.name != "Management":
        raise ValueError(f"Vous n'êtes pas manager ou l'employé responsable de cet événement.")

    for attribute, value in updates.items():
        if not hasattr(Event, attribute):
            raise ValueError(f"L'attribut '{attribute}' n'existe pas dans le modèle Event.")
        
        if attribute == "support_contact_id":
            raise ValueError(f"Veuillez utiliser la commande 'event update-contact' pour mettre à jour le contact support.")

        if attribute not in ['name', 'start_date', 'end_date', 'location', 'attendees']:
            raise ValueError(f"L'attribut '{attribute}' n'est pas modifiable.")
        
        if value.lower() in ("none", "null"):
            value = None
        
        elif value.lower() in ("true", "false"):
            value = value.lower() == "true"

        setattr(event, attribute, value)

    session.commit()
    session.refresh(event)
    return event

def delete_event(session, event):
    session.delete(event)
    session.commit()