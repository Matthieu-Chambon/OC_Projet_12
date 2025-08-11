from app.db.database import engine
from app.models.models import Base, Role
from app.db.database import Session
from sqlalchemy_utils import database_exists, create_database


# Windows powershell
# $env:PYTHONPATH = "."
# python .\app\db\create_db.py

if not database_exists(engine.url):
    print("La base de données n'existe pas, création en cours...")
    create_database(engine.url)

print("Suppression de toutes les tables...")
Base.metadata.drop_all(bind=engine)

print("Création de toutes les tables...")
Base.metadata.create_all(bind=engine)

print("Peuplement des données...")
db = Session()

roles = [
    Role(name="Commercial", description="Responsable des ventes et de la relation client"),
    Role(name="Support", description="Assistance technique et support client"),
    Role(name="Management", description="Gestion des opérations et des ressources humaines")
]

db.add_all(roles)

db.commit()
db.close()
