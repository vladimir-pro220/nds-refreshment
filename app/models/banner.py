from datetime import datetime
from app.extensions import db


class Banner(db.Model):
    """Modèle représentant une bannière publicitaire sur la page d'accueil."""

    __tablename__ = "banners"

    # ── Colonnes ───────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=False)
    lien_produit_id = db.Column(db.Integer, db.ForeignKey("products.id"),
                                nullable=True)
    ordre = db.Column(db.Integer, nullable=False, default=1)
    active = db.Column(db.Boolean, default=True, nullable=False)
    date_debut = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    date_fin = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ── Relations ──────────────────────────────────────
    product = db.relationship("Product", backref="banners", lazy=True)

    # ── Méthodes utilitaires ───────────────────────────
    def is_active(self):
        """Vérifie si la bannière est active et dans sa période de validité."""
        now = datetime.utcnow()
        if not self.active:
            return False
        if self.date_debut and now < self.date_debut:
            return False
        if self.date_fin and now > self.date_fin:
            return False
        return True

    def __repr__(self):
        return f"<Banner {self.titre} - ordre#{self.ordre} - actif:{self.active}>"