import pytest
from app.crud import employee as crud_employee
from app.models.models import Employee


def test_create_employee(session):
    """Vérifie que la création d'un employé fonctionne."""

    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@gmail.com",
        "password": "password",
        "role_id": 1,
    }

    new_employee = crud_employee.create_employee(
        session,
        data
    )

    assert new_employee.id is not None
    assert new_employee.employee_number == "EMP0007"
    assert new_employee.first_name == data["first_name"]
    assert new_employee.last_name == data["last_name"]
    assert new_employee.email == data["email"]
    assert new_employee.role_id == data["role_id"]


def test_create_employee_fail(session):
    """Vérifie que la création d'un employé échoue avec des données invalides."""
    data = {
        "first_name": "Alice",
        "last_name": "Dupont",
        "email": "alice.dupont@gmail.com",  # Email déjà utilisé
        "password": "password",
        "role_id": 999  # Un rôle qui n'existe pas
    }

    with pytest.raises(ValueError):
        crud_employee.create_employee(
            session,
            data
        )


def test_get_employees(session):
    """Vérifie que la récupération d'un employé fonctionne."""
    employees = crud_employee.get_employees(session)
    assert employees is not None
    assert len(employees) == 6


def test_get_employees_with_filters(session):
    """Vérifie que la récupération d'employés avec des filtres fonctionne."""
    filters = {
        "first_name": "Alice"
    }
    employees = crud_employee.get_employees(session, filters=filters)
    assert employees is not None
    assert len(employees) == 1
    assert employees[0].first_name == "Alice"


def test_get_employees_with_sorts(session):
    """Vérifie que la récupération d'employés avec des tris fonctionne."""
    sorts = {
        "last_name": "asc"
    }
    employees = crud_employee.get_employees(session, sorts=sorts)
    assert employees is not None
    assert len(employees) == 6
    assert [employee.last_name for employee in employees] == ["Curie", "Dupont", "Durand", "Guerin", "Hulot", "Martin"]


def test_get_employee_with_filters_and_sorts(session):
    """Vérifie que la récupération d'employés avec des filtres et des tris fonctionne."""
    filters = {
        "role_id": "2"
    }
    sorts = {
        "email": "desc"
    }
    employees = crud_employee.get_employees(session, filters=filters, sorts=sorts)
    assert employees is not None
    assert len(employees) == 2
    assert [employee.email for employee in employees] == ["zoe.guerin@gmail.com", "bob.martin@gmail.com"]


def test_update_employee(session):
    """Vérifie que la mise à jour d'un employé fonctionne."""
    updates = {
        "last_name": "Smith",
        "email": "alice.smith@gmail.com"
    }

    updated_employee = crud_employee.update_employee(
        session,
        1,
        updates
    )

    assert updated_employee.last_name == updates["last_name"]
    assert updated_employee.email == updates["email"]


def test_update_employee_fail(session):
    """Vérifie que la mise à jour d'un employé échoue avec des données invalides."""
    updates = {
        "password": "newpassword"  # Le mot de passe ne peut pas être mis à jour ici
    }

    with pytest.raises(ValueError):
        crud_employee.update_employee(
            session,
            1,
            updates
        )


def test_update_password_employee(session):
    """Vérifie que la mise à jour du mot de passe d'un employé fonctionne."""
    employee = session.query(Employee).filter(Employee.id == 1).first()
    assert employee is not None
    old_hashed_password = employee.password

    crud_employee.update_password(
        session,
        employee,
        "new_password"
    )

    updated_employee = session.query(Employee).filter(Employee.id == 1).first()
    assert updated_employee is not None
    assert updated_employee.password != old_hashed_password


def test_delete_employee(session):
    """Vérifie que la suppression d'un employé fonctionne."""
    employee = session.query(Employee).filter(Employee.id == 1).first()
    assert employee is not None

    crud_employee.delete_employee(
        session,
        employee
    )

    deleted_employee = session.query(Employee).filter(Employee.id == 1).first()
    assert deleted_employee is None
