from app.models.models import Employee
from app.auth.password import hash_password
from uuid import uuid4


def create_employee(session, data):
    """Crée un nouvel employé."""
    try:
        temp_number = "TEMP-" + uuid4().hex
        new_employee = Employee(employee_number=temp_number, **data)
        new_employee.password = hash_password(new_employee.password)

        session.add(new_employee)
        session.flush()

        new_employee.employee_number = f"EMP{new_employee.id:04d}"

        session.commit()
        session.refresh(new_employee)

        return new_employee
    except Exception as e:
        raise ValueError(f"Erreur lors de la création de l'employé : {e}")


def get_employees(session, filters={}, sorts={}):
    """Récupère la liste des employés en fonction des critères du filtrage et du tri."""
    query = session.query(Employee)

    for attr, value in filters.items():
        if not hasattr(Employee, attr):
            raise ValueError(f"L'attribut '{attr}' n'existe pas dans le modèle Employee.")

        column = getattr(Employee, attr)

        if value.lower() in ("none", "null"):
            query = query.filter(column.is_(None))
            continue

        if value.lower() in ("true", "false"):
            query = query.filter(column.is_(value.lower() == "true"))
            continue

        query = query.filter(column.contains(value))

    if sorts:
        for attr, order in sorts.items():
            if not hasattr(Employee, attr):
                raise ValueError(f"L'attribut '{attr}' n'existe pas dans le modèle Employee.")

            column = getattr(Employee, attr)

            if order == "asc":
                query = query.order_by(column.asc())
            elif order == "desc":
                query = query.order_by(column.desc())

    return query.all()


def update_employee(session, employee_number_or_id, updates):
    """Met à jour un employé."""
    employee = session.query(Employee).filter(
        (Employee.employee_number == employee_number_or_id) | (Employee.id == employee_number_or_id)
    ).first()

    if not employee:
        raise ValueError(f"Aucun employé trouvé avec le numéro ou id {employee_number_or_id}.")

    for attribute, value in updates.items():
        if not hasattr(Employee, attribute):
            raise ValueError(f"L'attribut '{attribute}' n'existe pas dans le modèle Employee.")

        if attribute == "password":
            raise ValueError("Veuillez utiliser la commande 'employee update-password' pour modifier le mot de passe.")

        if attribute not in ['first_name', 'last_name', 'email', 'role_id']:
            raise ValueError(f"L'attribut '{attribute}' n'est pas modifiable.")

        if attribute == "role_id" and value not in ["1", "2", "3"]:
            raise ValueError("L'ID de rôle doit être 1 (Commercial), 2 (Support) ou 3 (Gestion).")

        setattr(employee, attribute, value)

    session.commit()
    session.refresh(employee)
    return employee


def update_password(session, employee, new_password):
    """Met à jour le mot de passe d'un employé."""
    employee.password = hash_password(new_password)
    session.commit()
    return True


def delete_employee(session, employee):
    """Supprime un employé."""
    session.delete(employee)
    session.commit()
