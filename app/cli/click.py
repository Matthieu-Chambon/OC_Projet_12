from app.db.database import Session
from app.cli import views
from app.crud import (
    role as crud_role,
    employee as crud_employee,
    customer as crud_customer,
    contract as crud_contract,
    event as crud_event
)

from app.auth.password import verify_password
from app.auth.token import create_access_token, decode_access_token
from app.auth.session import save_token_locally, load_token
from app.auth.decorators import require_token, is_salesperson_or_manager, is_support_or_manager, is_manager

from getpass import getpass
from datetime import datetime

import click


db = Session()

# ******************************************* #
#            Fonctions génériques             #
# ******************************************* #

def safe_execute(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except ValueError as e:
        print(f"Erreur : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        
def input_with_limit(prompt, limit):
    while True:
        value = input(">>> " + prompt)
        if len(value) > limit:
            print(f"Veuillez entrer un texte de moins de {limit} caractères.")
        else:
            return value

def attr_val_to_dict(attr_val_pairs):
    attrs = {}

    for pair in attr_val_pairs:
        if "=" not in pair:
            raise click.BadParameter("Chaque option doit être au format attribut=valeur.")
        attribute, value = pair.split("=", 1)
        attrs[attribute] = value

    return attrs

def sort_to_dict(sort):
    sorts = {}

    for s in sort:
        if "=" not in s:
            raise click.BadParameter("Le critère de tri doit être au format attribut=asc|desc.")
        attribute, order = s.split("=", 1)
        if order not in ["asc", "desc"]:
            raise click.BadParameter("L'ordre de tri doit être 'asc' ou 'desc'.")
        
        sorts[attribute] = order

    return sorts

# ******************************************* #
#               CLI principale                #
# ******************************************* #

@click.group()
def cli():
    """Epic Events CLI - Gestion complète des rôles, employés, clients, contrats et événements"""
    pass

# ******************************************* #
#                Authentication               #
# ******************************************* #

@cli.command("login")
def login():
    emp_number = input(">>> Numéro d'employé : ")
    password = getpass(">>> Mot de passe : ")

    employees = safe_execute(crud_employee.get_employees, db, {"employee_number": emp_number}, None)
    if not employees:
        print(f"Aucun employé trouvé avec le numéro {emp_number}.")
        return
    
    user = employees[0]

    if verify_password(password, user.password):
        print(f"Connexion réussie pour l'employé : {user.first_name} {user.last_name}")
        token = create_access_token(data={"emp_number": emp_number, "role_id": user.role_id})
        save_token_locally(token)
    else:
        print("Échec de la connexion : numéro d'employé ou mot de passe incorrect.")
        
@cli.command("change-password")
def change_password():
    """Changer le mot de passe de l'utilisateur connecté."""
    print("Demande de changement du mot de passe pour l'utilisateur connecté.")
    token = load_token()
    employee_number = decode_access_token(token)["emp_number"]
    employees = crud_employee.get_employees(db, {"employee_number": employee_number}, None)

    try:
        employee = employees[0]
    except Exception as e:
        print(f"Aucun employé trouvé avec le numéro {employee_number}.")
        return
    
    previous_password = getpass(">>> Mot de passe précédent : ")
    new_password = getpass(">>> Nouveau mot de passe : ")

    if not verify_password(previous_password, employee.password):
        print("Échec de la mise à jour du mot de passe : mot de passe précédent incorrect.")
        return
    
    if safe_execute(crud_employee.update_password,db, employee, new_password):
        print("Mot de passe mis à jour avec succès.")
    else:
        print("Erreur lors de la mise à jour du mot de passe.")

        

# ******************************************* #
#                   Role                      #
# ******************************************* #

@cli.group()
def role():
    """Gestion des rôles"""
    pass

@role.command("list")
@require_token
def get_roles():
    """Récupère tous les rôles."""
    roles = safe_execute(crud_role.get_roles, db)
    views.display_roles(roles)

# ******************************************* #
#                 Employee                    #
# ******************************************* #

@cli.group()
def employee():
    """Groupe de commandes pour la gestion des employés"""
    pass

@employee.command("create")
@require_token
@is_manager
def create_employee():
    """Créer un nouvel employé"""
    first_name = input_with_limit("Prénom : ", 100)
    last_name = input_with_limit("Nom : ", 100)

    while True:
        email = input_with_limit("Email : ", 100)
        if not crud_employee.get_employees(db, {"email": email}, None):
            break
        else:
            print(f"Un employé avec l'email {email} existe déjà. Veuillez en choisir un autre.")

    while True:
        password = getpass(">>> Mot de passe : ")
        confirm_password = getpass(">>> Confirmer le mot de passe : ")
        if password == confirm_password:
            break
        else:
            print("Les mots de passe ne correspondent pas. Veuillez réessayer.")
    
    roles = safe_execute(crud_role.get_roles, db)
    views.display_roles(roles)
    
    while True:
        role = input(">>> ID du rôle (1, 2 ou 3) : ")
        try:
            role_id = int(role)
            if role_id in (1, 2, 3):
                break
        except ValueError:
            print("L'ID du rôle est incorrect.")

    data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "role_id": role,
    }

    new_employee = safe_execute(crud_employee.create_employee, db, data)
    if new_employee:
        views.display_employees([new_employee], "create")
        
@employee.command("list")
@click.option(
    "--filter", "-f",
    multiple=True,
    help="Critère de filtrage au format attribut=valeur. Exemple: -f first_name=Alice -f role_id=2"
)
@click.option(
    "--sort", "-s",
    multiple=True,
    help="Critère de tri au format attribut=asc|desc.\nExemple: -s last_name=asc"
)
@require_token
def get_employees(filter, sort):
    """Récupère la liste des employés en fonction des critères du filtrage et du tri."""

    filters = attr_val_to_dict(filter)
    sorts = sort_to_dict(sort)
    
    print(f"Filtres appliqués : {filters}")
    print(f"Tris appliqués : {sorts}")
    
    employees = safe_execute(crud_employee.get_employees, db, filters, sorts)
    views.display_employees(employees, "list")

@employee.command("update")
@click.argument("employee")
@click.argument("update", nargs=-1, required=True)
@require_token
@is_manager
def update_employee(employee, update):
    """
    Met à jour un employé.

    Exemple : employee update EMP0001 first_name=Alice last_name="Dupont Martin"
    """
    updates = attr_val_to_dict(update)
        
    print(updates)

    employee = safe_execute(crud_employee.update_employee, db, employee, updates)
    if employee:
        views.display_employees([employee], "update")
        
@employee.command("update-password")
@click.argument("employee")
@require_token
@is_manager
def update_employee_password(employee):
    """Met à jour le mot de passe d'un employé."""
    
    if employee.isdigit():
        employees = safe_execute(crud_employee.get_employees, db, {"id": employee}, None)
    else:
        employees = safe_execute(crud_employee.get_employees, db, {"employee_number": employee}, None)

    try:
        employee = employees[0]
    except Exception as e:
        print(f"Aucun employé trouvé avec le numéro ou ID {employee}.")
        return

    new_password = getpass(">>> Nouveau mot de passe : ")

    if safe_execute(crud_employee.update_password,db, employee, new_password):
            print("Mot de passe mis à jour avec succès.")
    else:
        print("Erreur lors de la mise à jour du mot de passe.")

@employee.command("delete")
@click.argument("employee")
@require_token
@is_manager
def delete_employee(employee):
    """Supprime un employé."""
    
    if employee.isdigit():
        employees = safe_execute(crud_employee.get_employees, db, {"id": employee}, None)
    else:
        employees = safe_execute(crud_employee.get_employees, db, {"employee_number": employee}, None)
   
    try:
        employee = employees[0]
    except Exception as e:
        print(f"Aucun employé trouvé avec le numéro ou ID {employee}.")
        return

    while True:
        confirmation = input(f">>> Êtes-vous sûr de vouloir supprimer l'employé {employee.first_name} {employee.last_name} ({employee.employee_number}) ? (oui/non) ")
        if confirmation.lower() == "oui":
            views.display_employees([employee], "delete")
            safe_execute(crud_employee.delete_employee, db, employee)
            break
        elif confirmation.lower() == "non":
            print("Suppression annulée.")
            break
        else:
            print("Veuillez répondre par 'oui' ou 'non'.")

# ******************************************* #
#                  Customer                   #
# ******************************************* #

@cli.group()
def customer():
    """Groupe de commandes pour la gestion des clients."""
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
    
    print(f"Filtres appliqués : {filters}")
    print(f"Tris appliqués : {sorts}")
    
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
    """
    Supprime un client.

    Exemple : customer delete 1
    """
    customers = safe_execute(crud_customer.get_customers, db, {"id": customer_id}, None)
    
    try:
        customer = customers[0]
    except Exception as e:
        print(f"Aucun client trouvé avec l'ID {customer_id}.")
        return

    while True:
        confirmation = input(f">>> Êtes-vous sûr de vouloir supprimer le client {customer.first_name} {customer.last_name} ? (oui/non) ")
        if confirmation.lower() == "oui":
            views.display_customers([customer], "delete")
            safe_execute(crud_customer.delete_customer, db, customer)
            break
        elif confirmation.lower() == "non":
            print("Suppression annulée.")
            break
        else:
            print("Veuillez répondre par 'oui' ou 'non'.")


# ******************************************* #
#                   Contract                  #
# ******************************************* #

@cli.group()
def contract():
    """Groupe de commandes pour gérer les contrats."""
    pass

@contract.command("create")
@require_token
@is_manager
def create_contract():
    while True:
        customer_id = input(">>> ID du client : ")
        customers = crud_customer.get_customers(db, {"id": customer_id}, None)

        if not customers:
            print(f"Aucun client trouvé avec l'ID {customer_id}. Veuillez réessayer.")
            continue

        customer = customers[0]
        print(customer.id)
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
        
        print(total_amount)
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

        print(remaining_amount)
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
    help="Critère de tri au format attribut=asc|desc.\nExemple: -s last_name=asc"
)
@require_token
def get_contracts(filter, sort):
    """Récupère la liste des contrats en fonction des critères du filtrage et du tri."""

    filters = attr_val_to_dict(filter)
    sorts = sort_to_dict(sort)
    
    print(f"Filtres appliqués : {filters}")
    print(f"Tris appliqués : {sorts}")

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
    """
    Supprime un contrat.

    Exemple : contract delete 1
    """
    contracts = safe_execute(crud_contract.get_contracts, db, {"id": contract_id}, None)  
    
    try:
        contract = contracts[0]
    except Exception as e:
        print(f"Aucun contrat trouvé avec l'ID {contract_id}.")
        return

    while True:
        confirmation = input(f">>> Êtes-vous sûr de vouloir supprimer le contrat {contract.id} (client : {contract.customer.first_name} {contract.customer.last_name}) ? (oui/non) ")
        if confirmation.lower() == "oui":
            views.display_contracts([contract], "delete")
            safe_execute(crud_contract.delete_contract, db, contract)
            break
        elif confirmation.lower() == "non":
            print("Suppression annulée.")
            break
        else:
            print("Veuillez répondre par 'oui' ou 'non'.")
            
