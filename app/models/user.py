from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt


class User(UserMixin, db.Model):
    """Modèle représentant un utilisateur (client ou admin)."""

    __tablename__ = "users"

    # ── Colonnes ───────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="client")
    actif = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    # ── Relations ──────────────────────────────────────
    orders = db.relationship("Order", backref="client", lazy=True,
                             cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="auteur", lazy=True,
                              cascade="all, delete-orphan")

    # ── Méthodes mot de passe ──────────────────────────
    def set_password(self, password):
        """Chiffre et stocke le mot de passe."""
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        """Vérifie si le mot de passe fourni correspond au hash stocké."""
        return bcrypt.check_password_hash(self.password_hash, password)

    # ── Méthodes utilitaires ───────────────────────────
    def is_admin(self):
        """Retourne True si l'utilisateur est administrateur."""
        return self.role == "admin"

    def full_name(self):
        """Retourne le nom complet de l'utilisateur."""
        return f"{self.prenom} {self.nom}"

    def __repr__(self):
        return f"<User {self.email} - {self.role}>"