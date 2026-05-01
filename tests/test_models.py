"""
FICHIER : tests/test_models.py
RÔLE    : Tests unitaires des modèles SQLAlchemy
APPORT  : Vérifie que les modèles User, Product, Order et Review
          fonctionnent correctement avec leurs méthodes utilitaires.
DÉPENDANCES : pytest, conftest, tous les modèles
"""
import pytest
from app.extensions import db
from app.models import User, Product, Order, OrderItem, Review


class TestUserModel:
    """Tests du modèle User."""

    def test_create_user(self, init_db, app):
        """Vérifie la création d'un utilisateur."""
        with app.app_context():
            user = User(
                nom="Dupont",
                prenom="Jean",
                email="jean@test.cm",
                role="client",
                actif=True
            )
            user.set_password("Test@1234")
            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.email == "jean@test.cm"
            assert user.role == "client"

    def test_password_hashing(self, init_db, app):
        """Vérifie que le mot de passe est bien hashé."""
        with app.app_context():
            user = User(nom="Test", prenom="Test",
                       email="hash@test.cm", role="client")
            user.set_password("MonMotDePasse@123")
            db.session.add(user)
            db.session.commit()

            assert user.password_hash != "MonMotDePasse@123"
            assert user.check_password("MonMotDePasse@123") is True
            assert user.check_password("MauvaisMotDePasse") is False

    def test_is_admin(self, init_db, app):
        """Vérifie la méthode is_admin()."""
        with app.app_context():
            admin = User(nom="Admin", prenom="Test",
                        email="admin2@test.cm", role="admin")
            admin.set_password("Admin@2024")
            client = User(nom="Client", prenom="Test",
                         email="client2@test.cm", role="client")
            client.set_password("Client@2024")
            db.session.add_all([admin, client])
            db.session.commit()

            assert admin.is_admin() is True
            assert client.is_admin() is False

    def test_full_name(self, init_db, app):
        """Vérifie la méthode full_name()."""
        with app.app_context():
            user = User(nom="Mbopi", prenom="Clarisse",
                       email="clarisse@test.cm", role="client")
            user.set_password("Test@1234")
            db.session.add(user)
            db.session.commit()

            assert user.full_name() == "Clarisse Mbopi"


class TestProductModel:
    """Tests du modèle Product."""

    def test_create_product(self, init_db, app):
        """Vérifie la création d'un produit."""
        with app.app_context():
            product = Product(
                nom="Jus Ananas",
                prix=1500.0,
                categorie="jus",
                stock=10,
                disponible=True
            )
            db.session.add(product)
            db.session.commit()

            assert product.id is not None
            assert product.nom == "Jus Ananas"
            assert product.prix == 1500.0

    def test_is_available(self, init_db, app):
        """Vérifie la méthode is_available()."""
        with app.app_context():
            p1 = Product(nom="P1", prix=1000.0, categorie="jus",
                        stock=5, disponible=True)
            p2 = Product(nom="P2", prix=1000.0, categorie="jus",
                        stock=0, disponible=True)
            p3 = Product(nom="P3", prix=1000.0, categorie="jus",
                        stock=5, disponible=False)
            db.session.add_all([p1, p2, p3])
            db.session.commit()

            assert p1.is_available() is True
            assert p2.is_available() is False
            assert p3.is_available() is False

    def test_formatted_price(self, init_db, app):
        """Vérifie le formatage du prix en FCFA."""
        with app.app_context():
            product = Product(nom="Test", prix=1500.0,
                            categorie="jus", stock=10)
            db.session.add(product)
            db.session.commit()

            assert "FCFA" in product.formatted_price()
            assert "1" in product.formatted_price()

    def test_average_rating_no_reviews(self, init_db, app):
        """Vérifie la note moyenne sans avis."""
        with app.app_context():
            product = Product(nom="Test2", prix=1000.0,
                            categorie="jus", stock=5)
            db.session.add(product)
            db.session.commit()

            assert product.average_rating() == 0


class TestOrderModel:
    """Tests du modèle Order."""

    def test_create_order(self, init_db, app, client_user):
        """Vérifie la création d'une commande."""
        with app.app_context():
            order = Order(
                user_id=client_user,
                statut="en_attente",
                total=3000.0,
                adresse_livraison="Douala, Akwa",
                telephone="699000000"
            )
            db.session.add(order)
            db.session.commit()

            assert order.id is not None
            assert order.statut == "en_attente"
            assert order.total == 3000.0

    def test_formatted_total(self, init_db, app, client_user):
        """Vérifie le formatage du total."""
        with app.app_context():
            order = Order(
                user_id=client_user,
                statut="en_attente",
                total=5000.0
            )
            db.session.add(order)
            db.session.commit()

            assert "FCFA" in order.formatted_total()

    def test_nombre_articles(self, init_db, app, client_user,
                              sample_product):
        """Vérifie le comptage des articles."""
        with app.app_context():
            order = Order(
                user_id=client_user,
                statut="en_attente",
                total=3000.0
            )
            db.session.add(order)
            db.session.flush()

            item = OrderItem(
                order_id=order.id,
                product_id=sample_product,
                quantite=3,
                prix_unitaire=1000.0
            )
            db.session.add(item)
            db.session.commit()

            assert order.nombre_articles() == 3


class TestReviewModel:
    """Tests du modèle Review."""

    def test_stars_display(self, init_db, app, client_user,
                           sample_product):
        """Vérifie l'affichage des étoiles."""
        with app.app_context():
            review = Review(
                user_id=client_user,
                product_id=sample_product,
                note=4,
                approuve=True
            )
            db.session.add(review)
            db.session.commit()

            stars = review.stars()
            assert "★" in stars
            assert "☆" in stars
            assert stars.count("★") == 4
            assert stars.count("☆") == 1

    def test_valid_note(self, init_db, app, client_user,
                        sample_product):
        """Vérifie la validation de la note."""
        with app.app_context():
            review = Review(
                user_id=client_user,
                product_id=sample_product,
                note=5,
                approuve=False
            )
            db.session.add(review)
            db.session.commit()

            assert review.is_valid_note() is True