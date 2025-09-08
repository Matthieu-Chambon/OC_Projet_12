from app.cli.core import cli
from app.cli.employee import employee


def test_command_employee_create(runner):
    """Test de la commande employee create"""
    runner.invoke(cli, ["login"], input="EMP0005\n")  # Employé manager
    result = runner.invoke(employee, ["create"], input="Pierre\nGaston\npierre.gaston@gmail.com\n1\n")
    assert result.exit_code == 0
    assert "Nouvel employé créé" in result.output


def test_command_employee_create_unauthenticated(runner):
    """Test de la commande employee create sans authentification."""
    result = runner.invoke(employee, ["create"], input="Pierre\nGaston\npierre.gaston@gmail.com\n1\n")
    assert result.exit_code == 0
    assert "Aucun token trouvé" in result.output


def test_command_employee_create_unauthorized(runner):
    """Test de la commande employee create sans autorisation."""
    runner.invoke(cli, ["login"], input="EMP0001\n")  # Employé commercial (non autorisé)
    result = runner.invoke(employee, ["create"], input="Pierre\nGaston\npierre.gaston@gmail.com\n1\n")
    assert result.exit_code == 0
    assert "Accès refusé" in result.output


def test_command_employee_list(runner):
    """Test de la commande employee list"""
    runner.invoke(cli, ["login"], input="EMP0001\n")  # Employé commercial
    result = runner.invoke(employee, ["list"])
    assert result.exit_code == 0
    assert all(employee in result.output for employee in ["Alice", "Marie", "Bob", "Zoe", "Charlie", "Nicolas"])


def test_command_employee_list_unauthenticated(runner):
    """Test de la commande employee list sans authentification."""
    result = runner.invoke(employee, ["list"])
    assert result.exit_code == 0
    assert "Aucun token trouvé" in result.output


def test_command_employee_list_filters_and_sorts(runner):
    """Test de la commande employee list avec des filtres et tris."""
    runner.invoke(cli, ["login"], input="EMP0001\n")  # Employé commercial
    result = runner.invoke(employee, ["list", "-f", "role_id=2", "-s", "first_name=desc"])
    assert result.exit_code == 0
    assert "2 résultat(s)" in result.output
    zoe_index = result.output.index("Zoe")
    bob_index = result.output.index("Bob")
    assert zoe_index < bob_index, "L'ordre attendu est Zoe avant Bob"


def test_command_employee_update(runner):
    """Test de la commande employee update"""
    runner.invoke(cli, ["login"], input="EMP0005\n")  # Employé manager
    result = runner.invoke(employee, ["update", "EMP0001", "last_name=Fournier", "email=alice.fournier@gmail.com"])
    assert result.exit_code == 0
    assert "Employé mis à jour" in result.output


def test_command_employee_update_unauthenticated(runner):
    """Test de la commande employee update sans authentification."""
    result = runner.invoke(employee, ["update", "EMP0001", "last_name=Fournier", "email=alice.fournier@gmail.com"])
    assert result.exit_code == 0
    assert "Aucun token trouvé" in result.output


def test_command_employee_update_unauthorized(runner):
    """Test de la commande employee update sans autorisation."""
    runner.invoke(cli, ["login"], input="EMP0001\n")  # Employé commercial (non autorisé)
    result = runner.invoke(employee, ["update", "EMP0001", "last_name=Fournier", "email=alice.fournier@gmail.com"])
    assert result.exit_code == 0
    assert "Accès refusé" in result.output


def test_command_employee_update_password(runner):
    """Test de la commande employee update-password"""
    runner.invoke(cli, ["login"], input="EMP0005\n")  # Employé manager
    result = runner.invoke(employee, ["update-password", "EMP0001"], input="new_password\nnew_password\n")
    assert result.exit_code == 0
    assert "Mot de passe mis à jour avec succès." in result.output


def test_command_employee_update_password_unauthenticated(runner):
    """Test de la commande employee update-password sans authentification."""
    result = runner.invoke(employee, ["update-password", "EMP0001"], input="new_password\nnew_password\n")
    assert result.exit_code == 0
    assert "Aucun token trouvé" in result.output


def test_command_employee_update_password_unauthorized(runner):
    """Test de la commande employee update-password sans autorisation."""
    runner.invoke(cli, ["login"], input="EMP0001\n")  # Employé commercial (non autorisé)
    result = runner.invoke(employee, ["update-password", "EMP0002"], input="new_password\nnew_password\n")
    assert result.exit_code == 0
    assert "Accès refusé" in result.output


def test_command_employee_delete(runner):
    """Test de la commande employee delete"""
    runner.invoke(cli, ["login"], input="EMP0005\n")  # Employé manager
    result = runner.invoke(employee, ["delete", "EMP0001"], input="oui\n")
    assert result.exit_code == 0
    assert "Employé supprimé" in result.output


def test_command_employee_delete_unauthenticated(runner):
    """Test de la commande employee delete sans authentification."""
    result = runner.invoke(employee, ["delete", "EMP0001"])
    assert result.exit_code == 0
    assert "Aucun token trouvé" in result.output


def test_command_employee_delete_unauthorized(runner):
    """Test de la commande employee delete sans autorisation."""
    runner.invoke(cli, ["login"], input="EMP0001\n")  # Employé commercial (non autorisé)
    result = runner.invoke(employee, ["delete", "EMP0001"])
    assert result.exit_code == 0
    assert "Accès refusé" in result.output
