from app.cli.core import cli
from app.cli.contract import contract


def test_command_contract_create(runner):
    """Test de la commande contract create"""
    runner.invoke(cli, ["login"], input="EMP0005\n")  # Employé manager
    result = runner.invoke(contract, ["create"], input="1\n5000\n3000\noui\n")
    assert result.exit_code == 0
    assert "Nouveau contrat créé" in result.output


def test_command_contract_create_unauthenticated(runner):
    """Test de la commande contract create sans authentification."""
    result = runner.invoke(contract, ["create"], input="1\n5000\n3000\noui\n")
    assert result.exit_code == 0
    assert "Aucun token trouvé." in result.output


def test_command_contract_create_unauthorized(runner):
    """Test de la commande contract create sans autorisation."""
    runner.invoke(cli, ["login"], input="EMP0001\n")  # Employé commercial (non autorisé)
    result = runner.invoke(contract, ["create"], input="1\n5000\n3000\noui\n")
    assert result.exit_code == 0
    assert "Accès refusé" in result.output


def test_command_contract_list(runner):
    """Test de la commande contract list"""
    runner.invoke(cli, ["login"], input="EMP0001\n")  # Employé commercial
    result = runner.invoke(contract, ["list"])
    assert result.exit_code == 0
    assert "Liste des contrats" in result.output
    assert "5 résultat(s)" in result.output


def test_command_contract_list_unauthenticated(runner):
    """Test de la commande contract list sans authentification."""
    result = runner.invoke(contract, ["list"])
    assert result.exit_code == 0
    assert "Aucun token trouvé." in result.output


def test_command_contract_list_filters_and_sorts(runner):
    """Test de la commande contract list avec des filtres et des tris."""
    runner.invoke(cli, ["login"], input="EMP0001\n")  # Employé commercial
    result = runner.invoke(contract, ["list", "--filter", "sale_contact_id=1", "--sort", "total_amount=desc"])
    assert result.exit_code == 0
    assert "3 résultat(s)" in result.output
    index = [
        result.output.index("2500"),
        result.output.index("2000"),
        result.output.index("1000")
    ]
    assert index[0] < index[1], "L'ordre attendu est 2500 avant 2000"
    assert index[1] < index[2], "L'ordre attendu est 2000 avant 1000"


def test_command_contract_update(runner):
    """Test de la commande contract update"""
    runner.invoke(cli, ["login"], input="EMP0005\n")  # Employé manager
    result = runner.invoke(contract, ["update", "1", "total_amount=6000", "remaining_amount=4000"])
    assert result.exit_code == 0
    assert "Contrat mis à jour" in result.output
    assert "6000" in result.output
    assert "4000" in result.output


def test_command_contract_update_unauthenticated(runner):
    """Test de la commande contract update sans authentification."""
    result = runner.invoke(contract, ["update", "1", "total_amount=6000", "remaining_amount=4000"])
    assert result.exit_code == 0
    assert "Aucun token trouvé." in result.output


def test_command_contract_update_unauthorized(runner):
    """Test de la commande contract update sans autorisation."""
    runner.invoke(cli, ["login"], input="EMP0003\n")  # Employé support (non autorisé)
    result = runner.invoke(contract, ["update", "1", "total_amount=6000", "remaining_amount=4000"])
    assert result.exit_code == 0
    assert "Accès refusé" in result.output


def test_command_contract_delete(runner):
    """Test de la commande contract delete"""
    runner.invoke(cli, ["login"], input="EMP0005\n")  # Employé manager
    result = runner.invoke(contract, ["delete", "1"], input="oui\n")
    assert result.exit_code == 0
    assert "Contrat supprimé" in result.output


def test_command_contract_delete_unauthenticated(runner):
    """Test de la commande contract delete sans authentification."""
    result = runner.invoke(contract, ["delete", "1"], input="oui\n")
    assert result.exit_code == 0
    assert "Aucun token trouvé." in result.output


def test_command_contract_delete_unauthorized(runner):
    """Test de la commande contract delete sans autorisation."""
    runner.invoke(cli, ["login"], input="EMP0001\n")  # Employé commercial (non autorisé)
    result = runner.invoke(contract, ["delete", "1"], input="oui\n")
    assert result.exit_code == 0
    assert "Accès refusé" in result.output
