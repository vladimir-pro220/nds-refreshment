"""
FICHIER : tests/conftest.py
RÔLE    : Configuration et fixtures pytest pour les tests
APPORT  : Crée une app de test avec BDD en mémoire et des données
          de base pour tous les tests du projet.
DÉPENDANCES : pytest, Flask, SQLAlchemy, tous les modèles
"""
import pytest
from app import create_app
from app.extensions import db
from app.models import User, Product, Order, OrderItem, Review


@pytest.fixture(scope='session')
def app():
    """Crée une instance de l'app pour les tests."""
    app = create_app('testing')
    return app


@pytest.fixture(scope='session')
def client(app):
    """Crée un client HTTP de test."""
    return app.test_client()


@pytest.fixture(scope='function')
def init_db(app):
    """Crée et détruit la BDD pour chaque test."""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def admin_user(init_db, app):
    """Crée un compte admin de test."""
    with app.app_context():
        admin = User(
            nom="Admin",
            prenom="Test",
            email="admin@test.cm",
            role="admin",
            actif=True
        )
        admin.set_password("Admin@2024")
        db.session.add(admin)
        db.session.commit()
        return admin.id


@pytest.fixture(scope='function')
def client_user(init_db, app):
    """Crée un compte client de test."""
    with app.app_context():
        user = User(
            nom="Client",
            prenom="Test",
            email="client@test.cm",
            role="client",
            actif=True
        )
        user.set_password("Client@2024")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture(scope='function')
def sample_product(init_db, app):
    """Crée un produit de test."""
    with app.app_context():
        product = Product(
            nom="Jus Test",
            description="Description test",
            prix=1500.0,
            categorie="jus",
            stock=10,
            disponible=True,
            image="default.jpg"
        )
        db.session.add(product)
        db.session.commit()
        return product.id