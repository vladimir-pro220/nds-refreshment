"""
FICHIER : app/routes/auth.py
RÔLE    : Authentification des clients (inscription, connexion, déconnexion)
APPORT  : Gère la création de comptes clients, la vérification des identifiants
          et les sessions utilisateurs via Flask-Login.
DÉPENDANCES : User, db, login_user, logout_user, anonymous_required, is_strong_password
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user
from app.extensions import db
from app.models import User
from app.utils import login_required_custom, anonymous_required, is_strong_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
@anonymous_required
def register():
    """Inscription d'un nouveau client."""
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        prenom = request.form.get("prenom", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not all([nom, prenom, email, password, confirm_password]):
            flash("Tous les champs sont obligatoires.", "danger")
            return render_template("client/register.html")

        if password != confirm_password:
            flash("Les deux mots de passe ne correspondent pas.", "danger")
            return render_template("client/register.html")

        valid, message = is_strong_password(password)
        if not valid:
            flash(message, "danger")
            return render_template("client/register.html")

        if User.query.filter_by(email=email).first():
            flash("Cet email est déjà utilisé.", "danger")
            return render_template("client/register.html")

        # Création du compte
        user = User(nom=nom, prenom=prenom, email=email, role="client")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Connexion automatique après inscription
        login_user(user, remember=False)

        flash(f"Bienvenue {user.prenom} ! Votre compte a été créé avec succès.", "success")
        return redirect(url_for("client.index"))

    return render_template("client/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
@anonymous_required
def login():
    """Connexion d'un client."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember", False)

        if not all([email, password]):
            flash("Tous les champs sont obligatoires.", "danger")
            return render_template("client/login.html")

        user = User.query.filter_by(email=email, role="client").first()

        if not user or not user.check_password(password):
            flash("Email ou mot de passe incorrect.", "danger")
            return render_template("client/login.html")

        if not user.actif:
            flash("Votre compte a été désactivé. Contactez l'administrateur.", "danger")
            return render_template("client/login.html")

        login_user(user, remember=remember)
        flash("Connexion réussie !", "success")

        next_page = request.args.get("next")
        return redirect(next_page or url_for("client.index"))

    return render_template("client/login.html")


@auth_bp.route("/logout")
@login_required_custom
def logout():
    """Déconnexion du client."""
    logout_user()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("client.index"))