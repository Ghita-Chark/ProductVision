from App.dal.db import get_connection

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

def create_user(username, password, role='user'):
    """Crée un nouvel utilisateur avec un mot de passe en texte brut (non haché)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    print(f"Création d'un utilisateur: {username}, Rôle: {role}, Mot de passe: {password}")
    
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                      (username, password, role))
        conn.commit()
        print(f"Utilisateur créé avec succès: {username}")
    except Exception as e:
        print(f"Erreur lors de la création de l'utilisateur: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()
