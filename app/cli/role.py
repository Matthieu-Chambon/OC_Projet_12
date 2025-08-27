from app.cli.core import cli, safe_execute
from app.crud import role as crud_role
from app.auth.decorators import require_token
from app.db.database import Session
from app.ui import views


db = Session()

@cli.group()
def role():
    """Gestion des rôles"""
    pass

@role.command("list")
@require_token
def get_roles():
    """Récupère tous les rôles."""
    roles = safe_execute(crud_role.get_roles, db)
    if roles:
        views.display_roles(roles)