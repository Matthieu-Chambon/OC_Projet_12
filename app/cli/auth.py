from getpass import getpass
from app.cli.core import cli, safe_execute
from app.crud import employee as crud_employee

from app.auth.password import verify_password
from app.auth.token import create_access_token, decode_access_token
from app.auth.session import save_token_locally, load_token
from app.auth.decorators import require_token

from app.db.database import Session


db = Session()

@cli.command("login")
def login():
    """Se connecter en tant qu'employé."""
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
@require_token
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