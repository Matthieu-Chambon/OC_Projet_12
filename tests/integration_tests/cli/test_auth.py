from app.cli.core import cli


def test_command_login(runner, mocker):
    """Test de la commande login"""
    mocker.patch("app.cli.auth.getpass", side_effect=["password"])
    result = runner.invoke(cli, ["login"], input="EMP0001\n")
    assert result.exit_code == 0
    assert "Connexion réussie pour l'employé" in result.output


def test_command_login_invalid_employee(runner, mocker):
    """Test de la commande login avec un employé invalide"""
    mocker.patch("app.cli.auth.getpass", side_effect=["password"])
    result = runner.invoke(cli, ["login"], input="INVALID\n")
    assert result.exit_code == 0
    assert "Aucun employé trouvé avec le numéro INVALID." in result.output


def test_command_login_invalid_password(runner, mocker):
    """Test de la commande login avec un mot de passe invalide"""
    mocker.patch("app.cli.auth.getpass", side_effect=["wrong_password"])
    result = runner.invoke(cli, ["login"], input="EMP0001\n")
    assert result.exit_code == 0
    assert "Échec de la connexion" in result.output


def test_command_change_password(runner, mocker):
    """Test de la commande change-password"""
    mocker.patch("app.cli.auth.getpass", side_effect=["password"])
    runner.invoke(cli, ["login"], input="EMP0001\n")

    mocker.patch("app.cli.auth.getpass", side_effect=["password", "new_password", "new_password"])
    result = runner.invoke(cli, ["change-password"])

    assert result.exit_code == 0
    assert "Mot de passe mis à jour avec succès." in result.output


def test_command_change_password_invalid_previous(runner, mocker):
    """Test de la commande change-password avec un mot de passe précédent invalide"""
    mocker.patch("app.cli.auth.getpass", side_effect=["password"])
    runner.invoke(cli, ["login"], input="EMP0001\n")

    mocker.patch("app.cli.auth.getpass", side_effect=["wrong_password", "new_password", "new_password"])
    result = runner.invoke(cli, ["change-password"])

    assert result.exit_code == 0
    assert "Échec de la mise à jour du mot de passe : mot de passe précédent incorrect." in result.output


def test_command_change_password_mismatch(runner, mocker):
    """Test de la commande change-password avec des mots de passe qui ne correspondent pas"""
    mocker.patch("app.cli.auth.getpass", side_effect=["password"])
    runner.invoke(cli, ["login"], input="EMP0001\n")

    mocker.patch("app.cli.auth.getpass", side_effect=["password", "new_password", "different_password",
                                                      "new_password", "new_password"])
    result = runner.invoke(cli, ["change-password"])

    assert result.exit_code == 0
    assert "Mot de passe mis à jour avec succès." in result.output


def test_command_change_password_unauthenticated(runner, mocker):
    """Test de la commande change-password sans authentification."""
    mocker.patch("app.cli.auth.getpass", side_effect=["wrong_password", "new_password", "new_password"])
    result = runner.invoke(cli, ["change-password"])
    assert result.exit_code == 0
    assert "Aucun token trouvé." in result.output
