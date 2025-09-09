from app.cli.core import cli, input_with_limit, safe_execute, attr_val_to_dict, sort_to_dict
from app.auth.token import decode_access_token
from app.auth.session import load_token
from app.auth.decorators import require_token, is_salesperson_or_manager, is_manager
from app.db.database import Session
from app.crud import employee as crud_employee
from app.crud import customer as crud_customer
from app.ui import views

import click


db = Session()


@cli.group()
def customer():
    """Groupe de commandes pour gérer les clients."""
    pass


@customer.command("create")
@require_token
@is_salesperson_or_manager
def create_customer():
    """Crée un nouveau client."""
    first_name = input_with_limit("Prénom du client : ", 100)
    last_name = input_with_limit("Nom du client : ", 100)

    while True:
        email = input_with_limit("Email : ", 100)
        if not crud_customer.get_customers(db, {"email": email}, None):
            break
        else:
            print(f"Un client avec l'email {email} existe déjà. Veuillez en choisir un autre.")

    phone = input_with_limit("Téléphone du client : ", 15)
    company = input_with_limit("Entreprise du client : ", 100)

    employee_number = decode_access_token(load_token())["emp_number"]
    employee_id = crud_employee.get_employees(db, {"employee_number": employee_number}, None)[0].id

    data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "company": company,
        "sale_contact_id": employee_id
    }

    customer = safe_execute(crud_customer.create_customer, db, data)

    if customer:
        views.display_customers([customer], "create")


@customer.command("list")
@click.option(
    "--filter", "-f",
    multiple=True,
    help="Critère de filtrage au format attribut=valeur. Exemple: -f first_name=Alice -f sale_contact_id=1"
)
@click.option(
    "--sort", "-s",
    multiple=True,
    help="Critère de tri au format attribut=asc|desc.\nExemple: -s last_name=asc"
)
@require_token
def get_customers(filter, sort):
    """Récupère la liste des clients en fonction des critères du filtrage et du tri."""

    filters = attr_val_to_dict(filter)
    sorts = sort_to_dict(sort)

    customers = safe_execute(crud_customer.get_customers, db, filters, sorts)
    views.display_customers(customers, "list")


@customer.command("update")
@click.argument("customer_id", type=int)
@click.argument("update", nargs=-1, required=True)
@require_token
@is_salesperson_or_manager
def update_customer(customer_id, update):
    """
    Met à jour un client.

    Exemple : customer update 1 first_name=Alice last_name="Dupont Martin"
    """
    updates = attr_val_to_dict(update)

    req_emp_num = decode_access_token(load_token())["emp_number"]

    customer = safe_execute(crud_customer.update_customer, db, customer_id, updates, req_emp_num)
    if customer:
        views.display_customers([customer], "update")


@customer.command("update-contact")
@click.argument("customer_id", type=int)
@click.argument("sale_contact")
@require_token
@is_manager
def update_customer_sale_contact(customer_id, sale_contact):
    """
    Met à jour le contact commercial d'un client.

    Exemple : customer update-contact 1 EMP0001
    """
    customer = safe_execute(crud_customer.update_customer_sale_contact, db, customer_id, sale_contact)
    if customer:
        views.display_customers([customer], "update")


@customer.command("delete")
@click.argument("customer_id")
@require_token
@is_manager
def delete_customer(customer_id):
    """Supprime un client."""
    customers = safe_execute(crud_customer.get_customers, db, {"id": customer_id}, None)

    try:
        customer = customers[0]
    except Exception:
        print(f"Aucun client trouvé avec l'ID {customer_id}.")
        return

    while True:
        confirmation = input(f">>> Êtes-vous sûr de vouloir supprimer le client "
                             f"{customer.first_name} {customer.last_name} ? (oui/non) ")
        if confirmation.lower() == "oui":
            views.display_customers([customer], "delete")
            safe_execute(crud_customer.delete_customer, db, customer)
            break
        elif confirmation.lower() == "non":
            print("Suppression annulée.")
            break
        else:
            print("Veuillez répondre par 'oui' ou 'non'.")
