"""
FICHIER : app/routes/api.py
RÔLE    : Endpoints REST JSON pour les interactions dynamiques
APPORT  : Fournit les données en JSON pour la recherche live de produits
          et le compteur du panier sans rechargement de page.
DÉPENDANCES : Product, Promotion, Banner, get_cart_count
"""
from flask import Blueprint, jsonify, request, session
from app.models import Product, Promotion, Banner, CATEGORIES
from app.utils import get_cart_count

api_bp = Blueprint("api", __name__)


@api_bp.route("/search")
def search():
    """
    Recherche live de produits.
    Retourne une liste de produits en JSON filtrés par nom ou description.
    Utilisé par search.js pour la recherche dynamique sans rechargement.
    """
    q = request.args.get("q", "").strip()
    categorie = request.args.get("categorie", "").strip()
    limit = request.args.get("limit", 10, type=int)

    if not q and not categorie:
        return jsonify({"produits": [], "total": 0})

    query = Product.query.filter_by(disponible=True)

    if q:
        query = query.filter(
            Product.nom.ilike(f"%{q}%") |
            Product.description.ilike(f"%{q}%")
        )

    if categorie:
        query = query.filter_by(categorie=categorie)

    produits = query.limit(limit).all()

    # Construction de la réponse JSON
    resultats = []
    for p in produits:
        promo_active = next(
            (promo for promo in p.promotions if promo.is_active()), None
        )
        resultats.append({
            "id": p.id,
            "nom": p.nom,
            "prix": p.prix,
            "prix_promo": promo_active.prix_promo() if promo_active else None,
            "pourcentage_promo": promo_active.pourcentage if promo_active else None,
            "categorie": p.categorie,
            "image": p.image,
            "stock": p.stock,
            "note_moyenne": p.average_rating(),
            "url": f"/produits/{p.id}"
        })

    return jsonify({
        "produits": resultats,
        "total": len(resultats),
        "query": q
    })


@api_bp.route("/produits")
def produits():
    """
    Retourne la liste complète des produits disponibles en JSON.
    Utilisé pour le chargement dynamique du catalogue.
    """
    categorie = request.args.get("categorie", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 12, type=int)

    query = Product.query.filter_by(disponible=True)

    if categorie:
        query = query.filter_by(categorie=categorie)

    query = query.order_by(Product.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    produits = []
    for p in pagination.items:
        promo_active = next(
            (promo for promo in p.promotions if promo.is_active()), None
        )
        produits.append({
            "id": p.id,
            "nom": p.nom,
            "description": p.description,
            "prix": p.prix,
            "prix_promo": promo_active.prix_promo() if promo_active else None,
            "categorie": p.categorie,
            "image": p.image,
            "stock": p.stock,
            "note_moyenne": p.average_rating(),
            "url": f"/produits/{p.id}"
        })

    return jsonify({
        "produits": produits,
        "total": pagination.total,
        "pages": pagination.pages,
        "page_actuelle": page,
        "categories": [{"valeur": c[0], "label": c[1]} for c in CATEGORIES]
    })


@api_bp.route("/panier/count")
def panier_count():
    """
    Retourne le nombre d'articles dans le panier en JSON.
    Utilisé par cart.js pour mettre à jour le badge navbar.
    """
    cart = session.get("panier", {})
    return jsonify({"count": get_cart_count(cart)})


@api_bp.route("/promotions/actives")
def promotions_actives():
    """
    Retourne toutes les promotions actives en JSON.
    Utilisé pour afficher les badges de réduction sur le catalogue.
    """
    promotions = Promotion.query.filter_by(active=True).all()
    promotions_actives = [p for p in promotions if p.is_active()]

    resultats = []
    for p in promotions_actives:
        resultats.append({
            "id": p.id,
            "titre": p.titre,
            "pourcentage": p.pourcentage,
            "product_id": p.product_id,
            "prix_promo": p.prix_promo(),
            "jours_restants": p.jours_restants()
        })

    return jsonify({
        "promotions": resultats,
        "total": len(resultats)
    })


@api_bp.route("/bannieres/actives")
def bannieres_actives():
    """
    Retourne toutes les bannières actives en JSON.
    Utilisé pour le carousel dynamique de la page d'accueil.
    """
    bannieres = Banner.query.filter_by(
        active=True
    ).order_by(Banner.ordre).all()
    bannieres_actives = [b for b in bannieres if b.is_active()]

    resultats = []
    for b in bannieres_actives:
        resultats.append({
            "id": b.id,
            "titre": b.titre,
            "description": b.description,
            "image": b.image,
            "lien_produit_id": b.lien_produit_id,
            "ordre": b.ordre
        })

    return jsonify({
        "bannieres": resultats,
        "total": len(resultats)
    })