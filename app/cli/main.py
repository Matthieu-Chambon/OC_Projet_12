from app.db.database import Session
from app.crud import role as crud_role, employee as crud_employee, customer as crud_customer
from app.auth.password import verify_password
from app.auth.token import create_access_token, decode_access_token
from app.auth.session import save_token_locally, load_token
from app.auth.decorators import require_token, require_sale_role, require_support_role, require_management_role
from getpass import getpass


db = Session()

def safe_execute(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except ValueError as e:
        print(f"Erreur : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")


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
    if employees:
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

@require_token
def get_role_by_id(id):
    try:
        id = int(id)
    except ValueError:
        print("L'ID doit être un nombre entier.")
        return

    role = safe_execute(crud_role.get_role_by_id, db, int(id))

    if role:
        print(role)

@require_token
def get_role_by_name(name):
    role = safe_execute(crud_role.get_role_by_name, db, name)

    if role:
        print(role)
        
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
    while True:
        emp_number = input("Numéro d'employé (EMPXXX) : ")
        if not crud_employee.get_employees_by(db, "employee_number", emp_number):
            break
        else:
            print(f"Un employé avec le numéro {emp_number} existe déjà. Veuillez en choisir un autre.")
            
    first_name = input("Prénom : ")
    last_name = input("Nom : ")

    while True:
        email = input("Email : ")
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
        role = input("ID du rôle : ")
        try:
            role_id = int(role)
            if crud_role.get_role_by_id(db, role_id):
                break
            else:
                print(f"Aucun rôle trouvé avec l'ID {role_id}. Veuillez réessayer.")
        except ValueError:
            print("L'ID du rôle doit être un nombre entier. Veuillez réessayer.")

    data = {
        "employee_number": emp_number,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "role_id": role,
    }

    new_employee = safe_execute(crud_employee.create_employee, db, data)
    if new_employee:
        print(f"Employé créé : {new_employee.first_name} {new_employee.last_name}")

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
    employee = safe_execute(crud_employee.delete_employee_by_number, db, employee_number)
    if employee:
        print(f"Employé supprimé : {employee.first_name} {employee.last_name}")

# ******************************************* #
#                  Customer                   #
# ******************************************* #

@require_token
@require_sale_role
def create_customer():
    
    first_name = input("Prénom du client : ")
    last_name = input("Nom du client : ")
    
    while True:
        email = input("Email : ")
        if not crud_customer.get_customers_by(db, "email", email):
            break
        else:
            print(f"Un client avec l'email {email} existe déjà. Veuillez en choisir un autre.")

    phone = input("Téléphone du client : ")
    company = input("Entreprise du client : ")
    
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

# A FAIRE > Suppression d'un client par le département gestion