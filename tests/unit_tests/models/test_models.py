from app.models.models import Role, Employee, Customer, Contract, Event


def test_role_repr(session):
    """Vérifie que la représentation en chaîne de caractères d'un rôle est correcte."""
    role = session.query(Role).filter_by(id=1).first()
    assert repr(role) == "<Role(id=1, name='Commercial', description='Responsable des ventes et de la relation client')>"

def test_employee_repr(session):
    """Vérifie que la représentation en chaîne de caractères d'un employé est correcte."""
    employee = session.query(Employee).filter_by(id=1).first()
    assert repr(employee) == "<Employee(id=1, employee_number='EMP0001', first_name='Alice', last_name='Dupont', email='alice.dupont@gmail.com', role_id=1)>"
    
def test_customer_repr(session):
    """Vérifie que la représentation en chaîne de caractères d'un client est correcte."""
    customer = session.query(Customer).filter_by(id=1).first()
    assert repr(customer) == "<Customer(id=1, first_name='David', last_name='Lefebvre', email='david.lefebvre@gmail.com', phone='0123456789', company='Acme Corp', sale_contact_id=1)>"

def test_contract_repr(session):
    """Vérifie que la représentation en chaîne de caractères d'un contrat est correcte."""
    contract = session.query(Contract).filter_by(id=1).first()
    assert repr(contract) == "<Contract(id=1, customer_id=1, sale_contact_id=1, total_amount=1000.00, remaining_amount=500.00, signed=True)>"

def test_event_repr(session):
    """Vérifie que la représentation en chaîne de caractères d'un événement est correcte."""
    event = session.query(Event).filter_by(id=1).first()
    assert repr(event) == "<Event(id=1, name='Fête de la musique', contract_id=1, support_contact_id=3, start_date='2023-06-21 21:00:00', end_date='2023-06-21 23:00:00', location='Parc des Princes', attendees=100, notes='Concert de rock')>"