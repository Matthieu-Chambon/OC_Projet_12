from app.db.database import Session
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
from app.auth.decorators import require_token, require_sale_role, require_support_role, require_management_role

from getpass import getpass
from datetime import datetime


db = Session()

def safe_execute(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except ValueError as e:
        print(f"Erreur : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        
def input_with_limit(prompt, limit):
    while True:
        value = input(prompt)
        if len(value) > limit:
            print(f"Veuillez entrer un texte de moins de {limit} caractères.")
        else:
            return value


# ******************************************* #
#                   Help                      #
# ******************************************* #

def help():
    print("Commandes disponibles :")
    print("  - create_role : Créer un nouveau rôle")
    print("  - get_all_roles : Obtenir tous les rôles")
    print("  - get_role_by_id <id> : Obtenir un rôle par son ID")
    print("  - get_role_by_name <name> : Obtenir un rôle par son nom")
    print("  - update_role_by_id <id> <attribute> <value> : Mettre à jour un rôle par son ID")
    print("  - update_role_by_name <name> <attribute> <value> : Mettre à jour un rôle par son nom")
    print("  - delete_role_by_id <id> : Supprimer un rôle par son ID")
    print("  - delete_role_by_name <name> : Supprimer un rôle par son nom")
    print("  - get_all_employees : Obtenir tous les employés")
    print("  - create_employee : Créer un nouvel employé")
    print("  - login : Connexion d'un employé")
    print("  - help : Afficher cette aide")

# ******************************************* #
#                Authentication               #
# ******************************************* #

def login():
    emp_number = input("Numéro d'employé : ")
    password = getpass("Mot de passe : ")
    
    employees = safe_execute(crud_employee.get_employees_by,db, "employee_number", emp_number)
    if not employees:
        print(f"Aucun employé trouvé avec le numéro {emp_number}.")
        return
    
    user = employees[0]
    print(user)

    if verify_password(password, user.password):
        print(f"Connexion réussie pour l'employé : {user.first_name} {user.last_name}")
        token = create_access_token(data={"emp_number": emp_number, "role_id": user.role_id})
        save_token_locally(token)
        print(token)
    else:
        print("Échec de la connexion : numéro d'employé ou mot de passe incorrect.")
        
@require_token
def change_password():
    previous_password = getpass("Mot de passe précédent : ")
    new_password = getpass("Nouveau mot de passe : ")
    token = load_token()
    employee_number = decode_access_token(token)["emp_number"]
    employee = crud_employee.get_employees_by(db, "employee_number", employee_number)[0]
    
    if verify_password(previous_password, employee.password):
        if safe_execute(crud_employee.update_password,db, employee_number, new_password):
            print("Mot de passe mis à jour avec succès.")
    else:
        print("Échec de la mise à jour du mot de passe : mot de passe précédent incorrect.")
    
            
# ******************************************* #
#                   Role                      #
# ******************************************* #

# def create_role():
#     name = input("Nom du rôle : ")
#     description = input("Description du rôle : ")

#     new_role = safe_execute(crud_role.create_role, db, name, description)
    
#     if new_role:
#         print(f"Rôle créé : {new_role.name}")

@require_token
def get_all_roles():
    roles = safe_execute(crud_role.get_all_roles, db)

    for r in roles:
        print(r)

# @require_token
# def get_role_by_id(id):
#     try:
#         id = int(id)
#     except ValueError:
#         print("L'ID doit être un nombre entier.")
#         return

#     role = safe_execute(crud_role.get_role_by_id, db, int(id))

#     if role:
#         print(role)

# @require_token
# def get_role_by_name(name):
#     role = safe_execute(crud_role.get_role_by_name, db, name)

#     if role:
#         print(role)
        
# def update_role_by_id(id, attribute, value):
#     try:
#         id = int(id)
#     except ValueError:
#         print("L'ID doit être un nombre entier.")
#         return

#     role = safe_execute(crud_role.update_role_by_id, db, int(id), attribute, value)
        
#     if role:
#         print(f"Rôle mis à jour : {role.name}")

# def update_role_by_name(name, attribute, value):
#     role = safe_execute(crud_role.update_role_by_name, db, name, attribute, value)
    
#     if role:
#         print(f"Rôle mis à jour : {role.name}")

# def delete_role_by_id(id):
#     try:
#         id = int(id)
#     except ValueError:
#         print("L'ID doit être un nombre entier.")
#         return
    
#     role = safe_execute(crud_role.delete_role_by_id, db, int(id))
#     if role:
#         print(f"Rôle supprimé : {role.name}")

# def delete_role_by_name(name):
#     role = safe_execute(crud_role.delete_role_by_name, db, name)
    
#     if role:
#         print(f"Rôle supprimé : {role.name}")

# ******************************************* #
#                 Employee                    #
# ******************************************* #

@require_token
@require_management_role
def create_employee():
            
    first_name = input_with_limit("Prénom : ", 100)
    last_name = input_with_limit("Nom : ", 100)

    while True:
        email = input_with_limit("Email : ", 100)
        if not crud_employee.get_employees_by(db, "email", email):
            break
        else:
            print(f"Un employé avec l'email {email} existe déjà. Veuillez en choisir un autre.")

    while True:
        password = getpass("Mot de passe : ")
        confirm_password = getpass("Confirmer le mot de passe : ")
        if password == confirm_password:
            break
        else:
            print("Les mots de passe ne correspondent pas. Veuillez réessayer.")
    
    while True:
        get_all_roles()
        role = input("ID du rôle (1, 2 ou 3) : ")
        try:
            role_id = int(role)
            if crud_role.get_role_by_id(db, role_id):
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
        print(f"Employé créé : {new_employee.first_name} {new_employee.last_name} ({new_employee.employee_number})")

@require_token
@require_management_role
def get_all_employees():

    employees = crud_employee.get_all_employees(db)

    for emp in employees:
        print(emp)

@require_token
@require_management_role
def get_employees_by(attribute, value):
    employees = safe_execute(crud_employee.get_employees_by, db, attribute, value)
    
    if employees:
        for emp in employees:
            print(emp)

@require_token
@require_management_role
def update_employee_by_number(employee_number, attribute, value):
    employee = safe_execute(crud_employee.update_employee_by_number, db, employee_number, attribute, value)

    if employee:
        print(f"Employé mis à jour : {employee.first_name} {employee.last_name}")

@require_token
@require_management_role
def delete_employee_by_number(employee_number):
    employees = safe_execute(crud_employee.get_employees_by, db, "employee_number", employee_number)
    if not employees:
        print(f"Aucun employé trouvé avec le numéro {employee_number}.")
        return

    employee = employees[0]
    while True:
        confirmation = input(f"Êtes-vous sûr de vouloir supprimer l'employé {employee.first_name} {employee.last_name} ({employee.employee_number})? (oui/non) ")
        if confirmation.lower() == "oui":
            safe_execute(crud_employee.delete_employee_by_number, db, employee)
            print(f"Employé supprimé : {employee.first_name} {employee.last_name}")
            break
        elif confirmation.lower() == "non":
            print("Suppression annulée.")
            break
        else:
            print("Veuillez répondre par 'oui' ou 'non'.")

# ******************************************* #
#                  Customer                   #
# ******************************************* #

@require_token
@require_sale_role
def create_customer():

    first_name = input_with_limit("Prénom du client : ", 100)
    last_name = input_with_limit("Nom du client : ", 100)

    while True:
        email = input_with_limit("Email : ", 100)
        if not crud_customer.get_customers_by(db, "email", email):
            break
        else:
            print(f"Un client avec l'email {email} existe déjà. Veuillez en choisir un autre.")

    phone = input_with_limit("Téléphone du client : ", 15)
    company = input_with_limit("Entreprise du client : ", 100)

    employee_number = decode_access_token(load_token())["emp_number"]
    employee_id = crud_employee.get_employees_by(db, "employee_number", employee_number)[0].id
    
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
        print(f"Client créé : {customer.first_name} {customer.last_name}")

@require_token        
def get_all_customers():
    customers = safe_execute(crud_customer.get_all_customers, db)

    if customers:
        for customer in customers:
            print(customer)

@require_token
def get_customers_by(attribute, value):
    customers = safe_execute(crud_customer.get_customers_by, db, attribute, value)
    
    if customers:
        for customer in customers:
            print(customer)
            
@require_token
@require_sale_role
def update_customer_by_id(customer_id, attribute, value):
    try:
        customer_id = int(customer_id)
    except ValueError:
        print("L'ID du client doit être un nombre entier.")
        return
    
    customer = safe_execute(crud_customer.update_customer_by_id, db, customer_id, attribute, value)
    
    if customer:
        print(f"Client mis à jour : {customer.first_name} {customer.last_name}")

@require_token
@require_management_role
def update_customer_sale_contact(customer_id, sale_contact_number):
    try:
        customer_id = int(customer_id)
    except ValueError:
        print("L'ID du client doit être un nombre entier.")
        return

    customer = safe_execute(crud_customer.update_customer_sale_contact, db, customer_id, sale_contact_number)

    if customer:
        print(f"Commercial mis à jour pour le client : {customer.first_name} {customer.last_name}")

@require_token
@require_management_role
def delete_customer_by_id(customer_id):
    try:
        customer_id = int(customer_id)
    except ValueError:
        print("L'ID du client doit être un nombre entier.")
        return
    
    customer = safe_execute(crud_customer.delete_customer_by_id, db, customer_id)
    
    if customer:
        print(f"Client supprimé : {customer.first_name} {customer.last_name}")

# ******************************************* #
#                   Contract                  #
# ******************************************* #

@require_token
@require_management_role
def create_contract():
    
    # while True:
    #     sale_contact_id = input("Numéro d'employé du commercial (EMPXXXX) : ")
    #     sale_contact = crud_employee.get_employees_by(db, "employee_number", sale_contact_id)
        
    #     if not sale_contact:
    #         print(f"Aucun employé trouvé avec le numéro {sale_contact_id}. Veuillez réessayer.")
    #         continue

    #     if sale_contact[0].role.name != "Commercial":
    #         print(f"L'employé {sale_contact_id} n'est pas un commercial. Veuillez réessayer.")
    #         continue

    #     sale_contact_id = sale_contact[0].id
    #     print(sale_contact_id)
    #     break

    while True:
        customer_id = input("ID du client : ")
        customer = crud_customer.get_customers_by(db, "id", customer_id)

        if not customer:
            print(f"Aucun client trouvé avec l'ID {customer_id}. Veuillez réessayer.")
            continue

        customer_id = customer[0].id
        print(customer_id)
        break
    
    customer = safe_execute(crud_customer.get_customers_by, db, "id", customer_id)[0]
    
    sale_contact_id = customer.sale_contact.id
    
    while True:
        total_amount = input("Montant total du contrat (en €): ")
        
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
        remaining_amount = input(f"Montant restant du contrat (défaut {total_amount}€): ")
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
        signed = input("Contrat signé (oui/non, défaut non) : ").strip().lower()

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
    
    print(signed)
    data = {
        "customer_id": customer_id,
        "sale_contact_id": sale_contact_id,
        "total_amount": total_amount,
        "remaining_amount": remaining_amount,
        "signed": signed
    }

    contract = safe_execute(crud_contract.create_contract, db, data)

    if contract:
        print(f"Contrat créé : {contract}")

@require_token
def get_all_contracts():
    contracts = safe_execute(crud_contract.get_all_contracts, db)
    if contracts:
        for contract in contracts:
            print(contract)

@require_token
def get_contracts_by(attribute, value):
    contracts = safe_execute(crud_contract.get_contracts_by, db, attribute, value)

    if contracts:
        for contract in contracts:
            print(contract)


@require_token
@require_sale_role
def update_contract_by_id(contract_id, attribute, value):
    
    employee_number = decode_access_token(load_token())["emp_number"]
    contract = safe_execute(crud_contract.update_contract_by_id, db, contract_id, attribute, value, employee_number)

    if contract:
        print(f"Contrat mis à jour : {contract}")
        
@require_token
@require_management_role
def delete_contract_by_id(contract_id):
    contract = safe_execute(crud_contract.delete_contract_by_id, db, contract_id)

    if contract:
        print(f"Contrat supprimé : {contract}")
        
# ******************************************* #
#                   Event                     #
# ******************************************* #

@require_token
@require_sale_role
def create_event():
    name = input_with_limit("Nom de l'événement : ", 100)

    while True:
        contract_id = input("ID du contrat associé à l'événement : ")

        contracts = crud_contract.get_contracts_by(db, "id", contract_id)

        if not contracts:
            print(f"Aucun contrat trouvé avec l'ID {contract_id}.")
            continue
        
        if contracts[0].event:
            print(f"Un événement est déjà associé au contrat {contract_id}.")
            continue
        
        if contracts[0].signed is False:
            print(f"Le contrat {contract_id} n'est pas signé.")
            continue

        break

    while True:
        start_date = input("Date de début de l'événement (DD/MM/YYYY HH:MM) : ")
        
        try:
            start_date = datetime.strptime(start_date, "%d/%m/%Y %H:%M")
            print(start_date)
        except ValueError:
            print("Format de date invalide. Veuillez utiliser le format DD/MM/YYYY HH:MM.")
            continue
        
        break
    
    while True:
        end_date = input("Date de fin de l'événement (DD/MM/YYYY HH:MM) : ")
        
        try:
            end_date = datetime.strptime(end_date, "%d/%m/%Y %H:%M")
            print(end_date)
        except ValueError:
            print("Format de date invalide. Veuillez utiliser le format DD/MM/YYYY HH:MM.")
            continue
        
        break

    location = input_with_limit("Lieu de l'événement : ", 100)

    while True:
        attendees = input("Nombre d'invités attendus : ")

        try:
            attendees = int(attendees)
        except ValueError:
            print("Veuillez entrer un nombre valide.")
            continue
        
        if attendees < 0:
            print("Veuillez entrer un nombre d'invités positif.")
            continue

        break

    note = input_with_limit("Remarques supplémentaires : ", 255)

    data = {
        "name": name,
        "contract_id": contract_id,
        "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S"),
        "location": location,
        "attendees": attendees,
        "note": note
    }
    
    event = safe_execute(crud_event.create_event, db, data)

@require_token
def get_all_events():
    events = safe_execute(crud_event.get_all_events, db)
    
    if events:
        for event in events:
            print(event)

@require_token
def get_events_by(attribute, value):
    events = safe_execute(crud_event.get_events_by, db, attribute, value)

    if events:
        for event in events:
            print(event)
            
@require_token
@require_support_role
def update_event_by_id(event_id, attribute, value):
    employee_number = decode_access_token(load_token())["emp_number"]
    
    event = safe_execute(crud_event.update_event_by_id, db, event_id, attribute, value, employee_number)

    if event:
        print(f"Événement mis à jour : {event}")

@require_token
@require_management_role
def delete_event_by_id(event_id):
    event = safe_execute(crud_event.delete_event_by_id, db, event_id)

    if event:
        print(f"Événement supprimé : {event}")