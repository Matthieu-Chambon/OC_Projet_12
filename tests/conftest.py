
import os
import pytest
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.auth.password import hash_password
from app.models.models import Base, Role, Employee, Customer, Contract, Event
from dotenv import load_dotenv


load_dotenv()

TEST_DATABASE_URL = "mysql+pymysql://test_user:test_password@localhost/epic_events_test"

def pytest_sessionstart(session):
    """Hook pour s'assurer que la base de données de test est initialisée avant les tests."""
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = "epic_events_test"
    
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        autocommit=True
    )
    
    with connection.cursor() as cursor:
        # Vérifie si la DB existe
        cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            # Crée la DB et l'utilisateur de test
            cursor.execute(f"CREATE DATABASE {db_name};")
            cursor.execute("CREATE USER IF NOT EXISTS 'test_user'@'localhost' IDENTIFIED BY 'test_password';")
            cursor.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO 'test_user'@'localhost';")
            cursor.execute("FLUSH PRIVILEGES;")

    connection.close()

@pytest.fixture
def database():
    """Fixture qui fournit une session SQLAlchemy avec une BDD en mémoire."""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Recrée toutes les tables
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    db = TestSession()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def session(database):
    """Fixture qui remplit la base de données pour les tests."""
    roles = [
        Role(name="Commercial", description="Responsable des ventes et de la relation client"),
        Role(name="Support", description="Assistance technique et support client"),
        Role(name="Management", description="Gestion des opérations et des ressources humaines")
    ]

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
            signed=True
        ),
        Contract(
            customer_id=2, # Eva Moreau
            sale_contact_id=1, # Alice Dupont
            total_amount=2500.00,
            remaining_amount=2500.00,
            signed=True
        ),
        Contract(
            customer_id=3, # Frank Bernard
            sale_contact_id=2, # Marie Curie
            total_amount=3000.00,
            remaining_amount=3000.00,
            signed=False
        ),
        Contract(
            customer_id=3, # Frank Bernard
            sale_contact_id=2, # Marie Curie
            total_amount=6000.00,
            remaining_amount=0.00,
            signed=True
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
            notes="Concert de rock",
        ),
        Event( # Pas de support_contact_id
            name="Réunion d'équipe",
            contract_id=2,
            start_date="2023-06-22 10:00:00",
            end_date="2023-06-22 12:00:00",
            location="Salle de conférence",
            attendees=10,
            notes="Discussion des objectifs du trimestre"
        ),
        Event( # Pas de support_contact_id
            name="Atelier de formation",
            contract_id=3,
            start_date="2025-08-23 14:00:00",
            end_date="2025-08-23 16:00:00",
            location="Salle de formation",
            attendees=20,
            notes="Formation sur les nouvelles fonctionnalités"
        )
    ]

    database.add_all(roles)
    database.add_all(employees)
    database.add_all(customers)
    database.add_all(contracts)
    database.add_all(events)
    database.commit()
    
    return database

import pytest
from click.testing import CliRunner

@pytest.fixture
def runner(session, mocker):
    """Fixture qui fournit un CliRunner avec une base de données pré-remplie et des fonctions patchées."""
    # Patch de la session dans les modules CLI
    mocker.patch("app.cli.core.db", session)
    mocker.patch("app.cli.auth.db", session)
    mocker.patch("app.cli.role.db", session)
    mocker.patch("app.cli.employee.db", session)
    mocker.patch("app.cli.customer.db", session)
    mocker.patch("app.cli.contract.db", session)
    mocker.patch("app.cli.event.db", session)

    # Patch des fonctions getpass
    mocker.patch("app.cli.auth.getpass", side_effect=["password"])
    mocker.patch("app.cli.employee.getpass", side_effect=["password", "password"])

    token_file = ".session_token"
    
    # Suppression du fichier de token de session avant un test
    if os.path.exists(token_file):
        os.remove(token_file)

    yield CliRunner()

    # Suppression du fichier de token de session après un test
    token_file = ".session_token"
    if os.path.exists(token_file):
        os.remove(token_file)
