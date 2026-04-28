from datetime import datetime
from app.extensions import db


class Promotion(db.Model):
    """Modèle représentant une promotion sur un produit."""

    __tablename__ = "promotions"

    # ── Colonnes ───────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    titre = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    pourcentage = db.Column(db.Float, nullable=False)
    date_debut = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_fin = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ── Relations ──────────────────────────────────────
    product = db.relationship("Product", backref="promotions", lazy=True)

    # ── Méthodes utilitaires ───────────────────────────
    def is_active(self):
        """Vérifie si la promotion est active et dans sa période de validité."""
        now = datetime.utcnow()
        return self.active and self.date_debut <= now <= self.date_fin

    def prix_promo(self):
        """Calcule le prix après réduction."""
        return round(self.product.prix * (1 - self.pourcentage / 100), 0)

    def formatted_prix_promo(self):
        """Retourne le prix promotionnel formaté en FCFA."""
        return f"{self.prix_promo():,.0f} FCFA"

    def formatted_pourcentage(self):
        """Retourne le pourcentage formaté."""
        return f"-{self.pourcentage:.0f}%"

    def jours_restants(self):
        """Retourne le nombre de jours restants avant la fin de la promotion."""
        if not self.is_active():
            return 0
        delta = self.date_fin - datetime.utcnow()
        return delta.days

    def __repr__(self):
        return f"<Promotion {self.titre} - {self.formatted_pourcentage()} sur {self.product.nom}>"