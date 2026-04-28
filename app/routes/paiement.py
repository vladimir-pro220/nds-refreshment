"""
FICHIER : app/routes/paiement.py
RÔLE    : Gestion du processus de paiement et validation des commandes
APPORT  : Transforme le panier session en commande réelle en base de données
          et vide le panier après confirmation de la commande.
DÉPENDANCES : Order, OrderItem, Product, Promotion, login_required_custom
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import current_user
from app.extensions import db
from app.models import Order, OrderItem, Product, Promotion
from app.utils import login_required_custom, get_cart_count

paiement_bp = Blueprint("paiement", __name__)


def get_cart():
    """Récupère le panier depuis la session."""
    return session.get("panier", {})


@paiement_bp.route("/paiement", methods=["GET", "POST"])
@login_required_custom
def paiement():
    """Affiche le formulaire de paiement et valide la commande."""
    cart = get_cart()

    # Redirection si panier vide
    if not cart:
        flash("Votre panier est vide.", "warning")
        return redirect(url_for("panier.panier"))

    # Récupération des produits du panier
    product_ids = [int(pid) for pid in cart.keys()]
    products = {p.id: p for p in Product.query.filter(
        Product.id.in_(product_ids)
    ).all()}

    # Construction des lignes et calcul du total
    lignes = []
    total = 0
    for product_id, item in cart.items():
        product = products.get(int(product_id))
        if product:
            promo_active = next(
                (p for p in product.promotions if p.is_active()), None
            )
            prix = promo_active.prix_promo() if promo_active else product.prix
            sous_total = prix * item["quantite"]
            total += sous_total
            lignes.append({
                "product": product,
                "quantite": item["quantite"],
                "prix": prix,
                "promo": promo_active,
                "sous_total": sous_total
            })

    if request.method == "POST":
        adresse = request.form.get("adresse_livraison", "").strip()
        telephone = request.form.get("telephone", "").strip()
        note_client = request.form.get("note_client", "").strip()

        # Vérifications
        if not adresse or not telephone:
            flash("L'adresse de livraison et le téléphone sont obligatoires.", "danger")
            return render_template(
                "client/paiement.html",
                lignes=lignes,
                total=total,
                count=get_cart_count(cart)
            )

        # Vérification stock avant création commande
        for product_id, item in cart.items():
            product = products.get(int(product_id))
            if not product or not product.is_available():
                flash(f"Le produit {product.nom} n'est plus disponible.", "danger")
                return redirect(url_for("panier.panier"))
            if item["quantite"] > product.stock:
                flash(f"Stock insuffisant pour {product.nom}.", "danger")
                return redirect(url_for("panier.panier"))

        # Création de la commande
        order = Order(
            user_id=current_user.id,
            statut="en_attente",
            total=total,
            adresse_livraison=adresse,
            telephone=telephone,
            note_client=note_client if note_client else None
        )
        db.session.add(order)
        db.session.flush()  # Génère l'id de la commande sans commit

        # Création des lignes de commande et mise à jour du stock
        for product_id, item in cart.items():
            product = products.get(int(product_id))
            if product:
                promo_active = next(
                    (p for p in product.promotions if p.is_active()), None
                )
                prix = promo_active.prix_promo() if promo_active else product.prix

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantite=item["quantite"],
                    prix_unitaire=prix
                )
                db.session.add(order_item)

                # Mise à jour du stock
                product.stock -= item["quantite"]
                if product.stock == 0:
                    product.disponible = False

        db.session.commit()

        # Vidage du panier après commande réussie
        session.pop("panier", None)
        session.modified = True

        flash("Votre commande a été passée avec succès !", "success")
        return redirect(url_for("paiement.confirmation", order_id=order.id))

    return render_template(
        "client/paiement.html",
        lignes=lignes,
        total=total,
        count=get_cart_count(cart)
    )


@paiement_bp.route("/paiement/confirmation/<int:order_id>")
@login_required_custom
def confirmation(order_id):
    """Page de confirmation après une commande réussie."""
    order = Order.query.get_or_404(order_id)

    # Sécurité : un client ne peut voir que ses propres commandes
    if order.user_id != current_user.id:
        flash("Accès refusé.", "danger")
        return redirect(url_for("client.index"))

    return render_template("client/confirmation.html", order=order)