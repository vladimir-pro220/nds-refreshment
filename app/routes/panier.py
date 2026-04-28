"""
FICHIER : app/routes/panier.py
RÔLE    : Gestion du panier d'achat côté serveur
APPORT  : Gère l'ajout, la suppression et la mise à jour des articles
          dans le panier stocké en session Flask.
DÉPENDANCES : Product, Promotion, login_required_custom, get_cart_count, get_cart_total
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import current_user
from app.models import Product, Promotion
from app.utils import login_required_custom, get_cart_count, get_cart_total

panier_bp = Blueprint("panier", __name__)


def get_cart():
    """Récupère le panier depuis la session ou crée un panier vide."""
    return session.get("panier", {})


def save_cart(cart):
    """Sauvegarde le panier dans la session."""
    session["panier"] = cart
    session.modified = True


@panier_bp.route("/panier")
def panier():
    """Affiche le contenu du panier."""
    cart = get_cart()

    # Récupération des produits du panier
    product_ids = [int(pid) for pid in cart.keys()]
    products = {p.id: p for p in Product.query.filter(
        Product.id.in_(product_ids)
    ).all()}

    # Construction des lignes du panier
    lignes = []
    for product_id, item in cart.items():
        product = products.get(int(product_id))
        if product:
            # Vérification promotion active
            promo_active = next(
                (p for p in product.promotions if p.is_active()), None
            )
            prix = promo_active.prix_promo() if promo_active else product.prix
            lignes.append({
                "product": product,
                "quantite": item["quantite"],
                "prix": prix,
                "promo": promo_active,
                "sous_total": prix * item["quantite"]
            })

    total = sum(ligne["sous_total"] for ligne in lignes)

    return render_template(
        "client/panier.html",
        lignes=lignes,
        total=total,
        count=get_cart_count(cart)
    )


@panier_bp.route("/panier/ajouter/<int:product_id>", methods=["POST"])
def ajouter(product_id):
    """Ajoute un produit au panier ou augmente sa quantité."""
    product = Product.query.get_or_404(product_id)

    if not product.is_available():
        flash("Ce produit n'est plus disponible.", "warning")
        return redirect(url_for("client.produit_detail", product_id=product_id))

    quantite = request.form.get("quantite", 1, type=int)
    if quantite < 1:
        quantite = 1

    cart = get_cart()
    pid = str(product_id)

    if pid in cart:
        # Vérification stock avant augmentation
        nouvelle_quantite = cart[pid]["quantite"] + quantite
        if nouvelle_quantite > product.stock:
            flash(f"Stock insuffisant. Maximum disponible : {product.stock}.", "warning")
            return redirect(url_for("client.produit_detail", product_id=product_id))
        cart[pid]["quantite"] = nouvelle_quantite
    else:
        cart[pid] = {"quantite": quantite}

    save_cart(cart)
    flash(f"{product.nom} ajouté au panier.", "success")
    return redirect(url_for("client.produit_detail", product_id=product_id))


@panier_bp.route("/panier/modifier/<int:product_id>", methods=["POST"])
def modifier(product_id):
    """Modifie la quantité d'un produit dans le panier."""
    product = Product.query.get_or_404(product_id)
    quantite = request.form.get("quantite", 1, type=int)
    cart = get_cart()
    pid = str(product_id)

    if pid not in cart:
        flash("Produit introuvable dans le panier.", "warning")
        return redirect(url_for("panier.panier"))

    if quantite < 1:
        # Suppression si quantité inférieure à 1
        del cart[pid]
        flash(f"{product.nom} retiré du panier.", "info")
    elif quantite > product.stock:
        flash(f"Stock insuffisant. Maximum disponible : {product.stock}.", "warning")
    else:
        cart[pid]["quantite"] = quantite
        flash("Panier mis à jour.", "success")

    save_cart(cart)
    return redirect(url_for("panier.panier"))


@panier_bp.route("/panier/supprimer/<int:product_id>", methods=["POST"])
def supprimer(product_id):
    """Supprime un produit du panier."""
    product = Product.query.get_or_404(product_id)
    cart = get_cart()
    pid = str(product_id)

    if pid in cart:
        del cart[pid]
        save_cart(cart)
        flash(f"{product.nom} retiré du panier.", "info")

    return redirect(url_for("panier.panier"))


@panier_bp.route("/panier/vider", methods=["POST"])
def vider():
    """Vide complètement le panier."""
    save_cart({})
    flash("Votre panier a été vidé.", "info")
    return redirect(url_for("panier.panier"))


@panier_bp.route("/panier/count")
def count():
    """Retourne le nombre d'articles dans le panier en JSON (pour le badge navbar)."""
    cart = get_cart()
    return jsonify({"count": get_cart_count(cart)})