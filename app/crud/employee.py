from app.models.models import Employee
from app.auth.password import hash_password
from uuid import uuid4

def create_employee(session, data):
    try:
        temp_number = "TEMP-" + uuid4().hex
        print(f"Création d'un nouvel employé avec le numéro temporaire : {temp_number}")
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
    
def get_all_employees(session):
    return session.query(Employee).all()
    
def get_employees_by(session, attribute, value):
    if not hasattr(Employee, attribute):
        raise ValueError(f"L'attribut '{attribute}' n'existe pas dans le modèle Employee.")
    
    return session.query(Employee).filter(getattr(Employee, attribute) == value).all()

def update_employee_by_number(session, employee_number, attribute, value):
    if not hasattr(Employee, attribute):
        raise ValueError(f"L'attribut '{attribute}' n'existe pas dans le modèle Employee.")
    
    if attribute == "password":
        raise ValueError("Veuillez utiliser la fonction 'change_password' pour modifier le mot de passe.")

    if not attribute in ['first_name', 'last_name', 'email', 'role_id']:
        raise ValueError(f"L'attribut '{attribute}' n'est pas modifiable.")
    
    if attribute == "role_id" and value not in ["1", "2", "3"]:
        raise ValueError("L'ID de rôle doit être 1 (Commercial), 2 (Support) ou 3 (Gestion).")

    employee = session.query(Employee).filter(Employee.employee_number == employee_number).first()
    
    if not employee:
        raise ValueError(f"Aucun employé trouvé avec le numéro {employee_number}.")
        
    setattr(employee, attribute, value)
    session.commit()
    session.refresh(employee)
    return employee
        
def update_password(session, employee_number, new_password):
    employee = session.query(Employee).filter(Employee.employee_number == employee_number).first()
    
    if not employee:
        raise ValueError(f"Aucun employé trouvé avec le numéro {employee_number}.")

    employee.password = hash_password(new_password)
    session.commit()
    return True
    
def delete_employee_by_number(session, employee):
    session.delete(employee)
    session.commit()
