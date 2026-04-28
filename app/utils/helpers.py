import os
from datetime import datetime
from flask import current_app


# ── Gestion des fichiers images ────────────────────────
def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def save_image(file, folder="uploads"):
    """
    Sauvegarde une image uploadée et retourne son nom de fichier.
    Génère un nom unique basé sur le timestamp pour éviter les doublons.
    """
    if not file or not allowed_file(file.filename):
        return None

    # Génération d'un nom unique
    extension = file.filename.rsplit(".", 1)[1].lower()
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}.{extension}"

    # Sauvegarde du fichier
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(upload_path)

    return filename


def delete_image(filename):
    """Supprime une image du dossier uploads si elle existe."""
    if not filename or filename == "default.jpg":
        return False

    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


# ── Formatage des données ──────────────────────────────
def format_price(price):
    """Formate un prix en FCFA avec séparateur de milliers."""
    return f"{price:,.0f} FCFA"


def format_date(date):
    """Formate une date en français."""
    if not date:
        return ""
    mois = [
        "janvier", "février", "mars", "avril", "mai", "juin",
        "juillet", "août", "septembre", "octobre", "novembre", "décembre"
    ]
    return f"{date.day} {mois[date.month - 1]} {date.year}"


def format_datetime(date):
    """Formate une date et heure en français."""
    if not date:
        return ""
    return f"{format_date(date)} à {date.strftime('%H:%M')}"


# ── Pagination ─────────────────────────────────────────
def paginate_query(query, page, per_page=12):
    """
    Pagine une requête SQLAlchemy.
    Retourne un objet pagination Flask-SQLAlchemy.
    """
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )


# ── Panier (session) ───────────────────────────────────
def get_cart_count(cart):
    """Retourne le nombre total d'articles dans le panier."""
    if not cart:
        return 0
    return sum(item["quantite"] for item in cart.values())


def get_cart_total(cart, products):
    """Calcule le total du panier en tenant compte des promotions actives."""
    if not cart:
        return 0

    total = 0
    for product_id, item in cart.items():
        product = products.get(int(product_id))
        if product:
            # Vérification promotion active
            promo_active = next(
                (p for p in product.promotions if p.is_active()), None
            )
            if promo_active:
                prix = promo_active.prix_promo()
            else:
                prix = product.prix
            total += prix * item["quantite"]
    return total


# ── Statistiques admin ─────────────────────────────────
def get_stats():
    """Retourne les statistiques globales pour le dashboard admin."""
    from app.models import User, Product, Order, Review

    return {
        "total_clients": User.query.filter_by(role="client").count(),
        "total_produits": Product.query.count(),
        "total_commandes": Order.query.count(),
        "total_avis": Review.query.filter_by(approuve=True).count(),
        "commandes_en_attente": Order.query.filter_by(
            statut="en_attente"
        ).count(),
        "commandes_livrees": Order.query.filter_by(
            statut="livree"
        ).count(),
    }