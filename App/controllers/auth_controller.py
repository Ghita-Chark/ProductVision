from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps


auth = Blueprint('auth', __name__)

def login_required(f):
    """Décorateur pour restreindre l'accès aux utilisateurs connectés."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Veuillez vous connecter pour accéder à cette page !!")
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


