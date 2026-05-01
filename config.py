import os
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis .env
load_dotenv()

class Config:
    """Configuration de base commune à tous les environnements."""

    # ── Sécurité ───────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "changez-moi-en-production")

    # ── Base de données ────────────────────────────────────
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI",
        f"sqlite:///{os.path.join(BASE_DIR, 'app', 'database.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Upload fichiers ────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB maximum

    # ── Sécurité admin (double mot de passe) ───────────────
    ADMIN_PASSWORD_FIXED = os.getenv("ADMIN_PASSWORD_FIXED", "divinite-saintete-purete")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin1234")


class DevelopmentConfig(Config):
    """Configuration pour le développement local."""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Affiche les requêtes SQL dans le terminal


class ProductionConfig(Config):
    """Configuration pour la mise en production."""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Configuration pour les tests automatisés."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # BDD en mémoire pour les tests
    WTF_CSRF_ENABLED = False  # Désactive CSRF pendant les tests


# Dictionnaire de mapping pour faciliter le chargement
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}