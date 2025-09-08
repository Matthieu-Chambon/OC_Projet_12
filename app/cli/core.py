from app.db.database import Session
from app.crud import employee as crud_employee

from app.auth.token import decode_access_token
from app.auth.session import load_token

import click
import sentry_sdk


db = Session()


@click.group()
def cli():
    """Epic Events CLI - Gestion complète des rôles, employés, clients, contrats et événements"""
    pass


def prepare_sentry_scope(extra_context=None):
    """Prépare le contexte Sentry pour la capture des erreurs."""
    user = None
    try:
        emp_number = decode_access_token(load_token())["emp_number"]
        employees = crud_employee.get_employees(db, {"employee_number": emp_number}, None)
        if employees:
            user = employees[0]
    except Exception:
        pass

    with sentry_sdk.configure_scope() as scope:
        if user:
            scope.set_user({
                "id": user.id,
                "employee_number": user.employee_number,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            })

        if extra_context:
            for key, value in extra_context.items():
                scope.set_extra(key, str(value))


def safe_execute(func, *args, **kwargs):
    """Exécute une fonction en toute sécurité et capture les exceptions."""
    try:
        return func(*args, **kwargs)
    except ValueError as e:
        print(str(e))
    except Exception as e:
        print(f"[ERREUR] : {e}")
        prepare_sentry_scope({
            "function": func.__name__,
            "module": func.__module__,
            "args": [str(a) for a in args],
            "kwargs": {k: str(v) for k, v in kwargs.items()},
        })

        sentry_sdk.capture_exception(e)
        return None


def input_with_limit(prompt, limit):
    """Demande une entrée utilisateur avec une limite de caractères."""
    while True:
        value = input(">>> " + prompt)
        if len(value) > limit:
            print(f"Veuillez entrer un texte de moins de {limit} caractères.")
        else:
            return value


def attr_val_to_dict(attr_val_pairs):
    """Convertit une liste de paires attribut=valeur en dictionnaire."""
    attrs = {}

    for pair in attr_val_pairs:
        if "=" not in pair:
            raise click.BadParameter("Chaque option doit être au format attribut=valeur.")
        attribute, value = pair.split("=", 1)
        attrs[attribute] = value

    return attrs


def sort_to_dict(sort):
    """Convertit une liste de critères de tri en dictionnaire."""
    sorts = {}

    for s in sort:
        if "=" not in s:
            raise click.BadParameter("Le critère de tri doit être au format attribut=asc|desc.")
        attribute, order = s.split("=", 1)
        if order not in ["asc", "desc"]:
            raise click.BadParameter("L'ordre de tri doit être 'asc' ou 'desc'.")

        sorts[attribute] = order

    return sorts
