"""
FICHIER : app/routes/admin.py
RÔLE    : Interface d'administration complète du site ND's REFRESHMENT
APPORT  : Gère la connexion admin, le dashboard, les produits, les commandes,
          les avis, les bannières, les promotions et la gestion du mot de passe.
DÉPENDANCES : User, Product, Order, Review, Banner, Promotion, admin_required,
              login_admin, change_password_by_admin, reset_password_by_constructor
"""
from flask import (Blueprint, render_template, request, flash,
                   redirect, url_for, session)
from app.extensions import db
from app.models import (User, Product, Order, Review, Banner,
                        Promotion, CATEGORIES, STATUTS_COMMANDE)
from app.utils import (admin_required, get_stats, save_image,
                       delete_image, paginate_query, format_date)
from app.utils.security import (login_admin, change_password_by_admin,
                                reset_password_by_constructor)

admin_bp = Blueprint("admin", __name__)


# ══════════════════════════════════════════════════════
# CONNEXION / DÉCONNEXION ADMIN
# ══════════════════════════════════════════════════════

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    """Page de connexion administrateur."""
    if session.get("admin_connecte"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        password = request.form.get("password", "")

        if not password:
            flash("Veuillez saisir votre mot de passe.", "danger")
            return render_template("admin/login.html")

        autorise, est_constructeur = login_admin(password)

        if not autorise:
            flash("Identifiants incorrects.", "danger")
            return render_template("admin/login.html")

        # Stockage de la session admin (invisible pour l'utilisateur)
        session["admin_connecte"] = True
        session["est_constructeur"] = est_constructeur
        session.permanent = True

        flash("Connexion réussie !", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    """Déconnexion administrateur."""
    session.pop("admin_connecte", None)
    session.pop("est_constructeur", None)
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("admin.login"))


# ══════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════

@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    """Tableau de bord avec statistiques globales."""
    stats = get_stats()
    commandes_recentes = Order.query.order_by(
        Order.created_at.desc()
    ).limit(10).all()
    avis_en_attente = Review.query.filter_by(approuve=False).count()

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        commandes_recentes=commandes_recentes,
        avis_en_attente=avis_en_attente
    )


# ══════════════════════════════════════════════════════
# GESTION DES PRODUITS
# ══════════════════════════════════════════════════════

@admin_bp.route("/produits")
@admin_required
def produits():
    """Liste tous les produits avec barre de recherche."""
    page = request.args.get("page", 1, type=int)
    recherche = request.args.get("q", "").strip()

    query = Product.query
    if recherche:
        query = query.filter(
            Product.nom.ilike(f"%{recherche}%")
        )

    query = query.order_by(Product.created_at.desc())
    produits = paginate_query(query, page, per_page=15)

    return render_template(
        "admin/produits.html",
        produits=produits,
        recherche=recherche
    )


@admin_bp.route("/produits/nouveau", methods=["GET", "POST"])
@admin_required
def nouveau_produit():
    """Formulaire d'ajout d'un nouveau produit."""
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        description = request.form.get("description", "").strip()
        prix = request.form.get("prix", type=float)
        categorie = request.form.get("categorie", "").strip()
        stock = request.form.get("stock", 0, type=int)
        disponible = request.form.get("disponible") == "on"
        image = request.files.get("image")

        # Vérifications
        if not all([nom, prix, categorie]):
            flash("Le nom, le prix et la catégorie sont obligatoires.", "danger")
            return render_template("admin/nouveau_produit.html",
                                   categories=CATEGORIES)

        if prix <= 0:
            flash("Le prix doit être supérieur à 0.", "danger")
            return render_template("admin/nouveau_produit.html",
                                   categories=CATEGORIES)

        # Sauvegarde image
        image_filename = "default.jpg"
        if image and image.filename:
            saved = save_image(image)
            if saved:
                image_filename = saved
            else:
                flash("Format d'image non supporté. Utilisez PNG, JPG ou WEBP.", "warning")

        product = Product(
            nom=nom,
            description=description,
            prix=prix,
            categorie=categorie,
            stock=stock,
            disponible=disponible,
            image=image_filename
        )
        db.session.add(product)
        db.session.commit()

        flash(f"Produit '{nom}' ajouté avec succès.", "success")
        return redirect(url_for("admin.produits"))

    return render_template("admin/nouveau_produit.html", categories=CATEGORIES)


