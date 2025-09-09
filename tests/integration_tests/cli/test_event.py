from app.cli.core import cli
from app.cli.event import event


def test_command_event_create(runner):
    """Test de la commande event create"""
    runner.invoke(cli, ["login"], input="EMP0002\n")  # Employé commercial
    result = runner.invoke(event, ["create"], input="Réunion de suivi\n5\n2023-09-15 10:00\n2023-09-15 12:00\n"
                                                    "Salle A\n5\nVenir avec le rapport de vente\n")
    assert result.exit_code == 0
    assert "Nouvel événement créé" in result.output


def test_command_event_create_unauthenticated(runner):
    """Test de la commande event create sans authentification."""
    result = runner.invoke(event, ["create"], input="Réunion de suivi\n5\n2023-09-15 10:00\n2023-09-15 12:00\n"
                                                    "Salle A\n5\nVenir avec le rapport de vente\n")
    assert result.exit_code == 0
    assert "Aucun token trouvé." in result.output


def test_command_event_create_unauthorized(runner):
    """Test de la commande event create sans autorisation."""
    runner.invoke(cli, ["login"], input="EMP0003\n")  # Employé support (non autorisé)
    result = runner.invoke(event, ["create"], input="Réunion de suivi\n5\n2023-09-15 10:00\n2023-09-15 12:00\n"
                                                    "Salle A\n5\nVenir avec le rapport de vente\n")
    assert result.exit_code == 0
    assert "Accès refusé" in result.output


def test_command_event_list(runner):
    """Test de la commande event list"""
    runner.invoke(cli, ["login"], input="EMP0002\n")  # Employé commercial
    result = runner.invoke(event, ["list"])
    assert result.exit_code == 0
    assert "Liste des événements" in result.output
    assert "3 résultat(s)" in result.output


def test_command_event_list_unauthenticated(runner):
    """Test de la commande event list sans authentification."""
    result = runner.invoke(event, ["list"])
    assert result.exit_code == 0
    assert "Aucun token trouvé." in result.output


def test_command_event_list_filters_and_sorts(runner):
    """Test de la commande event list avec des filtres et des tris."""
    runner.invoke(cli, ["login"], input="EMP0002\n")  # Employé commercial
    result = runner.invoke(event, ["list", "--filter", "support_contact_id=None", "--sort", "start_date=asc"])
    assert result.exit_code == 0
    assert "2 résultat(s)" in result.output
    event1_index = result.output.index("Réun")  # Les mots sont tronqués dans l'affichage via les tests
    event2_index = result.output.index("Atel")  # Les mots sont tronqués dans l'affichage via les tests
    assert event1_index < event2_index, "L'ordre attendu est 'Réunion' avant 'Atelier'"


def test_command_event_update(runner):
    """Test de la commande event update"""
    runner.invoke(cli, ["login"], input="EMP0005\n")  # Employé manager
    result = runner.invoke(event, ["update", "1", "name=Festival de la musique", "attendees=250"])
    assert result.exit_code == 0
    assert "Événement mis à jour" in result.output
    assert "Fest" in result.output  # Les mots sont tronqués dans l'affichage via les tests
    assert "250" in result.output


def test_command_event_update_unauthenticated(runner):
    """Test de la commande event update sans authentification."""
    result = runner.invoke(event, ["update", "1", "name=Festival de la musique", "attendees=250"])
    assert result.exit_code == 0
    assert "Aucun token trouvé." in result.output


def test_command_event_update_unauthorized(runner):
    """Test de la commande event update sans autorisation."""
    runner.invoke(cli, ["login"], input="EMP0001\n")  # Employé commercial (non autorisé)
    result = runner.invoke(event, ["update", "1", "name=Festival de la musique", "attendees=250"])
    assert result.exit_code == 0
    assert "Accès refusé" in result.output


def test_command_event_update_contact(runner):
    """Test de la commande event update-contact"""
    runner.invoke(cli, ["login"], input="EMP0005\n")  # Employé manager
    result = runner.invoke(event, ["update-contact", "1", "EMP0004"])
    assert result.exit_code == 0
    assert "Événement mis à jour" in result.output
    assert "Zoe" in result.output
    assert "Guer" in result.output  # Les mots sont tronqués dans l'affichage via les tests


def test_command_event_update_contact_unauthenticated(runner):
    """Test de la commande event update-contact sans authentification."""
    result = runner.invoke(event, ["update-contact", "1", "EMP0004"])
    assert result.exit_code == 0
    assert "Aucun token trouvé." in result.output


def test_command_event_update_contact_unauthorized(runner):
    """Test de la commande event update-contact sans autorisation."""
    runner.invoke(cli, ["login"], input="EMP0003\n")  # Employé support (non autorisé)
    result = runner.invoke(event, ["update-contact", "1", "EMP0004"])
    assert result.exit_code == 0
    assert "Accès refusé" in result.output


def test_command_event_delete(runner):
    """Test de la commande event delete"""
    runner.invoke(cli, ["login"], input="EMP0005\n")  # Employé manager
    result = runner.invoke(event, ["delete", "1"], input="oui\n")
    assert result.exit_code == 0
    assert "Événement supprimé" in result.output


def test_command_event_delete_unauthenticated(runner):
    """Test de la commande event delete sans authentification."""
    result = runner.invoke(event, ["delete", "1"])
    assert result.exit_code == 0
    assert "Aucun token trouvé." in result.output


def test_command_event_delete_unauthorized(runner):
    """Test de la commande event delete sans autorisation."""
    runner.invoke(cli, ["login"], input="EMP0001\n")  # Employé commercial (non autorisé)
    result = runner.invoke(event, ["delete", "1"], input="oui\n")
    assert result.exit_code == 0
    assert "Accès refusé" in result.output
