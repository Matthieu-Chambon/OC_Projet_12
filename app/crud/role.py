from app.models.models import Role

def get_roles(session):
    return session.query(Role).all()