# ******************************************* #
#                   Event                     #
# ******************************************* #

@cli.group()
def event():
    """Groupe de commandes pour gérer les événements."""
    pass

@event.command("create")
@require_token
@is_salesperson_or_manager
def create_event():
    req_emp_num = decode_access_token(load_token())["emp_number"]
    employee = safe_execute(crud_employee.get_employees, db, {"employee_number": req_emp_num}, None)[0]

    name = input_with_limit("Nom de l'événement : ", 100)
    
    while True:
        contract_id = input(">>> ID du contrat associé à l'événement : ")

        contracts = safe_execute(crud_contract.get_contracts, db, {"id": contract_id}, None)
        
        try:
            contract = contracts[0]
        except Exception as e:
            print(f"Aucun contrat trouvé avec l'ID {contract_id}.")
            continue
        
        if contract.event:
            print(f"Un événement est déjà associé au contrat {contract_id}.")
            continue 

        if contract.sale_contact:
            if contract.sale_contact.employee_number != req_emp_num and employee.role.name != "Management":
                print(f"Vous n'êtes pas autorisé à créer un événement pour ce contrat.")
                continue
        else:
            if employee.role.name != "Management":
                print(f"Seul un manager peut créer un événement si le contrat n'a pas de commercial associé.")
                continue

        if contract.signed is False:
            print(f"Le contrat {contract_id} n'est pas signé.")
            continue

        break
    
    while True:
        start_date = input(">>> Date de début de l'événement (YYYY-MM-DD HH:MM) : ")

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
            print(start_date)
        except ValueError:
            print("Format de date invalide. Veuillez utiliser le format YYYY-MM-DD HH:MM.")
            continue
        
        break
    
    while True:
        end_date = input(">>> Date de fin de l'événement (YYYY-MM-DD HH:MM) : ")

        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
            print(end_date)
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
    
    print(f"Filtres appliqués : {filters}")
    print(f"Tris appliqués : {sorts}")

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
    """
    Supprime un événement.

    Exemple : event delete 1
    """
    events = safe_execute(crud_event.get_events, db, {"id": event_id}, None)

    try:
        event = events[0]
    except Exception as e:
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