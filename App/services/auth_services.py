from App.dal.auth_dal import get_user_by_username, create_user
import hashlib

def hash_password(password):
    """Hache le mot de passe avec SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    """Vérifie les informations d'identification de l'utilisateur."""
    user = get_user_by_username(username)
    
    if user and user[2] == password:  
        return user
        
    return None


def register_user(username, password, role='user'):

    create_user(username, password, role)