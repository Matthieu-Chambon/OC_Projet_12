from app.auth.session import load_token
from app.auth.token import decode_access_token

def require_token(func):
    def wrapper(*args, **kwargs):
        token = load_token()
        if not token:
            print("Aucun token trouvé. Veuillez vous connecter.")
            return
        try:
            payload = decode_access_token(token)
            print(f"Token valide pour l'utilisateur : {payload['emp_number']}")
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Token invalide ou expiré : {str(e)}")
            return
    return wrapper

def require_sale_role(func):
    def wrapper(*args, **kwargs):
        token = load_token()
        payload = decode_access_token(token)
        if payload['role_id'] == 1:
            print("Accès autorisé (Commercial)")
            return func(*args, **kwargs)
        else:
            print("Accès refusé : cette action est réservée au département commercial.")
            return
    return wrapper

def require_support_role(func):
    def wrapper(*args, **kwargs):
        token = load_token()
        payload = decode_access_token(token)
        if payload['role_id'] == 2:
            print("Accès autorisé (Support)")
            return func(*args, **kwargs)
        else:
            print("Accès refusé : cette action est réservée au département support.")
            return
    return wrapper

def require_management_role(func):
    def wrapper(*args, **kwargs):
        token = load_token()
        payload = decode_access_token(token)
        if payload['role_id'] == 3:
            print("Accès autorisé (Gestion)")
            return func(*args, **kwargs)
        else:
            print("Accès refusé : cette action est réservée au département gestion.")
            return
    return wrapper