@admin_bp.route("/produits/modifier/<int:product_id>", methods=["GET", "POST"])
@admin_required
def modifier_produit(product_id):
    """Formulaire de modification d'un produit existant."""
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        product.nom = request.form.get("nom", "").strip()
        product.description = request.form.get("description", "").strip()
        product.prix = request.form.get("prix", type=float)
        product.categorie = request.form.get("categorie", "").strip()
        product.stock = request.form.get("stock", 0, type=int)
        product.disponible = request.form.get("disponible") == "on"
        image = request.files.get("image")

        # Vérifications
        if not all([product.nom, product.prix, product.categorie]):
            flash("Le nom, le prix et la catégorie sont obligatoires.", "danger")
            return render_template("admin/modifier_produit.html",
                                   product=product, categories=CATEGORIES)

        # Mise à jour image si nouvelle image uploadée
        if image and image.filename:
            saved = save_image(image)
            if saved:
                delete_image(product.image)
                product.image = saved
            else:
                flash("Format d'image non supporté.", "warning")

        db.session.commit()
        flash(f"Produit '{product.nom}' modifié avec succès.", "success")
        return redirect(url_for("admin.produits"))

    return render_template("admin/modifier_produit.html",
                           product=product, categories=CATEGORIES)


@admin_bp.route("/produits/supprimer/<int:product_id>", methods=["POST"])
@admin_required
def supprimer_produit(product_id):
    """Supprime un produit et son image associée."""
    product = Product.query.get_or_404(product_id)
    delete_image(product.image)
    db.session.delete(product)
    db.session.commit()
    flash(f"Produit '{product.nom}' supprimé avec succès.", "success")
    return redirect(url_for("admin.produits"))


# ══════════════════════════════════════════════════════
# GESTION DES COMMANDES
# ══════════════════════════════════════════════════════

@admin_bp.route("/commandes")
@admin_required
def commandes():
    """Liste toutes les commandes avec filtre par statut."""
    page = request.args.get("page", 1, type=int)
    statut = request.args.get("statut", "")

    query = Order.query
    if statut:
        query = query.filter_by(statut=statut)

    query = query.order_by(Order.created_at.desc())
    commandes = paginate_query(query, page, per_page=15)

    return render_template(
        "admin/commandes.html",
        commandes=commandes,
        statuts=STATUTS_COMMANDE,
        statut_actif=statut
    )


@admin_bp.route("/commandes/<int:order_id>")
@admin_required
def detail_commande(order_id):
    """Affiche le détail d'une commande."""
    order = Order.query.get_or_404(order_id)
    return render_template("admin/detail_commande.html",
                           order=order, statuts=STATUTS_COMMANDE)


@admin_bp.route("/commandes/<int:order_id>/statut", methods=["POST"])
@admin_required
def changer_statut(order_id):
    """Change le statut d'une commande."""
    order = Order.query.get_or_404(order_id)
    nouveau_statut = request.form.get("statut", "")
    statuts_valides = [s[0] for s in STATUTS_COMMANDE]

    if nouveau_statut not in statuts_valides:
        flash("Statut invalide.", "danger")
        return redirect(url_for("admin.detail_commande", order_id=order_id))

    order.statut = nouveau_statut
    db.session.commit()
    flash("Statut de la commande mis à jour.", "success")
    return redirect(url_for("admin.detail_commande", order_id=order_id))


# ══════════════════════════════════════════════════════
# GESTION DES AVIS
# ══════════════════════════════════════════════════════

