from app.models.models import Role

def get_roles(session):
    """Récupère tous les rôles."""
    return session.query(Role).all()
