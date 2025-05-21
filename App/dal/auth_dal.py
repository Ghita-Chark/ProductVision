from app.dal.db import get_connection

def get_user_by_username(username):
    """Récupère un utilisateur par son nom d'utilisateur."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Affichage de débogage
    print(f"Recherche de l'utilisateur: {username}")
    
    cursor.execute("SELECT id, username, password, role FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    
    # Affichage du résultat pour débogage
    if user:
        print(f"Utilisateur trouvé: {user[1]}, Mot de passe stocké: {user[2]}, Rôle: {user[3]}")
    else:
        print("Aucun utilisateur trouvé")
    
    cursor.close()
    conn.close()
    return user
