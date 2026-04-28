from datetime import datetime
from app.extensions import db


class Review(db.Model):
    """Modèle représentant un avis client sur un produit."""

    __tablename__ = "reviews"

    # ── Colonnes ───────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    note = db.Column(db.Integer, nullable=False)
    commentaire = db.Column(db.Text, nullable=True)
    approuve = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ── Contrainte unicité ─────────────────────────────
    __table_args__ = (
        db.UniqueConstraint("user_id", "product_id", name="unique_user_product_review"),
    )

    # ── Méthodes utilitaires ───────────────────────────
    def stars(self):
        """Retourne les étoiles sous forme de symboles."""
        return "★" * self.note + "☆" * (5 - self.note)

    def is_valid_note(self):
        """Vérifie que la note est bien comprise entre 1 et 5."""
        return 1 <= self.note <= 5

    def __repr__(self):
        return f"<Review user#{self.user_id} produit#{self.product_id} - {self.note}/5>"


# ── Notes disponibles ──────────────────────────────────
NOTES = [
    (1, "★ Très mauvais"),
    (2, "★★ Mauvais"),
    (3, "★★★ Moyen"),
    (4, "★★★★ Bien"),
    (5, "★★★★★ Excellent"),
]