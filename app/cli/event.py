from app.cli.core import cli, input_with_limit, safe_execute, attr_val_to_dict, sort_to_dict
from app.auth.token import decode_access_token
from app.auth.session import load_token
from app.auth.decorators import require_token, is_salesperson_or_manager, is_support_or_manager, is_manager
from app.db.database import Session
from app.crud import employee as crud_employee
from app.crud import contract as crud_contract
from app.crud import event as crud_event
from app.ui import views

import click
from datetime import datetime


db = Session()


@cli.group()
def event():
    """Groupe de commandes pour gérer les événements."""
    pass


@event.command("create")
@require_token
@is_salesperson_or_manager
def create_event():
    """Créer un nouvel événement."""
    req_emp_num = decode_access_token(load_token())["emp_number"]
    employee = safe_execute(crud_employee.get_employees, db, {"employee_number": req_emp_num}, None)[0]

    name = input_with_limit("Nom de l'événement : ", 100)

    while True:
        contract_id = input(">>> ID du contrat associé à l'événement : ")

        contracts = safe_execute(crud_contract.get_contracts, db, {"id": contract_id}, None)

        try:
            contract = contracts[0]
        except Exception:
            print(f"Aucun contrat trouvé avec l'ID {contract_id}.")
            continue

        if contract.event:
            print(f"Un événement est déjà associé au contrat {contract_id}.")
            continue

        if contract.sale_contact:
            if contract.sale_contact.employee_number != req_emp_num and employee.role.name != "Management":
                print("Vous n'êtes pas autorisé à créer un événement pour ce contrat.")
                continue
        else:
            if employee.role.name != "Management":
                print("Seul un manager peut créer un événement si le contrat n'a pas de commercial associé.")
                continue

        if contract.signed is False:
            print(f"Le contrat {contract_id} n'est pas signé.")
            continue

        break

    while True:
        start_date = input(">>> Date de début de l'événement (YYYY-MM-DD HH:MM) : ")

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        except ValueError:
            print("Format de date invalide. Veuillez utiliser le format YYYY-MM-DD HH:MM.")
            continue

        break

    while True:
        end_date = input(">>> Date de fin de l'événement (YYYY-MM-DD HH:MM) : ")

        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
        except ValueError:
            print("Format de date invalide. Veuillez utiliser le format YYYY-MM-DD HH:MM.")
            continue

        if end_date <= start_date:
            print("La date de fin doit être postérieure à la date de début.")
            continue

        break

    location = input_with_limit("Lieu de l'événement : ", 100)

    while True:
        attendees = input(">>> Nombre d'invités attendus : ")

        try:
            attendees = int(attendees)
        except ValueError:
            print("Veuillez entrer un nombre valide.")
            continue

        if attendees < 0:
            print("Veuillez entrer un nombre d'invités positif.")
            continue

        break

    notes = input_with_limit("Remarques supplémentaires : ", 255)

    data = {
        "name": name,
        "contract_id": contract_id,
        "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S"),
        "location": location,
        "attendees": attendees,
        "notes": notes
    }

    event = safe_execute(crud_event.create_event, db, data)
    if event:
        views.display_events([event], "create")


@event.command("list")
@click.option(
    "--filter", "-f",
    multiple=True,
    help="Critère de filtrage au format attribut=valeur. Exemple: -f sale_contact_id=1 -f signed=False"
)
@click.option(
    "--sort", "-s",
    multiple=True,
    help="Critère de tri au format attribut=asc|desc.\nExemple: -s last_name=asc"
)
@require_token
def get_events(filter, sort):
    """Récupère la liste des événements en fonction des critères du filtrage et du tri."""

    filters = attr_val_to_dict(filter)
    sorts = sort_to_dict(sort)

    events = safe_execute(crud_event.get_events, db, filters, sorts)
    views.display_events(events, "list")


@event.command("update")
@click.argument("event_id", type=int)
@click.argument("update", nargs=-1, required=True)
@require_token
@is_support_or_manager
def update_event(event_id, update):
    """
    Met à jour un événement.

    Exemple : event update 1 name='Nouvel événement' location='Salle 1'
    """
    updates = attr_val_to_dict(update)

    req_emp_num = decode_access_token(load_token())["emp_number"]

    event = safe_execute(crud_event.update_event, db, event_id, updates, req_emp_num)
    if event:
        views.display_events([event], "update")


@event.command("update-contact")
@click.argument("event_id", type=int)
@click.argument("support_contact")
@require_token
@is_manager
def update_event_support_contact(event_id, support_contact):
    """
    Met à jour le contact support d'un événement.

    Exemple : event update-contact 1 EMP0001
    """
    event = safe_execute(crud_event.update_event_support_contact, db, event_id, support_contact)
    if event:
        views.display_events([event], "update")


@event.command("delete")
@click.argument("event_id")
@require_token
@is_manager
def delete_event(event_id):
    """Supprime un événement."""
    events = safe_execute(crud_event.get_events, db, {"id": event_id}, None)

    try:
        event = events[0]
    except Exception:
        print(f"Aucun événement trouvé avec l'ID {event_id}.")
        return

    while True:
        confirmation = input(f">>> Êtes-vous sûr de vouloir supprimer l'événement {event.id} ? (oui/non) ")
        if confirmation.lower() == "oui":
            views.display_events([event], "delete")
            safe_execute(crud_event.delete_event, db, event)
            break
        elif confirmation.lower() == "non":
            print("Suppression annulée.")
            break
        else:
            print("Veuillez répondre par 'oui' ou 'non'.")
