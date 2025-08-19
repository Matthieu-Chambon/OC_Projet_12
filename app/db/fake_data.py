from app.db.database import engine
from app.models.models import Base, Employee, Customer, Contract, Event
from app.db.database import Session
from sqlalchemy_utils import database_exists, create_database
from app.auth.password import hash_password


# Windows powershell
# $env:PYTHONPATH = "."
# python .\app\db\fake_data.py

db = Session()

employees = [
    Employee(
        employee_number="EMP0001",
        first_name="Alice",
        last_name="Dupont",
        email="alice.dupont@gmail.com",
        password=hash_password("password"),
        role_id=1, # Commercial
    ),
    Employee(
        employee_number="EMP0002",
        first_name="Marie",
        last_name="Curie",
        email="marie.curie@gmail.com",
        password=hash_password("password"),
        role_id=1, # Commercial
    ),
    Employee(
        employee_number="EMP0003",
        first_name="Bob",
        last_name="Martin",
        email="bob.martin@gmail.com",
        password=hash_password("password"),
        role_id=2, # Support
    ),
    Employee(
        employee_number="EMP0004",
        first_name="Zoe",
        last_name="Guerin",
        email="zoe.guerin@gmail.com",
        password=hash_password("password"),
        role_id=2, # Support
    ),
    Employee(
        employee_number="EMP0005",
        first_name="Charlie",
        last_name="Durand",
        email="charlie.durand@gmail.com",
        password=hash_password("password"),
        role_id=3, # Gestion
    ),
    Employee(
        employee_number="EMP0006",
        first_name="Nicolas",
        last_name="Hulot",
        email="nicolas.hulot@gmail.com",
        password=hash_password("password"),
        role_id=3, # Gestion
    ),
]

customers = [
    Customer(
        first_name="David",
        last_name="Lefebvre",
        email="david.lefebvre@gmail.com",
        phone="0123456789",
        company="Acme Corp",
        sale_contact_id=1 # Alice Dupont
    ),
    Customer(
        first_name="Eva",
        last_name="Moreau",
        email="eva.moreau@gmail.com",
        phone="9876543210",
        company="Globex Inc",
        sale_contact_id=1 # Alice Dupont
    ),
    Customer(
        first_name="Frank",
        last_name="Bernard",
        email="frank.bernard@gmail.com",
        phone="0123456789",
        company="Initech",
        sale_contact_id=2 # Marie Curie
    )
]

contracts = [
    Contract(
        customer_id=1, # David Lefebvre
        sale_contact_id=1, # Alice Dupont
        total_amount=1000.00,
        remaining_amount=500.00,
        signed=True
    ),
    Contract(
        customer_id=1, # David Lefebvre
        sale_contact_id=1, # Alice Dupont
        total_amount=2000.00,
        remaining_amount=1500.00,
        signed=False
    ),
    Contract(
        customer_id=3, # Frank Bernard
        sale_contact_id=2, # Marie Curie
        total_amount=3000.00,
        remaining_amount=3000.00,
        signed=False
    )
]

events = [
    Event(
        name="Fête de la musique",
        contract_id=1,
        support_contact_id=3, # Bob Martin
        start_date="2023-06-21 21:00:00",
        end_date="2023-06-21 23:00:00",
        location="Parc des Princes",
        attendees=100,
        note="Concert de rock",
    ),
    Event( # Pas de support_contact_id
        name="Réunion d'équipe",
        contract_id=2,
        start_date="2023-06-22 10:00:00",
        end_date="2023-06-22 12:00:00",
        location="Salle de conférence",
        attendees=10,
        note="Discussion des objectifs du trimestre"
    )
]


db.add_all(employees)
db.add_all(customers)
db.add_all(contracts)
db.add_all(events)
db.commit()
db.close()

print("Données de test insérées avec succès.")