@admin_bp.route("/avis")
@admin_required
def avis():
    """Liste tous les avis avec filtre par statut d'approbation."""
    page = request.args.get("page", 1, type=int)
    filtre = request.args.get("filtre", "tous")

    query = Review.query
    if filtre == "approuves":
        query = query.filter_by(approuve=True)
    elif filtre == "en_attente":
        query = query.filter_by(approuve=False)

    query = query.order_by(Review.created_at.desc())
    avis = paginate_query(query, page, per_page=15)

    return render_template(
        "admin/avis.html",
        avis=avis,
        filtre=filtre
    )


@admin_bp.route("/avis/<int:review_id>/approuver", methods=["POST"])
@admin_required
def approuver_avis(review_id):
    """Approuve un avis client."""
    review = Review.query.get_or_404(review_id)
    review.approuve = True
    db.session.commit()
    flash("Avis approuvé et publié.", "success")
    return redirect(url_for("admin.avis"))


@admin_bp.route("/avis/<int:review_id>/supprimer", methods=["POST"])
@admin_required
def supprimer_avis(review_id):
    """Supprime un avis client."""
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash("Avis supprimé.", "success")
    return redirect(url_for("admin.avis"))


# ══════════════════════════════════════════════════════
# GESTION DES BANNIÈRES
# ══════════════════════════════════════════════════════

@admin_bp.route("/bannieres")
@admin_required
def bannieres():
    """Liste toutes les bannières publicitaires."""
    bannieres = Banner.query.order_by(Banner.ordre).all()
    return render_template("admin/bannieres.html", bannieres=bannieres)


@admin_bp.route("/bannieres/nouvelle", methods=["GET", "POST"])
@admin_required
def nouvelle_banniere():
    """Formulaire d'ajout d'une nouvelle bannière."""
    if request.method == "POST":
        titre = request.form.get("titre", "").strip()
        description = request.form.get("description", "").strip()
        ordre = request.form.get("ordre", 1, type=int)
        active = request.form.get("active") == "on"
        lien_produit_id = request.form.get("lien_produit_id", type=int)
        image = request.files.get("image")

        if not titre or not image:
            flash("Le titre et l'image sont obligatoires.", "danger")
            produits = Product.query.filter_by(disponible=True).all()
            return render_template("admin/nouvelle_banniere.html",
                                   produits=produits)

        saved = save_image(image)
        if not saved:
            flash("Format d'image non supporté.", "warning")
            produits = Product.query.filter_by(disponible=True).all()
            return render_template("admin/nouvelle_banniere.html",
                                   produits=produits)

        banniere = Banner(
            titre=titre,
            description=description,
            image=saved,
            ordre=ordre,
            active=active,
            lien_produit_id=lien_produit_id if lien_produit_id else None
        )
        db.session.add(banniere)
        db.session.commit()

        flash(f"Bannière '{titre}' ajoutée avec succès.", "success")
        return redirect(url_for("admin.bannieres"))

    produits = Product.query.filter_by(disponible=True).all()
    return render_template("admin/nouvelle_banniere.html", produits=produits)


@admin_bp.route("/bannieres/supprimer/<int:banner_id>", methods=["POST"])
@admin_required
def supprimer_banniere(banner_id):
    """Supprime une bannière et son image associée."""
    banniere = Banner.query.get_or_404(banner_id)
    delete_image(banniere.image)
    db.session.delete(banniere)
    db.session.commit()
    flash(f"Bannière '{banniere.titre}' supprimée.", "success")
    return redirect(url_for("admin.bannieres"))


# ══════════════════════════════════════════════════════
# GESTION DES PROMOTIONS
# ══════════════════════════════════════════════════════

@admin_bp.route("/promotions")
@admin_required
def promotions():
    """Liste toutes les promotions."""
    promotions = Promotion.query.order_by(
        Promotion.created_at.desc()
    ).all()
    return render_template("admin/promotions.html", promotions=promotions)


