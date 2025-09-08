import pytest
from app.crud import contract as crud_contract
from app.models.models import Contract


def test_create_contract(session):
    """Vérifie que la création d'un contrat fonctionne."""
    data = {
        "customer_id": 1,
        "total_amount": 1500.0,
        "remaining_amount": 1500.0,
        "signed": False
    }

    new_contract = crud_contract.create_contract(
        session,
        data
    )

    assert new_contract.id is not None
    assert new_contract.customer_id == data["customer_id"]
    assert new_contract.total_amount == data["total_amount"]
    assert new_contract.remaining_amount == data["remaining_amount"]
    assert new_contract.signed == data["signed"]


def test_create_contract_fail(session):
    """Vérifie que la création d'un contrat échoue avec des données invalides."""
    data = {
        "customer_id": 999,  # Un client qui n'existe pas
        "total_amount": 1500.0,
        "remaining_amount": 1500.0,
        "signed": False
    }

    with pytest.raises(ValueError):
        crud_contract.create_contract(
            session,
            data
        )


def test_get_contracts(session):
    """Vérifie que la récupération des contrats fonctionne."""
    contracts = crud_contract.get_contracts(session)
    assert contracts is not None
    assert len(contracts) == 5


def test_get_contracts_with_filters(session):
    """Vérifie que la récupération des contrats avec des filtres fonctionne."""
    filters = {
        "customer_id": "1"
    }
    contracts = crud_contract.get_contracts(session, filters=filters)
    assert contracts is not None
    assert len(contracts) == 2
    assert all(contract.customer_id == 1 for contract in contracts)


def test_get_contracts_with_sorts(session):
    """Vérifie que la récupération des contrats avec des tris fonctionne."""
    sorts = {
        "total_amount": "desc"
    }
    contracts = crud_contract.get_contracts(session, sorts=sorts)
    assert contracts is not None
    assert len(contracts) == 5
    assert contracts == sorted(contracts, key=lambda c: c.total_amount, reverse=True)


def test_get_contracts_with_filters_and_sorts(session):
    """Vérifie que la récupération des contrats avec des filtres et des tris fonctionne."""
    filters = {
        "customer_id": "1"
    }
    sorts = {
        "total_amount": "desc"
    }
    contracts = crud_contract.get_contracts(session, filters=filters, sorts=sorts)
    assert contracts is not None
    assert len(contracts) == 2
    assert all(contract.customer_id == 1 for contract in contracts)
    assert contracts == sorted(contracts, key=lambda c: c.total_amount, reverse=True)


def test_update_contract(session):
    """Vérifie que la mise à jour d'un contrat fonctionne."""
    updates = {
        "remaining_amount": "1000.0",
        "signed": "True"
    }

    updated_contract = crud_contract.update_contract(
        session,
        contract_id=4,
        updates=updates,
        req_emp_num="EMP0002"  # Marie Curie, contact de vente du contrat
    )

    assert updated_contract.remaining_amount == 1000.0
    assert updated_contract.signed is True


def test_update_contract_fail(session):
    """Vérifie que la mise à jour d'un contrat échoue avec des données invalides."""
    updates = {
        "remaining_amount": "invalid_amount",
        "signed": "not_a_boolean"
    }

    with pytest.raises(ValueError):
        crud_contract.update_contract(
            session,
            contract_id=4,
            updates=updates,
            req_emp_num="EMP0002"  # Marie Curie, contact de vente du contrat
        )


def test_update_contract_unauthorized(session):
    """Vérifie que la mise à jour d'un contrat échoue si l'utilisateur n'est pas autorisé."""
    updates = {
        "remaining_amount": "1000.0",
        "signed": "True"
    }

    with pytest.raises(ValueError):
        crud_contract.update_contract(
            session,
            contract_id=4,
            updates=updates,
            req_emp_num="EMP0003"  # Un employé non autorisé
        )


def test_delete_contract(session):
    """Vérifie que la suppression d'un contrat fonctionne."""
    contract = session.query(Contract).filter(Contract.id == 1).first()
    assert contract is not None

    crud_contract.delete_contract(
        session,
        contract,
    )

    deleted_contract = session.query(Contract).filter(Contract.id == 1).first()
    assert deleted_contract is None
