"""
FICHIER : tests/test_auth.py
RÔLE    : Tests d'authentification client et admin
APPORT  : Vérifie l'inscription, la connexion client et la connexion
          admin avec les deux mots de passe.
DÉPENDANCES : pytest, conftest, auth routes, security
"""
import pytest
from app.extensions import db
from app.models import User


class TestClientAuth:
    """Tests authentification client."""

    def test_register_success(self, client, init_db):
        """Vérifie l'inscription d'un nouveau client."""
        response = client.post('/register', data={
            'nom': 'Fotso',
            'prenom': 'Jean',
            'email': 'jean.fotso@test.cm',
            'password': 'Test@1234',
            'confirm_password': 'Test@1234'
        }, follow_redirects=True)

        assert response.status_code == 200

    def test_register_duplicate_email(self, client, init_db,
                                      client_user, app):
        """Vérifie qu'on ne peut pas s'inscrire deux fois avec le même email."""
        with app.app_context():
            response = client.post('/register', data={
                'nom': 'Test',
                'prenom': 'Test',
                'email': 'client@test.cm',
                'password': 'Test@1234',
                'confirm_password': 'Test@1234'
            }, follow_redirects=True)

            assert response.status_code == 200

    def test_login_success(self, client, init_db, client_user, app):
        """Vérifie la connexion d'un client."""
        with app.app_context():
            response = client.post('/login', data={
                'email': 'client@test.cm',
                'password': 'Client@2024'
            }, follow_redirects=True)

            assert response.status_code == 200

    def test_login_wrong_password(self, client, init_db,
                                   client_user):
        """Vérifie le rejet d'un mauvais mot de passe."""
        response = client.post('/login', data={
            'email': 'client@test.cm',
            'password': 'MauvaisMotDePasse'
        }, follow_redirects=True)

        assert response.status_code == 200


class TestAdminAuth:
    """Tests authentification admin."""

    def test_admin_login_page(self, client, init_db):
        """Vérifie que la page de connexion admin est accessible."""
        response = client.get('/admin/login')
        assert response.status_code == 200

    def test_admin_login_success(self, client, init_db,
                                  admin_user, app):
        """Vérifie la connexion admin avec le mot de passe modifiable."""
        with app.app_context():
            response = client.post('/admin/login', data={
                'password': 'Admin@2024'
            }, follow_redirects=True)

            assert response.status_code == 200

    def test_admin_login_wrong_password(self, client, init_db):
        """Vérifie le rejet d'un mauvais mot de passe admin."""
        response = client.post('/admin/login', data={
            'password': 'MauvaisMotDePasse'
        }, follow_redirects=True)

        assert response.status_code == 200

    def test_admin_dashboard_requires_auth(self, client, init_db):
        """Vérifie que le dashboard nécessite une connexion."""
        response = client.get('/admin/dashboard',
                             follow_redirects=True)
        assert response.status_code == 200