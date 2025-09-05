from app.cli.core import cli
from app.cli.role import role


def test_command_role_list(runner):
    """Test de la commande role list."""
    runner.invoke(cli, ["login"], input="EMP0001\n")  # Employé commercial
    result = runner.invoke(role, ["list"])
    assert result.exit_code == 0
    assert "Liste des rôles" in result.output
    assert all(role in result.output for role in ["Commercial", "Support", "Management"])

def test_command_role_list_unauthenticated(runner):
    """Test de la commande role list sans authentification."""
    result = runner.invoke(role, ["list"])
    assert result.exit_code == 0
    assert "Aucun token trouvé" in result.output