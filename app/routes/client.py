"""
FICHIER : app/routes/client.py
RÔLE    : Pages principales de l'interface client
APPORT  : Gère l'accueil, le catalogue produits, la fiche produit,
          la page avis et la page à propos du site ND's REFRESHMENT.
DÉPENDANCES : Product, Review, Banner, Promotion, paginate_query, login_required_custom
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from app.extensions import db
from app.models import Product, Review, Banner, Promotion, CATEGORIES, NOTES
from app.utils import login_required_custom, paginate_query

client_bp = Blueprint("client", __name__)


@client_bp.route("/")
def index():
    """Page d'accueil — hero, produits vedettes, bannières et promotions actives."""
    # Bannières actives triées par ordre d'affichage
    banners = Banner.query.filter_by(active=True).order_by(Banner.ordre).all()
    banners = [b for b in banners if b.is_active()]

    # Produits vedettes (8 derniers produits disponibles)
    produits_vedettes = Product.query.filter_by(
        disponible=True
    ).order_by(Product.created_at.desc()).limit(8).all()

    # Promotions actives
    promotions = Promotion.query.filter_by(active=True).all()
    promotions = [p for p in promotions if p.is_active()]

    return render_template(
        "client/index.html",
        banners=banners,
        produits_vedettes=produits_vedettes,
        promotions=promotions
    )


@client_bp.route("/produits")
def produits():
    """Catalogue produits avec filtres par catégorie et recherche."""
    page = request.args.get("page", 1, type=int)
    categorie = request.args.get("categorie", "")
    recherche = request.args.get("q", "").strip()

    # Construction de la requête
    query = Product.query.filter_by(disponible=True)

    if categorie:
        query = query.filter_by(categorie=categorie)

    if recherche:
        query = query.filter(
            Product.nom.ilike(f"%{recherche}%") |
            Product.description.ilike(f"%{recherche}%")
        )

    query = query.order_by(Product.created_at.desc())
    produits = paginate_query(query, page, per_page=12)

    return render_template(
        "client/produits.html",
        produits=produits,
        categories=CATEGORIES,
        categorie_active=categorie,
        recherche=recherche
    )


@client_bp.route("/produits/<int:product_id>")
def produit_detail(product_id):
    """Fiche détaillée d'un produit avec ses avis et promotions."""
    product = Product.query.get_or_404(product_id)

    # Promotion active sur ce produit
    promo_active = next(
        (p for p in product.promotions if p.is_active()), None
    )

    # Avis approuvés uniquement
    avis = Review.query.filter_by(
        product_id=product_id, approuve=True
    ).order_by(Review.created_at.desc()).all()

    # Vérifier si le client a déjà laissé un avis
    deja_avis = False
    if current_user.is_authenticated:
        deja_avis = Review.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first() is not None

    return render_template(
        "client/produit_detail.html",
        product=product,
        promo_active=promo_active,
        avis=avis,
        deja_avis=deja_avis,
        notes=NOTES
    )


@client_bp.route("/avis", methods=["GET", "POST"])
@login_required_custom
def avis():
    """Page avis — dépôt d'un avis sur un produit acheté."""
    if request.method == "POST":
        product_id = request.form.get("product_id", type=int)
        note = request.form.get("note", type=int)
        commentaire = request.form.get("commentaire", "").strip()

        if not all([product_id, note]):
            flash("Veuillez renseigner tous les champs obligatoires.", "danger")
            return redirect(url_for("client.avis"))

        if not 1 <= note <= 5:
            flash("La note doit être comprise entre 1 et 5.", "danger")
            return redirect(url_for("client.avis"))

        # Vérification doublon
        existant = Review.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()

        if existant:
            flash("Vous avez déjà laissé un avis sur ce produit.", "warning")
            return redirect(url_for("client.produit_detail", product_id=product_id))

        review = Review(
            user_id=current_user.id,
            product_id=product_id,
            note=note,
            commentaire=commentaire,
            approuve=False
        )
        db.session.add(review)
        db.session.commit()

        flash("Votre avis a été soumis et sera publié après validation.", "success")
        return redirect(url_for("client.produit_detail", product_id=product_id))

    # Produits disponibles pour laisser un avis
    produits = Product.query.filter_by(disponible=True).all()
    return render_template("client/avis.html", produits=produits, notes=NOTES)


@client_bp.route("/apropos")
def apropos():
    """Page à propos — histoire et valeurs de ND's REFRESHMENT."""
    return render_template("client/apropos.html")