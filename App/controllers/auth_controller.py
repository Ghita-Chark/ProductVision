from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from app.services.auth_services import authenticate_user, register_user

auth = Blueprint('auth', __name__)

def login_required(f):
    """Décorateur pour restreindre l'accès aux utilisateurs connectés."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Veuillez vous connecter pour accéder à cette page ❌")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Décorateur pour restreindre l'accès aux administrateurs."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash("Accès refusé : Vous devez être administrateur pour accéder à cette page ❌")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Débogage: Afficher les valeurs pour vérification
        print(f"Tentative de connexion - Nom d'utilisateur: {username}, Mot de passe: {password}")
        
        user = authenticate_user(username, password)
        if user:
            print(f"Authentification réussie pour: {username}, ID: {user[0]}, Rôle: {user[3]}")
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]  # Ajout du rôle dans la session
            flash("Connexion réussie ✅")
            return redirect(url_for('main.import_csv'))  # Redirige vers la page d'importation
        else:
            print(f"Échec d'authentification pour: {username}")
            flash("Nom d'utilisateur ou mot de passe incorrect ❌")

    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f"Tentative d'inscription - Nom d'utilisateur: {username}, Mot de passe: {password}")
        
        try:
            # Création d'un utilisateur avec mot de passe en texte brut
            register_user(username, password, role='user')
            print(f"Inscription réussie pour: {username}")
            flash("Inscription réussie ✅")
            return redirect(url_for('auth.login'))
        except Exception as e:
            print(f"Erreur lors de l'inscription: {e}")
            flash("Erreur : Nom d'utilisateur déjà pris ❌")

    return render_template('auth.html')

@auth.route('/logout')
def logout():
    if 'username' in session:
        print(f"Déconnexion de l'utilisateur: {session['username']}")
    session.clear()
    flash("Déconnexion réussie ✅")
    return redirect(url_for('auth.login'))