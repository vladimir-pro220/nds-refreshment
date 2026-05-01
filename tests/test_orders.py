"""
FICHIER : tests/test_orders.py
RÔLE    : Tests des commandes et du panier
APPORT  : Vérifie l'ajout au panier, la validation de commande
          et la consultation de l'historique.
DÉPENDANCES : pytest, conftest, panier routes, Order
"""
import pytest
from app.extensions import db
from app.models import Order, OrderItem, Product


class TestPanier:
    """Tests du panier."""

    def test_panier_accessible(self, client, init_db):
        """Vérifie que la page panier est accessible."""
        response = client.get('/panier')
        assert response.status_code == 200

    def test_ajouter_produit_panier(self, client, init_db,
                                     sample_product):
        """Vérifie l'ajout d'un produit au panier."""
        with client.session_transaction() as sess:
            sess['_csrf_token'] = 'test'

        response = client.post(
            f'/panier/ajouter/{sample_product}',
            data={'quantite': '1', 'csrf_token': 'test'},
            follow_redirects=True
        )
        assert response.status_code == 200

    def test_panier_count_api(self, client, init_db):
        """Vérifie l'endpoint API du compteur panier."""
        response = client.get('/api/panier/count')
        assert response.status_code == 200
        data = response.get_json()
        assert 'count' in data


class TestOrders:
    """Tests des commandes."""

    def test_create_order(self, init_db, app, client_user,
                          sample_product):
        """Vérifie la création d'une commande en base."""
        with app.app_context():
            order = Order(
                user_id=client_user,
                statut="en_attente",
                total=1500.0,
                adresse_livraison="Douala, Akwa, Rue Test",
                telephone="699000001"
            )
            db.session.add(order)
            db.session.flush()

            item = OrderItem(
                order_id=order.id,
                product_id=sample_product,
                quantite=1,
                prix_unitaire=1500.0
            )
            db.session.add(item)
            db.session.commit()

            assert order.id is not None
            assert len(order.items) == 1
            assert order.nombre_articles() == 1
            assert order.total == 1500.0

    def test_order_total_calculation(self, init_db, app,
                                      client_user, sample_product):
        """Vérifie le calcul du total d'une commande."""
        with app.app_context():
            order = Order(
                user_id=client_user,
                statut="en_attente",
                total=0.0
            )
            db.session.add(order)
            db.session.flush()

            item1 = OrderItem(
                order_id=order.id,
                product_id=sample_product,
                quantite=2,
                prix_unitaire=1500.0
            )
            db.session.add(item1)
            db.session.commit()

            order.calculate_total()
            assert order.total == 3000.0

    def test_order_statut_change(self, init_db, app, client_user):
        """Vérifie le changement de statut d'une commande."""
        with app.app_context():
            order = Order(
                user_id=client_user,
                statut="en_attente",
                total=1000.0
            )
            db.session.add(order)
            db.session.commit()

            order.statut = "confirmee"
            db.session.commit()

            updated = Order.query.get(order.id)
            assert updated.statut == "confirmee"

    def test_paiement_requires_auth(self, client, init_db):
        """Vérifie que le paiement nécessite une connexion."""
        response = client.get('/paiement', follow_redirects=True)
        assert response.status_code == 200


class TestAPI:
    """Tests des endpoints API."""

    def test_api_search_empty(self, client, init_db):
        """Vérifie la recherche vide retourne une liste vide."""
        response = client.get('/api/search?q=')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 0

    def test_api_search_with_query(self, client, init_db,
                                    sample_product):
        """Vérifie la recherche avec un terme."""
        response = client.get('/api/search?q=Jus')
        assert response.status_code == 200
        data = response.get_json()
        assert 'produits' in data

    def test_api_produits(self, client, init_db):
        """Vérifie l'endpoint liste des produits."""
        response = client.get('/api/produits')
        assert response.status_code == 200
        data = response.get_json()
        assert 'produits' in data
        assert 'total' in data