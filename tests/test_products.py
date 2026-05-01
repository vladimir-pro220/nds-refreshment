"""
FICHIER : tests/test_products.py
RÔLE    : Tests CRUD des produits côté admin
APPORT  : Vérifie l'ajout, la modification et la suppression
          de produits depuis l'interface admin.
DÉPENDANCES : pytest, conftest, admin routes, Product
"""
import pytest
from app.extensions import db
from app.models import Product


class TestProductRoutes:
    """Tests des routes produits."""

    def test_catalogue_accessible(self, client, init_db):
        """Vérifie que le catalogue est accessible."""
        response = client.get('/produits')
        assert response.status_code == 200

    def test_catalogue_with_search(self, client, init_db,
                                    sample_product):
        """Vérifie la recherche dans le catalogue."""
        response = client.get('/produits?q=Jus')
        assert response.status_code == 200

    def test_product_detail_accessible(self, client, init_db,
                                        sample_product):
        """Vérifie que la fiche produit est accessible."""
        response = client.get(f'/produits/{sample_product}')
        assert response.status_code == 200

    def test_product_detail_not_found(self, client, init_db):
        """Vérifie la page 404 pour un produit inexistant."""
        response = client.get('/produits/9999')
        assert response.status_code == 404

    def test_admin_products_requires_auth(self, client, init_db):
        """Vérifie que la gestion produits nécessite une connexion."""
        response = client.get('/admin/produits',
                             follow_redirects=True)
        assert response.status_code == 200


class TestProductCRUD:
    """Tests CRUD produits."""

    def test_create_product(self, init_db, app):
        """Vérifie la création d'un produit en base."""
        with app.app_context():
            product = Product(
                nom="Nouveau Jus",
                description="Test",
                prix=2000.0,
                categorie="jus",
                stock=20,
                disponible=True,
                image="default.jpg"
            )
            db.session.add(product)
            db.session.commit()

            found = Product.query.filter_by(nom="Nouveau Jus").first()
            assert found is not None
            assert found.prix == 2000.0

    def test_update_product(self, init_db, app, sample_product):
        """Vérifie la modification d'un produit."""
        with app.app_context():
            product = Product.query.get(sample_product)
            product.prix = 2500.0
            product.stock = 5
            db.session.commit()

            updated = Product.query.get(sample_product)
            assert updated.prix == 2500.0
            assert updated.stock == 5

    def test_delete_product(self, init_db, app, sample_product):
        """Vérifie la suppression d'un produit."""
        with app.app_context():
            product = Product.query.get(sample_product)
            db.session.delete(product)
            db.session.commit()

            deleted = Product.query.get(sample_product)
            assert deleted is None

    def test_product_unavailable_when_stock_zero(self, init_db, app):
        """Vérifie qu'un produit avec stock 0 est indisponible."""
        with app.app_context():
            product = Product(
                nom="Produit Epuise",
                prix=1000.0,
                categorie="jus",
                stock=0,
                disponible=True
            )
            db.session.add(product)
            db.session.commit()

            assert product.is_available() is False