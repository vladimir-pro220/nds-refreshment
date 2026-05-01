import os
from flask import Flask
from config import config
from app.extensions import db, login_manager, bcrypt, migrate, csrf

def create_app(config_name="development"):
    """Factory function — crée et configure l'application Flask."""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    app = Flask(__name__,
                template_folder=os.path.join(BASE_DIR, 'templates'),
                static_folder=os.path.join(BASE_DIR, 'static'))

    # ── Chargement de la configuration ─────────────────
    app.config.from_object(config[config_name])

    # ── Initialisation des extensions ──────────────────
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # ── Création du dossier uploads si inexistant ──────
    uploads_folder = app.config["UPLOAD_FOLDER"]
    if not os.path.exists(uploads_folder):
        os.makedirs(uploads_folder)

    # ── Enregistrement des blueprints ──────────────────
    from app.routes.auth import auth_bp
    from app.routes.client import client_bp
    from app.routes.panier import panier_bp
    from app.routes.paiement import paiement_bp
    from app.routes.profil import profil_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(panier_bp)
    app.register_blueprint(paiement_bp)
    app.register_blueprint(profil_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    # ── Gestionnaires d'erreurs ─────────────────────────
    from app.routes import errors
    app.register_error_handler(404, errors.page_404)
    app.register_error_handler(500, errors.page_500)

    return app