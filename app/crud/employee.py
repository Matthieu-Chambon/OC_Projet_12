from app.models.models import Employee
from app.auth.password import hash_password

def create_employee(session, data):
    try:
        new_employee = Employee(**data)
        new_employee.password = hash_password(new_employee.password)
        session.add(new_employee)
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
    
    if not attribute in ['employee_number', 'first_name', 'last_name', 'email', 'role_id']:
        raise ValueError(f"L'attribut '{attribute}' n'est pas modifiable.")

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
    
def delete_employee_by_number(session, employee_number):
    employee = session.query(Employee).filter(Employee.employee_number == employee_number).first()
    
    if not employee:
        raise ValueError(f"Aucun employé trouvé avec le numéro {employee_number}.")

    session.delete(employee)
    session.commit()
    return employee
