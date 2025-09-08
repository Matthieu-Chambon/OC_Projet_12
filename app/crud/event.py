from app.models.models import Event, Employee
from datetime import datetime


def create_event(session, data):
    """Crée un nouvel événement."""
    try:
        event = Event(**data)
        session.add(event)
        session.commit()
        session.refresh(event)
        return event
    except Exception as e:
        raise ValueError(f"Erreur lors de la création de l'événement : {e}")


def get_events(session, filters={}, sorts={}):
    """Récupère la liste des événements en fonction des critères du filtrage et du tri."""
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
    """Met à jour un événement."""
    event = session.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise ValueError(f"Aucun événement trouvé avec l'ID {event_id}.")

    employee = session.query(Employee).filter(Employee.employee_number == req_emp_num).first()

    if event.support_contact:
        if event.support_contact.employee_number != req_emp_num and employee.role.name != "Management":
            raise ValueError("Vous n'êtes pas autorisé à modifier cet événement.")
    else:
        if employee.role.name != "Management":
            raise ValueError("Seul un manager peut modifier l'événement s'il n'a pas de contact support associé.")

    for attribute, value in updates.items():
        if not hasattr(Event, attribute):
            raise ValueError(f"L'attribut '{attribute}' n'existe pas dans le modèle Event.")

        if attribute == "support_contact_id":
            raise ValueError("Veuillez utiliser la commande 'event update-contact' "
                             "pour mettre à jour le contact support.")

        if attribute not in ['name', 'start_date', 'end_date', 'location', 'attendees', 'notes']:
            raise ValueError(f"L'attribut '{attribute}' n'est pas modifiable.")

        if value.lower() in ("none", "null"):
            value = None

        if attribute in ['start_date', 'end_date'] and value is not None:
            try:
                value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValueError(f"Le format de la date pour '{attribute}' est invalide. Utilisez le format "
                                 f"YYYY-MM-DD HH:MM:SS.")

        if attribute == 'attendees' and value is not None:
            try:
                value = int(value)
                if value < 0:
                    raise ValueError("Le nombre d'invités doit être un entier positif.")
            except ValueError:
                raise ValueError("Le nombre d'invités doit être un entier positif.")

        setattr(event, attribute, value)

    session.commit()
    session.refresh(event)
    return event


def update_event_support_contact(session, event_id, support_contact):
    """Met à jour le contact support d'un événement."""
    employee = session.query(Employee).filter(
        (Employee.id == support_contact) | (Employee.employee_number == support_contact)
    ).first()

    if not employee:
        raise ValueError(f"Aucun employé trouvé avec le numéro ou l'ID {support_contact}.")

    if employee.role.name != "Support":
        raise ValueError(f"L'employé {employee.first_name} {employee.last_name} ({employee.employee_number}) "
                         f"n'est pas un support.")

    event = session.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise ValueError(f"Aucun événement trouvé avec l'ID {event_id}.")

    event.support_contact_id = employee.id
    session.commit()
    session.refresh(event)

    return event


def delete_event(session, event):
    """Supprime un événement."""
    session.delete(event)
    session.commit()
