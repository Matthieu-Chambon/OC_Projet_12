from app.cli.core import cli
from app.cli.customer import customer

def test_command_customer_create(runner):
    """Test de la commande customer create"""
    runner.invoke(cli, ["login"], input="EMP0005\n")  # Employé commercial
    result = runner.invoke(customer, ["create"], input="Pierre\nGaston\npierre.gaston@gmail.com\n0601020304\nPierre's shop")
    assert result.exit_code == 0
    assert "Nouveau client créé" in result.output

def test_command_customer_create_unauthenticated(runner):
    """Test de la commande customer create sans authentification."""
    result = runner.invoke(customer, ["create"], input="Pierre\nGaston\npierre.gaston@gmail.com\n0601020304\nPierre's shop")
    assert result.exit_code == 0
    assert "Aucun token trouvé." in result.output
    
def test_command_customer_create_unauthorized(runner):
    """Test de la commande customer create sans autorisation."""
    runner.invoke(cli, ["login"], input="EMP0003\n")  # Employé support (non autorisé)
    result = runner.invoke(customer, ["create"], input="Pierre\nGaston\npierre.gaston@gmail.com\n0601020304\nPierre's shop")
    assert result.exit_code == 0
    assert "Accès refusé" in result.output
    
def test_command_customer_list(runner):
    """Test de la commande customer list."""
    runner.invoke(cli, ["login"], input="EMP0001\n")  # Employé commercial
    result = runner.invoke(customer, ["list"])
    assert result.exit_code == 0
    assert all(customer in result.output for customer in ["David", "Eva", "Frank"])
    
def test_command_customer_list_unauthenticated(runner):
    """Test de la commande customer list sans authentification."""
    result = runner.invoke(customer, ["list"])
    assert result.exit_code == 0
    assert "Aucun token trouvé." in result.output

def test_command_customer_list_filters_and_sorts(runner):
    """Test de la commande customer list avec filtres et tris."""
    runner.invoke(cli, ["login"], input="EMP0001\n")  # Employé commercial
    result = runner.invoke(customer, ["list", "--filter", "sale_contact_id=1", "--sort", "company=asc"])
    assert result.exit_code == 0
    assert "2 résultat(s)" in result.output
    david_index = result.output.index("David")
    eva_index = result.output.index("Eva")
    assert david_index < eva_index, "L'ordre attendu est David avant Eva"

def test_command_customer_update(runner):
    """Test de la commande customer update"""
    runner.invoke(cli, ["login"], input="EMP0001\n")  # Employé commercial
    result = runner.invoke(customer, ["update", "1", "last_name=Gaston", "email=david.gaston@gmail.com"])
    assert result.exit_code == 0
    assert "Client mis à jour" in result.output

def test_command_customer_update_unauthenticated(runner):
    """Test de la commande customer update sans authentification."""
    result = runner.invoke(customer, ["update", "1", "last_name=Gaston", "email=david.gaston@gmail.com"])
    assert result.exit_code == 0
    assert "Aucun token trouvé." in result.output

def test_command_customer_update_unauthorized(runner):
    """Test de la commande customer update sans autorisation."""
    runner.invoke(cli, ["login"], input="EMP0002\n")  # Employé commercial (n'étant pas en charge du client)
    result = runner.invoke(customer, ["update", "1", "last_name=Gaston", "email=david.gaston@gmail.com"])
    assert result.exit_code == 0
    assert "Vous n'êtes pas autorisé à modifier ce client" in result.output
    
def test_command_customer_update_contact(runner):
    """Test de la commande customer update-contact"""
    runner.invoke(cli, ["login"], input="EMP0005\n")  # Employé manager
    result = runner.invoke(customer, ["update-contact", "3", "EMP0001"])
    assert result.exit_code == 0
    assert "Client mis à jour" in result.output
    assert "Alice" in result.output
    assert "Dupont" in result.output

def test_command_customer_update_contact_unauthenticated(runner):
    """Test de la commande customer update-contact sans authentification."""
    result = runner.invoke(customer, ["update-contact", "3", "EMP0001"])
    assert result.exit_code == 0
    assert "Aucun token trouvé." in result.output

def test_command_customer_update_contact_unauthorized(runner):
    """Test de la commande customer update-contact sans autorisation."""
    runner.invoke(cli, ["login"], input="EMP0003\n")  # Employé support (non autorisé)
    result = runner.invoke(customer, ["update-contact", "3", "EMP0001"])
    assert result.exit_code == 0
    assert "Accès refusé" in result.output

def test_command_customer_delete(runner):
    """Test de la commande customer delete"""
    runner.invoke(cli, ["login"], input="EMP0005\n")  # Employé manager
    result = runner.invoke(customer, ["delete", "3"], input="oui\n")
    assert result.exit_code == 0
    assert "Client supprimé" in result.output

def test_command_customer_delete_unauthenticated(runner):
    """Test de la commande customer delete sans authentification."""
    result = runner.invoke(customer, ["delete", "3"])
    assert result.exit_code == 0
    assert "Aucun token trouvé." in result.output

def test_command_customer_delete_unauthorized(runner):
    """Test de la commande customer delete sans autorisation."""
    runner.invoke(cli, ["login"], input="EMP0003\n")  # Employé support (non autorisé)
    result = runner.invoke(customer, ["delete", "3"])
    assert result.exit_code == 0
    assert "Accès refusé" in result.output