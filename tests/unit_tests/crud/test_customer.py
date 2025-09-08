import pytest
from app.crud import customer as crud_customer
from app.models.models import Customer


def test_create_customer(session):
    """Vérifie que la création d'un client fonctionne."""
    data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@gmail.com",
        "phone": "0987654321",
        "company": "Doe Enterprises",
        "sale_contact_id": 1
    }

    new_customer = crud_customer.create_customer(
        session,
        data
    )

    assert new_customer.id is not None
    assert new_customer.first_name == data["first_name"]
    assert new_customer.last_name == data["last_name"]
    assert new_customer.email == data["email"]
    assert new_customer.phone == data["phone"]
    assert new_customer.company == data["company"]
    assert new_customer.sale_contact_id == data["sale_contact_id"]


def test_create_customer_fail(session):
    """Vérifie que la création d'un client échoue avec des données invalides."""
    data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@gmail.com",
        "phone": "0987654321",
        "company": "Doe Enterprises",
        "sale_contact_id": 999  # Un contact de vente qui n'existe pas
    }

    with pytest.raises(ValueError):
        crud_customer.create_customer(
            session,
            data
        )


def test_get_customers(session):
    """Vérifie que la récupération d'un client fonctionne."""
    customers = crud_customer.get_customers(session)
    assert customers is not None
    assert len(customers) == 3


def test_get_customers_with_filters(session):
    """Vérifie que la récupération des clients avec des filtres fonctionne."""
    filters = {
        "company": "Globex Inc",
        "sale_contact_id": "1"
    }
    customers = crud_customer.get_customers(session, filters)
    assert customers is not None
    assert len(customers) == 1
    assert customers[0].first_name == "Eva"
    assert customers[0].last_name == "Moreau"


def test_get_customers_with_sorts(session):
    """Vérifie que la récupération des clients avec des tris fonctionne."""
    sorts = {
        "last_name": "asc"
    }
    customers = crud_customer.get_customers(session, sorts=sorts)
    assert customers is not None
    assert len(customers) == 3
    assert [customer.last_name for customer in customers] == ["Bernard", "Lefebvre", "Moreau"]


def test_get_customers_with_filters_and_sorts(session):
    """Vérifie que la récupération des clients avec des filtres et des tris fonctionne."""
    filters = {
        "sale_contact_id": "1"
    }
    sorts = {
        "last_name": "desc"
    }
    customers = crud_customer.get_customers(session, filters=filters, sorts=sorts)
    assert customers is not None
    assert len(customers) == 2
    assert [customer.last_name for customer in customers] == ["Moreau", "Lefebvre"]


def test_update_customer(session):
    """Vérifie que la mise à jour d'un client fonctionne."""
    updates = {
        "phone": "0898989898",
        "company": "Lefebvre Inc.",
    }

    updated_customer = crud_customer.update_customer(
        session,
        1,
        updates,
        "EMP0001"  # Alice Dupont, contact de vente du client
    )

    assert updated_customer is not None
    assert updated_customer.phone == updates["phone"]
    assert updated_customer.company == updates["company"]


def test_update_customer_fail(session):
    """Vérifie que la mise à jour d'un client échoue avec des données invalides."""
    updates = {
        "id": "80"  # Impossible de modifier l'ID d'un client
    }

    with pytest.raises(ValueError):
        crud_customer.update_customer(
            session,
            1,
            updates,
            "EMP0005"  # Un manager ayant les droits
        )


def test_update_customer_unauthorized(session):
    """Vérifie que la mise à jour d'un client échoue si l'utilisateur n'est pas autorisé."""
    updates = {
        "phone": "0898989898",
        "company": "Lefebvre Inc.",
    }

    with pytest.raises(ValueError):
        crud_customer.update_customer(
            session,
            1,
            updates,
            "EMP0003"  # Un employé (Support) sans droits
        )


def test_delete_customer(session):
    """Vérifie que la suppression d'un client fonctionne."""
    customer = session.query(Customer).filter(Customer.id == 1).first()
    assert customer is not None

    crud_customer.delete_customer(
        session,
        customer,
    )

    deleted_customer = session.query(Customer).filter(Customer.id == 1).first()
    assert deleted_customer is None
