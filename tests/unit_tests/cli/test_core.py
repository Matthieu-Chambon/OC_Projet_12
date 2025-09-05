import pytest
from unittest.mock import MagicMock
from app.cli import core
import click

def test_prepare_sentry_scope_without_user_without_extra_context(mocker):
    """Test sans utilisateur et sans contexte supplémentaire."""
    # Mock de la fonction get_employees pour ne pas renvoyer d'utilisateur
    mocker.patch.object(core.crud_employee, "get_employees", return_value=[])

    # mocker "with sentry_sdk.configure_scope() as scope" (contexte manager)
    mock_scope_ctx = mocker.patch("app.cli.core.sentry_sdk.configure_scope")
    # création faux objet scope (qui est censé avoir .set_user et .set_extra)
    mock_scope = mocker.MagicMock()
    # définir ce que renvoie mock_scope_ctx
    mock_scope_ctx.return_value.__enter__.return_value = mock_scope

    # Appel de la fonction à tester
    core.prepare_sentry_scope()

    # Vérification que .set_user n'a pas été appelé
    mock_scope.set_user.assert_not_called()

    # Vérification que .set_extra n'a pas été appelé
    mock_scope.set_extra.assert_not_called()

def test_prepare_sentry_scope_with_user_and_extra_context(mocker):
    """Test avec utilisateur et contexte supplémentaire."""
    # Création d'un faux utilisateur
    fake_user = MagicMock()
    fake_user.id = 1
    fake_user.employee_number = "EMP0001"
    fake_user.first_name = "Alice"
    fake_user.last_name = "Dupont"
    fake_user.email = "alice@example.com"
    fake_user.role_id = 1

    # Mock des fonctions utilisées dans prepare_sentry_scope
    mocker.patch.object(core, "load_token", return_value="fake_token")
    mocker.patch.object(core, "decode_access_token", return_value={"emp_number": "EMP0001"})
    mocker.patch.object(core.crud_employee, "get_employees", return_value=[fake_user])
    
    # mocker "with sentry_sdk.configure_scope() as scope" (contexte manager)
    mock_scope_ctx = mocker.patch("app.cli.core.sentry_sdk.configure_scope")
    # création faux objet scope (qui est censé avoir .set_user et .set_extra)
    mock_scope = mocker.MagicMock()
    # définir ce que renvoie mock_scope_ctx
    mock_scope_ctx.return_value.__enter__.return_value = mock_scope

    # Appel de la fonction à tester
    core.prepare_sentry_scope(extra_context={"function": "my_function"})

    # Vérification de l'appel à la méthode .set_user
    mock_scope.set_user.assert_called_once_with({
        "id": 1,
        "employee_number": "EMP0001",
        "first_name": "Alice",
        "last_name": "Dupont",
        "email": "alice@example.com"
    })

    # Vérification de l'appel à la méthode .set_extra
    mock_scope.set_extra.assert_called_once_with("function", "my_function")

def test_safe_execute_success():
    """Fonction qui se déroule normalement."""
    def my_func(a, b):
        return a + b

    result = core.safe_execute(my_func, 2, 3)
    assert result == 5

def test_safe_execute_value_error(mocker):
    """Fonction qui lève ValueError."""
    def my_func():
        raise ValueError("Cette fonction échoue")

    mock_print = mocker.patch("builtins.print")
    result = core.safe_execute(my_func)

    mock_print.assert_called_once_with("Cette fonction échoue")
    assert result is None

def test_safe_execute_generic_exception(mocker):
    """Fonction qui lève une exception générique."""
    def my_func(*args, **kwargs):
        raise RuntimeError("Something went wrong")

    # Mock des fonctions utilisées dans safe_execute
    mock_prepare_scope = mocker.patch("app.cli.core.prepare_sentry_scope")
    mock_capture = mocker.patch("app.cli.core.sentry_sdk.capture_exception")
    mock_print = mocker.patch("builtins.print")

    # Appel de la fonction à tester
    result = core.safe_execute(my_func, 1, key="value")

    # Vérifie le retour None
    assert result is None

    # Vérifie print
    mock_print.assert_called_once_with("[ERREUR] : Something went wrong")

    # Vérifie que prepare_sentry_scope est appelé avec le bon contexte
    mock_prepare_scope.assert_called_once_with({
        "function": "my_func",
        "module": my_func.__module__,
        "args": ["1"],
        "kwargs": {"key": "value"}
    })

    # Vérifie que sentry_sdk.capture_exception a été appelé
    mock_capture.assert_called_once()
    
def test_input_with_limit_ok(mocker):
    """Test de la fonction input_with_limit avec une entrée valide."""
    mocker.patch("builtins.input", return_value="Hello")
    
    result = core.input_with_limit("Entrez un texte:", 10)
    
    assert result == "Hello"

def test_input_with_limit_too_long(mocker):
    """Test de la fonction input_with_limit avec une entrée trop longue."""
    # On simule plusieurs entrées de l'utilisateur : d'abord trop longue, puis correcte
    inputs = ["Ceci est trop long", "Ok"]
    mock_input = mocker.patch("builtins.input", side_effect=inputs)
    mock_print = mocker.patch("builtins.print")

    # Appel de la fonction à tester
    result = core.input_with_limit("Entrez un texte:", 5)
    
    # Vérifie que la fonction retourne la valeur correcte
    assert result == "Ok"
    
    # Vérifie que le message d'erreur a été affiché
    mock_print.assert_called_with("Veuillez entrer un texte de moins de 5 caractères.")
    
    # Vérifie que input a été appelé deux fois
    assert mock_input.call_count == 2

def test_attr_val_to_dict_success(mocker):
    """Test de la fonction attr_val_to_dict avec des données valides."""
    attr_val_pairs = [
        "attr1=value1",
        "attr2=value2",
        "attr3=value3"
    ]

    result = core.attr_val_to_dict(attr_val_pairs)

    assert result == {
        "attr1": "value1",
        "attr2": "value2",
        "attr3": "value3"
    }

def test_attr_val_to_dict_fail(mocker):
    """Test de la fonction attr_val_to_dict avec une entrée invalide."""
    attr_val_pairs = [
        "attr1:value1",
        "attr2 value2",
        "attr3"
    ]

    with pytest.raises(click.BadParameter):
        core.attr_val_to_dict(attr_val_pairs)

def test_sort_to_dict_success(mocker):
    """Test de la fonction sort_to_dict avec des données valides."""
    sort = [
        "attr1=asc",
        "attr2=desc",
        "attr3=asc"
    ]

    result = core.sort_to_dict(sort)

    assert result == {
        "attr1": "asc",
        "attr2": "desc",
        "attr3": "asc"
    }

def test_sort_to_dict_without_equals(mocker):
    """Test de la fonction sort_to_dict sans '=' dans ses critères."""
    sort = [
        "attr1:asc",
        "attr2 desc",
        "attr3"
    ]

    with pytest.raises(click.BadParameter):
        core.sort_to_dict(sort)

def test_sort_to_dict_wrong_sort_keyword(mocker):
    """Test de la fonction sort_to_dict avec un mot-clé de tri invalide."""
    sort = [
        "attr1:asc",
        "attr2:desc",
        "attr3:invalid"
    ]

    with pytest.raises(click.BadParameter):
        core.sort_to_dict(sort)