
from app.cli.core import cli, input_with_limit, safe_execute, attr_val_to_dict, sort_to_dict
from app.auth.decorators import require_token, is_manager
from app.db.database import Session
from app.crud import employee as crud_employee
from app.crud import role as crud_role
from app.ui import views

from getpass import getpass
import click

db = Session()

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