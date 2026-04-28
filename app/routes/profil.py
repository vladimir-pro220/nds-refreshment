"""
FICHIER : app/routes/profil.py
RÔLE    : Gestion du profil et de l'historique des commandes client
APPORT  : Permet au client de consulter et modifier ses informations
          personnelles et de suivre l'historique de ses commandes.
DÉPENDANCES : User, Order, login_required_custom, is_strong_password, db
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from app.extensions import db
from app.models import User, Order
from app.utils import login_required_custom, is_strong_password

profil_bp = Blueprint("profil", __name__)


@profil_bp.route("/profil")
@login_required_custom
def profil():
    """Affiche le profil du client et son historique de commandes."""
    orders = Order.query.filter_by(
        user_id=current_user.id
    ).order_by(Order.created_at.desc()).all()

    return render_template(
        "client/profil.html",
        user=current_user,
        orders=orders
    )


@profil_bp.route("/profil/modifier", methods=["GET", "POST"])
@login_required_custom
def modifier_profil():
    """Permet au client de modifier ses informations personnelles."""
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        prenom = request.form.get("prenom", "").strip()
        email = request.form.get("email", "").strip().lower()

        # Vérifications
        if not all([nom, prenom, email]):
            flash("Tous les champs sont obligatoires.", "danger")
            return render_template("client/modifier_profil.html", user=current_user)

        # Vérification email unique
        existant = User.query.filter_by(email=email).first()
        if existant and existant.id != current_user.id:
            flash("Cet email est déjà utilisé par un autre compte.", "danger")
            return render_template("client/modifier_profil.html", user=current_user)

        # Mise à jour
        current_user.nom = nom
        current_user.prenom = prenom
        current_user.email = email
        db.session.commit()

        flash("Profil mis à jour avec succès.", "success")
        return redirect(url_for("profil.profil"))

    return render_template("client/modifier_profil.html", user=current_user)


@profil_bp.route("/profil/mot-de-passe", methods=["GET", "POST"])
@login_required_custom
def changer_password():
    """Permet au client de changer son mot de passe."""
    if request.method == "POST":
        old_password = request.form.get("old_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Vérification ancien mot de passe
        if not current_user.check_password(old_password):
            flash("Ancien mot de passe incorrect.", "danger")
            return render_template("client/changer_password.html")

        # Vérification confirmation
        if new_password != confirm_password:
            flash("Les deux nouveaux mots de passe ne correspondent pas.", "danger")
            return render_template("client/changer_password.html")

        # Vérification force du mot de passe
        valid, message = is_strong_password(new_password)
        if not valid:
            flash(message, "danger")
            return render_template("client/changer_password.html")

        # Mise à jour
        current_user.set_password(new_password)
        db.session.commit()

        flash("Mot de passe modifié avec succès.", "success")
        return redirect(url_for("profil.profil"))

    return render_template("client/changer_password.html")


@profil_bp.route("/profil/commande/<int:order_id>")
@login_required_custom
def detail_commande(order_id):
    """Affiche le détail d'une commande spécifique du client."""
    order = Order.query.get_or_404(order_id)

    # Sécurité : un client ne peut voir que ses propres commandes
    if order.user_id != current_user.id:
        flash("Accès refusé.", "danger")
        return redirect(url_for("profil.profil"))

    return render_template("client/detail_commande.html", order=order)