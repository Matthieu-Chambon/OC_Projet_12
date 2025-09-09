from app.cli.core import cli, safe_execute, attr_val_to_dict, sort_to_dict
from app.auth.token import decode_access_token
from app.auth.session import load_token
from app.auth.decorators import require_token, is_salesperson_or_manager, is_manager
from app.db.database import Session
from app.crud import customer as crud_customer
from app.crud import contract as crud_contract
from app.ui import views

import click


db = Session()


@cli.group()
def contract():
    """Groupe de commandes pour gérer les contrats."""
    pass


@contract.command("create")
@require_token
@is_manager
def create_contract():
    """Créer un nouveau contrat."""
    while True:
        customer_id = input(">>> ID du client : ")
        customers = crud_customer.get_customers(db, {"id": customer_id}, None)

        if not customers:
            print(f"Aucun client trouvé avec l'ID {customer_id}. Veuillez réessayer.")
            continue

        customer = customers[0]
        break

    sale_contact_id = customer.sale_contact_id

    while True:
        total_amount = input(">>> Montant total du contrat (en €): ")

        try:
            total_amount = float(total_amount)
        except ValueError:
            print("Le montant total doit être un nombre.")
            continue

        if total_amount <= 0:
            print("Le montant total doit être supérieur à 0.")
            continue

        if total_amount > 99999999.99:
            print("Le montant total ne peut pas dépasser 99 999 999,99€.")
            continue

        break

    while True:
        remaining_amount = input(f">>> Montant restant du contrat (défaut {total_amount}€): ")
        if not remaining_amount:
            remaining_amount = total_amount
            break

        try:
            remaining_amount = float(remaining_amount)
        except ValueError:
            print("Le montant restant doit être un nombre.")
            continue

        if remaining_amount <= 0:
            print("Le montant restant doit être supérieur à 0.")
            continue

        if remaining_amount > total_amount:
            print("Le montant restant ne peut pas être supérieur au montant total.")
            continue

        break

    while True:
        signed = input(">>> Contrat signé (oui/non, défaut non) : ").strip().lower()

        if not signed:
            signed = False
            break

        if signed in ["oui", "o", "yes", "y", "1", "true"]:
            signed = True
        elif signed in ["non", "n", "no", "0", "false"]:
            signed = False
        else:
            print("Veuillez répondre par 'oui' ou 'non'.")
            continue

        break

    data = {
        "customer_id": customer.id,
        "sale_contact_id": sale_contact_id,
        "total_amount": total_amount,
        "remaining_amount": remaining_amount,
        "signed": signed
    }

    contract = safe_execute(crud_contract.create_contract, db, data)
    if contract:
        views.display_contracts([contract], "create")


@contract.command("list")
@click.option(
    "--filter", "-f",
    multiple=True,
    help="Critère de filtrage au format attribut=valeur. Exemple: -f sale_contact_id=1 -f signed=False"
)
@click.option(
    "--sort", "-s",
    multiple=True,
    help="Critère de tri au format attribut=asc|desc. Exemple: -s last_name=asc"
)
@require_token
def get_contracts(filter, sort):
    """Récupère la liste des contrats en fonction des critères du filtrage et du tri."""

    filters = attr_val_to_dict(filter)
    sorts = sort_to_dict(sort)

    contracts = safe_execute(crud_contract.get_contracts, db, filters, sorts)
    views.display_contracts(contracts, "list")


@contract.command("update")
@click.argument("contract_id", type=int)
@click.argument("update", nargs=-1, required=True)
@require_token
@is_salesperson_or_manager
def update_contract(contract_id, update):
    """
    Met à jour un contrat.

    Exemple : contract update 1 total_amount=5000 remaining_amount=3000 signed=True
    """
    updates = attr_val_to_dict(update)

    req_emp_num = decode_access_token(load_token())["emp_number"]

    contract = safe_execute(crud_contract.update_contract, db, contract_id, updates, req_emp_num)
    if contract:
        views.display_contracts([contract], "update")


@contract.command("delete")
@click.argument("contract_id")
@require_token
@is_manager
def delete_contract(contract_id):
    """Supprime un contrat."""
    contracts = safe_execute(crud_contract.get_contracts, db, {"id": contract_id}, None)

    try:
        contract = contracts[0]
    except Exception:
        print(f"Aucun contrat trouvé avec l'ID {contract_id}.")
        return

    while True:
        confirmation = input(f">>> Êtes-vous sûr de vouloir supprimer le contrat {contract.id} "
                             f"(client : {contract.customer.first_name} {contract.customer.last_name}) ? (oui/non) ")
        if confirmation.lower() == "oui":
            views.display_contracts([contract], "delete")
            safe_execute(crud_contract.delete_contract, db, contract)
            break
        elif confirmation.lower() == "non":
            print("Suppression annulée.")
            break
        else:
            print("Veuillez répondre par 'oui' ou 'non'.")
