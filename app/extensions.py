from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# ── Base de données ────────────────────────────────────
db = SQLAlchemy()

# ── Authentification ───────────────────────────────────
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
login_manager.login_message_category = "warning"

# ── Chiffrement des mots de passe ──────────────────────
bcrypt = Bcrypt()

# ── Migrations de base de données ─────────────────────
migrate = Migrate()

# ── Protection CSRF ────────────────────────────────────
csrf = CSRFProtect()