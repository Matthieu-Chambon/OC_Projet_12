import pytest
from app.crud import role as crud_role
from app.models.models import Role

def test_get_roles(session):
    """Vérifie que get_roles renvoie les rôles existants."""
    db_roles = crud_role.get_roles(session)
    expected_names = [
        "Commercial",
        "Support",
        "Management",
    ]
    assert [role.name for role in db_roles] == expected_names