@admin_bp.route("/promotions/nouvelle", methods=["GET", "POST"])
@admin_required
def nouvelle_promotion():
    """Formulaire d'ajout d'une nouvelle promotion."""
    if request.method == "POST":
        titre = request.form.get("titre", "").strip()
        description = request.form.get("description", "").strip()
        product_id = request.form.get("product_id", type=int)
        pourcentage = request.form.get("pourcentage", type=float)
        date_debut = request.form.get("date_debut", "").strip()
        date_fin = request.form.get("date_fin", "").strip()
        active = request.form.get("active") == "on"

        if not all([titre, product_id, pourcentage, date_debut, date_fin]):
            flash("Tous les champs sont obligatoires.", "danger")
            produits = Product.query.filter_by(disponible=True).all()
            return render_template("admin/nouvelle_promotion.html",
                                   produits=produits)

        if not 1 <= pourcentage <= 99:
            flash("Le pourcentage doit être compris entre 1 et 99.", "danger")
            produits = Product.query.filter_by(disponible=True).all()
            return render_template("admin/nouvelle_promotion.html",
                                   produits=produits)

        from datetime import datetime
        try:
            debut = datetime.strptime(date_debut, "%Y-%m-%d")
            fin = datetime.strptime(date_fin, "%Y-%m-%d")
        except ValueError:
            flash("Format de date invalide.", "danger")
            produits = Product.query.filter_by(disponible=True).all()
            return render_template("admin/nouvelle_promotion.html",
                                   produits=produits)

        if fin <= debut:
            flash("La date de fin doit être après la date de début.", "danger")
            produits = Product.query.filter_by(disponible=True).all()
            return render_template("admin/nouvelle_promotion.html",
                                   produits=produits)

        promotion = Promotion(
            titre=titre,
            description=description,
            product_id=product_id,
            pourcentage=pourcentage,
            date_debut=debut,
            date_fin=fin,
            active=active
        )
        db.session.add(promotion)
        db.session.commit()

        flash(f"Promotion '{titre}' ajoutée avec succès.", "success")
        return redirect(url_for("admin.promotions"))

    produits = Product.query.filter_by(disponible=True).all()
    return render_template("admin/nouvelle_promotion.html", produits=produits)


@admin_bp.route("/promotions/supprimer/<int:promotion_id>", methods=["POST"])
@admin_required
def supprimer_promotion(promotion_id):
    """Supprime une promotion."""
    promotion = Promotion.query.get_or_404(promotion_id)
    db.session.delete(promotion)
    db.session.commit()
    flash(f"Promotion '{promotion.titre}' supprimée.", "success")
    return redirect(url_for("admin.promotions"))


# ══════════════════════════════════════════════════════
# GESTION DU MOT DE PASSE
# ══════════════════════════════════════════════════════

@admin_bp.route("/password", methods=["GET", "POST"])
@admin_required
def password():
    """Gestion du mot de passe admin et réinitialisation par le constructeur."""
    est_constructeur = session.get("est_constructeur", False)

    if request.method == "POST":
        action = request.form.get("action", "")

        # Action : admin change son propre mot de passe
        if action == "changer":
            old_password = request.form.get("old_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            succes, message = change_password_by_admin(
                old_password, new_password, confirm_password
            )
            if succes:
                flash(message, "success")
                return redirect(url_for("admin.dashboard"))
            flash(message, "danger")

        # Action : constructeur réinitialise le mot de passe admin
        elif action == "reinitialiser" and est_constructeur:
            fixed_password = request.form.get("fixed_password", "")
            new_password = request.form.get("new_password_reset", "")
            confirm_password = request.form.get("confirm_password_reset", "")

            succes, message = reset_password_by_constructor(
                fixed_password, new_password, confirm_password
            )
            if succes:
                flash(message, "success")
                return redirect(url_for("admin.dashboard"))
            flash(message, "danger")

    return render_template(
        "admin/password.html",
        est_constructeur=est_constructeur
    )