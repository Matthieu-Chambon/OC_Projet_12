from app.db.database import engine
from app.models.models import Base, Employee, Customer, Event
from app.db.database import Session
from sqlalchemy_utils import database_exists, create_database
from app.auth.password import hash_password


# Windows powershell
# $env:PYTHONPATH = "."
# python .\app\db\fake_data.py

db = Session()

employees = [
    Employee(
        employee_number="EMP001",
        first_name="Alice",
        last_name="Dupont",
        email="alice.dupont@gmail.com",
        password=hash_password("password"),
        role_id=1, # Commercial
    ),
    Employee(
        employee_number="EMP002",
        first_name="Bob",
        last_name="Martin",
        email="bob.martin@gmail.com",
        password=hash_password("password"),
        role_id=2, # Support
    ),
    Employee(
        employee_number="EMP003",
        first_name="Charlie",
        last_name="Durand",
        email="charlie.durand@gmail.com",
        password=hash_password("password"),
        role_id=3, # Gestion
    )
]

customers = [
    Customer(
        first_name="David",
        last_name="Lefebvre",
        email="david.lefebvre@gmail.com",
        phone="0123456789",
        company="Acme Corp",
        sale_contact_id=1
    ),
    Customer(
        first_name="Eva",
        last_name="Moreau",
        email="eva.moreau@gmail.com",
        phone="9876543210",
        company="Globex Inc",
        sale_contact_id=1
    ),
    Customer(
        first_name="Frank",
        last_name="Bernard",
        email="frank.bernard@gmail.com",
        phone="0123456789",
        company="Initech",
        sale_contact_id=1
    )
]

db.add_all(employees)
db.add_all(customers)

db.commit()
db.close()

print("Données de test insérées avec succès.")