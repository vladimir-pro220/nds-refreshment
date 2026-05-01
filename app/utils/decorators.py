from functools import wraps
from flask import redirect, url_for, flash, abort, session
from flask_login import current_user


def admin_required(f):
    """
    Décorateur qui vérifie que l'admin est connecté via session["admin_connecte"].
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_connecte"):
            flash("Veuillez vous connecter pour accéder à cette page.", "warning")
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return decorated_function


def login_required_custom(f):
    """
    Décorateur qui vérifie que le client est connecté via Flask-Login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Veuillez vous connecter pour accéder à cette page.", "warning")
            return redirect(url_for("auth.login"))
        if not current_user.actif:
            flash("Votre compte a été désactivé. Contactez l'administrateur.", "danger")
            return redirect(url_for("client.index"))
        return f(*args, **kwargs)
    return decorated_function


def anonymous_required(f):
    """
    Décorateur qui vérifie que l'utilisateur N'est PAS connecté.
    Utile pour les pages login/register.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("client.index"))
        return f(*args, **kwargs)
    return decorated_function