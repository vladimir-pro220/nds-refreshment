"""
FICHIER : migrations/init_db.py
RÔLE    : Initialisation du schéma de la base de données SQLite
APPORT  : Crée toutes les tables en base de données à partir des modèles
          SQLAlchemy définis dans app/models/. À exécuter une seule fois.
DÉPENDANCES : app, db, tous les modèles
"""
import sys
import os

# Ajout du dossier racine au PATH pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import User, Product, Order, OrderItem, Review, Promotion, Banner

def init_database():
    """Crée toutes les tables de la base de données."""
    app = create_app('development')

    with app.app_context():
        print("Initialisation de la base de données...")

        # Suppression des tables existantes (reset complet)
        db.drop_all()
        print("Tables existantes supprimées.")

        # Création de toutes les tables
        db.create_all()
        print("Tables créées avec succès :")

        # Liste des tables créées
        tables = [
            "users", "products", "orders",
            "order_items", "reviews",
            "promotions", "banners"
        ]
        for table in tables:
            print(f"  ✓ {table}")

        print("\nBase de données initialisée avec succès !")
        print(f"Fichier : app/database.db")

if __name__ == "__main__":
    init_database()