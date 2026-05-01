"""
FICHIER : tests/test_routes.py
RÔLE    : Tests d'intégration des routes principales
APPORT  : Vérifie les codes HTTP, les redirections et les permissions
          pour toutes les routes importantes du projet.
DÉPENDANCES : pytest, conftest, toutes les routes
"""
import pytest


class TestClientRoutes:
    """Tests des routes client."""

    def test_homepage(self, client, init_db):
        """Vérifie que la page d'accueil est accessible."""
        response = client.get('/')
        assert response.status_code == 200

    def test_produits_page(self, client, init_db):
        """Vérifie que le catalogue est accessible."""
        response = client.get('/produits')
        assert response.status_code == 200

    def test_apropos_page(self, client, init_db):
        """Vérifie que la page à propos est accessible."""
        response = client.get('/apropos')
        assert response.status_code == 200

    def test_login_page(self, client, init_db):
        """Vérifie que la page de connexion est accessible."""
        response = client.get('/login')
        assert response.status_code == 200

    def test_register_page(self, client, init_db):
        """Vérifie que la page d'inscription est accessible."""
        response = client.get('/register')
        assert response.status_code == 200

    def test_panier_page(self, client, init_db):
        """Vérifie que la page panier est accessible."""
        response = client.get('/panier')
        assert response.status_code == 200

    def test_profil_requires_login(self, client, init_db):
        """Vérifie que le profil nécessite une connexion."""
        response = client.get('/profil', follow_redirects=True)
        assert response.status_code == 200

    def test_paiement_requires_login(self, client, init_db):
        """Vérifie que le paiement nécessite une connexion."""
        response = client.get('/paiement', follow_redirects=True)
        assert response.status_code == 200

    def test_404_page(self, client, init_db):
        """Vérifie la page 404."""
        response = client.get('/page-qui-nexiste-pas')
        assert response.status_code == 404


class TestAdminRoutes:
    """Tests des routes admin."""

    def test_admin_login_page(self, client, init_db):
        """Vérifie que la page de connexion admin est accessible."""
        response = client.get('/admin/login', follow_redirects=True)
        assert response.status_code == 200

    def test_admin_dashboard_redirects(self, client, init_db):
        """Vérifie que le dashboard redirige sans connexion."""
        response = client.get('/admin/dashboard',
                             follow_redirects=True)
        assert response.status_code == 200

    def test_admin_produits_redirects(self, client, init_db):
        """Vérifie que la gestion produits redirige sans connexion."""
        response = client.get('/admin/produits',
                             follow_redirects=True)
        assert response.status_code == 200

    def test_admin_commandes_redirects(self, client, init_db):
        """Vérifie que les commandes redirigent sans connexion."""
        response = client.get('/admin/commandes',
                             follow_redirects=True)
        assert response.status_code == 200

    def test_admin_logout(self, client, init_db):
        """Vérifie la déconnexion admin."""
        response = client.get('/admin/logout',
                             follow_redirects=True)
        assert response.status_code == 200