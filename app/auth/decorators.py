from app.auth.session import load_token
from app.auth.token import decode_access_token

from rich.console import Console
from rich.text import Text

def require_token(func):
    def wrapper(*args, **kwargs):
        token = load_token()
        console = Console()
        if not token:
            console.print(Text("Aucun token trouvé. Veuillez vous connecter.", style="red"))
            return
        try:
            payload = decode_access_token(token)
            console.print(Text(f"Token valide pour l'utilisateur : {payload['emp_number']}", style="green"))
        except Exception as e:
            console.print(Text(f"Token invalide ou expiré : {str(e)}", style="red"))
            return
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            console.print(Text(f"Erreur lors de l'exécution de la fonction : {str(e)}", style="red"))
            return
    return wrapper

def is_salesperson_or_manager(func):
    def wrapper(*args, **kwargs):
        token = load_token()
        payload = decode_access_token(token)
        console = Console()
        if payload['role_id'] == 1:
            console.print(Text("Accès autorisé (Commercial)", style="green"))
            return func(*args, **kwargs)
        elif payload['role_id'] == 3:
            console.print(Text("Accès autorisé (Gestion)", style="green"))
            return func(*args, **kwargs)
        else:
            console.print(Text("Accès refusé : cette action est réservée au département commercial.", style="red"))
            return
    return wrapper

def is_support_or_manager(func):
    def wrapper(*args, **kwargs):
        token = load_token()
        payload = decode_access_token(token)
        console = Console()
        if payload['role_id'] == 2:
            console.print(Text("Accès autorisé (Support)", style="green"))
            return func(*args, **kwargs)
        elif payload['role_id'] == 3:
            console.print(Text("Accès autorisé (Gestion)", style="green"))
            return func(*args, **kwargs)
        else:
            console.print(Text("Accès refusé : cette action est réservée au département support.", style="red"))
            return
    return wrapper

def is_manager(func):
    def wrapper(*args, **kwargs):
        token = load_token()
        payload = decode_access_token(token)
        console = Console()
        if payload['role_id'] == 3:
            console.print(Text("Accès autorisé (Gestion)", style="green"))
            return func(*args, **kwargs)
        else:
            console.print(Text("Accès refusé : cette action est réservée au département gestion.", style="red"))
            return
    return wrapper
