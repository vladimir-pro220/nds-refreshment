from datetime import datetime
from app.extensions import db


class Product(db.Model):
    """Modèle représentant un produit de ND's REFRESHMENT."""

    __tablename__ = "products"

    # ── Colonnes ───────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    prix = db.Column(db.Float, nullable=False)
    categorie = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(255), nullable=True, default="default.jpg")
    stock = db.Column(db.Integer, nullable=False, default=0)
    disponible = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    # ── Relations ──────────────────────────────────────
    order_items = db.relationship("OrderItem", backref="product", lazy=True,
                                  cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="product", lazy=True,
                              cascade="all, delete-orphan")

    # ── Méthodes utilitaires ───────────────────────────
    def is_available(self):
        """Retourne True si le produit est disponible et en stock."""
        return self.disponible and self.stock > 0

    def average_rating(self):
        """Calcule la note moyenne du produit basée sur les avis."""
        if not self.reviews:
            return 0
        return round(sum(r.note for r in self.reviews) / len(self.reviews), 1)

    def formatted_price(self):
        """Retourne le prix formaté en FCFA."""
        return f"{self.prix:,.0f} FCFA"

    def __repr__(self):
        return f"<Product {self.nom} - {self.categorie} - {self.formatted_price()}>"


# ── Catégories disponibles ─────────────────────────────
CATEGORIES = [
    ("jus", "Jus Naturels"),
    ("cocktail", "Cocktails"),
    ("gourmandise", "Gourmandises"),
    ("gamelle", "Gamelles"),
    ("gateau", "Gâteaux"),
    ("autre", "Autres"),
]