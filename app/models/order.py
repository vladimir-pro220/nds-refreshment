from datetime import datetime
from app.extensions import db


class Order(db.Model):
    """Modèle représentant une commande client."""

    __tablename__ = "orders"

    # ── Colonnes ───────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    statut = db.Column(db.String(20), nullable=False, default="en_attente")
    total = db.Column(db.Float, nullable=False, default=0.0)
    adresse_livraison = db.Column(db.String(255), nullable=True)
    telephone = db.Column(db.String(20), nullable=True)
    note_client = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    # ── Relations ──────────────────────────────────────
    items = db.relationship("OrderItem", backref="order", lazy=True,
                            cascade="all, delete-orphan")

    # ── Méthodes utilitaires ───────────────────────────
    def calculate_total(self):
        """Calcule et met à jour le total de la commande."""
        self.total = sum(item.sous_total() for item in self.items)
        return self.total

    def formatted_total(self):
        """Retourne le total formaté en FCFA."""
        return f"{self.total:,.0f} FCFA"

    def nombre_articles(self):
        """Retourne le nombre total d'articles dans la commande."""
        return sum(item.quantite for item in self.items)

    def __repr__(self):
        return f"<Order #{self.id} - {self.statut} - {self.formatted_total()}>"


class OrderItem(db.Model):
    """Modèle représentant une ligne de commande (produit + quantité)."""

    __tablename__ = "order_items"

    # ── Colonnes ───────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantite = db.Column(db.Integer, nullable=False, default=1)
    prix_unitaire = db.Column(db.Float, nullable=False)

    # ── Méthodes utilitaires ───────────────────────────
    def sous_total(self):
        """Calcule le sous-total de la ligne (prix x quantité)."""
        return self.prix_unitaire * self.quantite

    def formatted_sous_total(self):
        """Retourne le sous-total formaté en FCFA."""
        return f"{self.sous_total():,.0f} FCFA"

    def __repr__(self):
        return f"<OrderItem produit#{self.product_id} x{self.quantite}>"


# ── Statuts disponibles ────────────────────────────────
STATUTS_COMMANDE = [
    ("en_attente", "En attente"),
    ("confirmee", "Confirmée"),
    ("en_preparation", "En préparation"),
    ("livree", "Livrée"),
    ("annulee", "Annulée"),
]