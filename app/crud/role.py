from app.models.models import Role

def create_role(session, name, description):
    new_role = Role(name=name, description=description)
    session.add(new_role)
    session.commit()
    session.refresh(new_role)
    return new_role

def get_all_roles(session):
    return session.query(Role).all()

def get_role_by_id(session, role_id):
    role = session.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise ValueError(f"Aucun rôle trouvé avec l'ID {role_id}.")
    return role

def get_role_by_name(session, name):
    role = session.query(Role).filter(Role.name == name).first()
    if not role:
        raise ValueError(f"Aucun rôle trouvé avec le nom {name}.")
    return role

def update_role_by_id(session, id, attribute, value):
    if not hasattr(Role, attribute):
        raise ValueError(f"L'attribut '{attribute}' n'existe pas dans le modèle Role.")
    
    if attribute not in ['name', 'description']:
        raise ValueError(f"L'attribut '{attribute}' ne peut pas être mis à jour directement.")
    
    role = session.query(Role).filter(Role.id == id).first()
    
    if not role:
        raise ValueError(f"Aucun rôle trouvé avec l'ID {id}.")
    
    setattr(role, attribute, value)
    session.commit()
    return role

def update_role_by_name(session, name, attribute, value):
    if not hasattr(Role, attribute):
        raise ValueError(f"L'attribut '{attribute}' n'existe pas dans le modèle Role.")
    
    if attribute not in ['name', 'description']:
        raise ValueError(f"L'attribut '{attribute}' ne peut pas être mis à jour directement.")
    
    role = session.query(Role).filter(Role.name == name).first()
    
    if not role:
        raise ValueError(f"Aucun rôle trouvé avec le nom {name}.")

    setattr(role, attribute, value)
    session.commit()
    session.refresh(role)
    return role

def delete_role_by_id(session, id):
    role = session.query(Role).filter(Role.id == id).first()
    
    if not role:
        raise ValueError(f"Aucun rôle trouvé avec l'ID {id}.")

    session.delete(role)
    session.commit()
    session.refresh(role)
    return role

def delete_role_by_name(session, name):
    role = session.query(Role).filter(Role.name == name).first()
    
    if not role:
        raise ValueError(f"Aucun rôle trouvé avec le nom {name}.")
    
    session.delete(role)
    session.commit()
    return role