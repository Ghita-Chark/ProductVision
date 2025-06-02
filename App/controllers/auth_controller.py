from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps

auth = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Veuillez vous connecter pour accéder à cette page !!")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash("Accès refusé : Vous devez être administrateur pour accéder à cette page!!")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']


        print(f"Tentative de connexion - Nom d'utilisateur: {username}, Mot de passe: {password}")
        
        user = authenticate_user(username, password)
        if user:
            print(f"Authentification réussie pour: {username}, ID: {user[0]}, Rôle: {user[3]}")
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]  
            flash("Connexion réussie ✅")
            return redirect(url_for('main.import_csv'))  
        else:
            print(f"Échec d'authentification pour: {username}")
            flash("Nom d'utilisateur ou mot de passe incorrect ❌")

    return render_template('login.html')




