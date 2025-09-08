# Projet 12 – Développez une architecture back-end sécurisée avec Python et SQL

## 📚 Description

Ce projet est une **application CRM en ligne de commande** développée pour **Epic Events**, une société spécialisée dans la gestion d’événements.

L’outil permet aux employés (commerciaux, support, management) de :

* gérer les **clients** et leurs informations,
* suivre les **contrats** et leur statut (signés ou non),
* organiser et superviser les **événements** liés aux clients.

L’accès est sécurisé grâce à un système d’**authentification avec rôles et permissions**, et toutes les opérations sensibles sont **journalisées via Sentry**.
Le projet a été développé en **Python** avec **SQLAlchemy** pour la base de données, et suit les bonnes pratiques de qualité et de sécurité (tests automatisés, PEP8, variables d’environnement).

---

## 📥 Installation et exécution

### 0️⃣ Prérequis

- [Python 3.12.4+](https://www.python.org/downloads/)
- [MySQL](https://dev.mysql.com/downloads/installer/) Installé et en cours d'exécution
- Un **utilisateur** MySQL avec les droits nécessaires pour créer des bases, des tables et des utilisateurs

### 1️⃣ Cloner le projet
```bash
git clone https://github.com/Matthieu-Chambon/OC_Projet_12
cd OC_Projet_12
```

### 2️⃣ Créer un environnement virtuel

```bash
python -m venv env
source env/bin/activate   # macOS/Linux
env\Scripts\activate      # Windows
```

### 3️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurer les variables d’environnement

Editer le fichier `.env` à la racine du projet avec vos identifiants MySQL :

```bash
DB_USER=root          # Nom d'utilisateur MySQL
DB_PASSWORD=password  # Mot de passe MySQL
DB_HOST=localhost     # Hôte (laisser localhost en local)
DB_NAME=epic_events   # Nom de la base (sera créée si inexistante)
```

### 5️⃣ Initialiser la base de données

```bash
python -m app.db.init_db
```

👉 Ce script :

* crée la base epic_events si elle n’existe pas
* supprime et recrée toutes les tables
* insère les rôles de base (Commercial, Support, Management)

### 6️⃣ (Optionnel) Générer des données de test

```cmd
python -m app.db.fake_data
```

### 7️⃣ Exécuter des premières commandes

```bash
python main.py --help         # Liste des commandes
python main.py login          # Connexion à l'application
python main.py customer list  # Afficher la liste des clients
```

---

## 📂 Structure du projet

```bash
.
├── app/                  # Code source principal de l'application
│   ├── auth/             # Gestion de l'authentification et des tokens
│   ├── cli/              # Commandes CLI (interface en ligne de commande)
│   ├── crud/             # Opérations CRUD (accès et modification des données)
│   ├── db/               # Gestion de la base de données (connexion, init, données de test)
│   ├── models/           # Définition des modèles SQLAlchemy (tables)
│   ├── ui/               # Vues pour l'affichage des données (avec Rich)
│   └── config.py         # Configuration globale de l'application
│
├── tests/                 # Tests automatisés (Pytest)
│   ├── integration_tests/ # Tests d’intégration
│   └── unit_tests/        # Tests unitaires
│
├── main.py               # Point d'entrée de l’application
├── requirements.txt      # Dépendances du projet
├── README.md             # Documentation du projet
└── .env                  # Variables d'environnement (DB, Sentry, JWT)
```

---

## 🧪 Tests

### Structure des tests :

* `unit_tests/` : tests unitaires
* `integration_tests/` : tests d’intégration

### Lancer les tests

```bash
pytest
```

---

## 📊 Génération des rapports

### Couverture de tests :

```bash
pytest --cov=. --cov-report html

start htmlcov/index.html     # Windows
open htmlcov/index.html      # macOS
xdg-open htmlcov/index.html  # linux

```

### Respect de la norme PEP8 :

```bash
flake8 --format=html --htmldir=flake-report

start flake-report/index.html     # Windows
open flake-report/index.html      # macOS
xdg-open flake-report/index.html  # linux
```

---

## 🛠️ Technologies utilisées

* [Python](https://www.python.org/)  
* [SQLAlchemy](https://www.sqlalchemy.org/)   
* [MySQL](https://www.mysql.com/)  
* [PyMySQL](https://pymysql.readthedocs.io/)  
* [Click](https://click.palletsprojects.com/)  
* [Rich](https://rich.readthedocs.io/)  
* [PyJWT](https://pyjwt.readthedocs.io/)  
* [Passlib](https://passlib.readthedocs.io/)  
* [Argon2](https://argon2-cffi.readthedocs.io/)  
* [Sentry](https://docs.sentry.io/platforms/python/)  
* [pytest](https://docs.pytest.org/)  
* [python-dotenv](https://saurabh-kumar.com/python-dotenv/)  

---

## ✅ Conformité

* ✅ Respect des normes **PEP8** (via Flake8)
* ✅ Base de données sécurisée avec **SQLAlchemy ORM**
* ✅ Authentification robuste (hachage + salage, **JWT**)
* ✅ Gestion des rôles et **permissions strictes**
* ✅ Journalisation des erreurs et actions avec **Sentry**
* ✅ Données sensibles protégées (**.env**, pas en dur dans le code)
* ✅ Code testé (**Pytest**, couverture unitaire & intégration)