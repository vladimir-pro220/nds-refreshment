from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user


def admin_required(f):
    """
    Décorateur qui vérifie que l'utilisateur connecté est un administrateur.
    Redirige vers l'accueil avec un message d'erreur si ce n'est pas le cas.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Veuillez vous connecter pour accéder à cette page.", "warning")
            return redirect(url_for("auth.login"))
        if not current_user.is_admin():
            flash("Accès refusé. Vous n'avez pas les droits administrateur.", "danger")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def login_required_custom(f):
    """
    Décorateur qui vérifie que l'utilisateur est connecté.
    Redirige vers la page de connexion avec un message si ce n'est pas le cas.
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
    Utile pour les pages login/register — redirige si déjà connecté.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.is_admin():
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("client.index"))
        return f(*args, **kwargs)
    return decorated_function