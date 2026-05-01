"""
FICHIER : migrations/seed_data.py
RÔLE    : Peuplement de la base de données avec des données de test
APPORT  : Crée le compte admin, les comptes clients de test et tous
          les produits ND's REFRESHMENT avec leurs catégories.
DÉPENDANCES : init_db.py (doit être exécuté avant), tous les modèles
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import User, Product, Order, OrderItem, Review, Promotion, Banner

def seed_database():
    """Peuple la base de données avec les données initiales."""
    app = create_app('development')

    with app.app_context():
        print("Peuplement de la base de données...")

        # ── COMPTE ADMINISTRATEUR ──────────────────────
        print("\n[1/5] Création du compte administrateur...")
        admin = User(
            nom="DONFACK",
            prenom="Vladimir",
            email="admin@nds-refreshment.cm",
            role="admin",
            actif=True
        )
        admin.set_password("Admin@2024")
        db.session.add(admin)
        db.session.flush()
        print(f"  ✓ Admin créé : {admin.email} / Admin@2024")

        # ── COMPTES CLIENTS DE TEST ────────────────────
        print("\n[2/5] Création des comptes clients de test...")
        clients = [
            {
                "nom": "Fotso",
                "prenom": "Jean-Marie",
                "email": "jean.fotso@test.cm",
                "password": "Client@2024"
            },
            {
                "nom": "Mbopi",
                "prenom": "Clarisse",
                "email": "clarisse.mbopi@test.cm",
                "password": "Client@2024"
            },
            {
                "nom": "Nguessang",
                "prenom": "Paul",
                "email": "paul.nguessang@test.cm",
                "password": "Client@2024"
            }
        ]

        client_objects = []
        for c in clients:
            client = User(
                nom=c["nom"],
                prenom=c["prenom"],
                email=c["email"],
                role="client",
                actif=True
            )
            client.set_password(c["password"])
            db.session.add(client)
            client_objects.append(client)
            print(f"  ✓ Client créé : {c['email']}")

        db.session.flush()

        # ── PRODUITS ───────────────────────────────────
        print("\n[3/5] Création des produits ND's REFRESHMENT...")
        produits_data = [
            # Jus naturels
            {
                "nom": "Jus Ananas Gingembre",
                "description": "Notre best-seller ! La douceur de l'ananas "
                               "mariée au piquant naturel du gingembre frais "
                               "du Cameroun. Sans sucres ajoutés, 100% naturel.",
                "prix": 1500.0,
                "categorie": "jus",
                "stock": 50,
                "disponible": True
            },
            {
                "nom": "Jus Ananas Passion",
                "description": "Une explosion tropicale en bouche. L'ananas "
                               "frais rencontre la maracuja pour une saveur "
                               "unique et rafraîchissante.",
                "prix": 1500.0,
                "categorie": "jus",
                "stock": 45,
                "disponible": True
            },
            {
                "nom": "Jus de Baobab Pur",
                "description": "Le superaliment africain par excellence. "
                               "Riche en vitamine C et en antioxydants "
                               "naturels. Goût acidulé et désaltérant.",
                "prix": 2000.0,
                "categorie": "jus",
                "stock": 30,
                "disponible": True
            },
            {
                "nom": "Jus Ananas Nature",
                "description": "La pureté de l'ananas frais du Cameroun, "
                               "pressé à froid pour préserver tous ses "
                               "nutriments et vitamines.",
                "prix": 1200.0,
                "categorie": "jus",
                "stock": 60,
                "disponible": True
            },
            {
                "nom": "Jus d'Oseille",
                "description": "La boisson traditionnelle camerounaise "
                               "revisitée. Fraîche, légèrement acidulée "
                               "et naturellement riche en fer.",
                "prix": 1000.0,
                "categorie": "jus",
                "stock": 40,
                "disponible": True
            },
            # Cocktails
            {
                "nom": "Cocktail Tropical Mix",
                "description": "Un mélange signature sans alcool de fruits "
                               "tropicaux africains. Parfait pour vos "
                               "réceptions et événements d'entreprise.",
                "prix": 2500.0,
                "categorie": "cocktail",
                "stock": 20,
                "disponible": True
            },
            {
                "nom": "Cocktail Baobab Citron",
                "description": "L'alliance parfaite du baobab africain et "
                               "du citron vert frais. Frais et tonique pour "
                               "toutes vos occasions.",
                "prix": 2500.0,
                "categorie": "cocktail",
                "stock": 15,
                "disponible": True
            },
            # Gourmandises
            {
                "nom": "Assortiment Gourmand",
                "description": "Un assortiment de petits plaisirs sucrés "
                               "et salés préparés artisanalement pour "
                               "accompagner nos jus premium.",
                "prix": 3000.0,
                "categorie": "gourmandise",
                "stock": 25,
                "disponible": True
            },
            {
                "nom": "Beignets Sucrés Maison",
                "description": "Des beignets moelleux préparés selon la "
                               "recette traditionnelle camerounaise, "
                               "légèrement sucrés et irrésistibles.",
                "prix": 1500.0,
                "categorie": "gourmandise",
                "stock": 30,
                "disponible": True
            },
            # Gamelles
            {
                "nom": "Gamelle Équilibrée du Jour",
                "description": "Un repas sain et équilibré préparé "
                               "quotidiennement avec des ingrédients "
                               "frais locaux. Livraison au bureau.",
                "prix": 2500.0,
                "categorie": "gamelle",
                "stock": 20,
                "disponible": True
            },
            {
                "nom": "Gamelle Végétarienne",
                "description": "Pour nos clients soucieux de leur santé, "
                               "une gamelle 100% végétarienne riche en "
                               "protéines végétales et légumes frais.",
                "prix": 2000.0,
                "categorie": "gamelle",
                "stock": 15,
                "disponible": True
            },
            # Gâteaux
            {
                "nom": "Gâteau d'Anniversaire Sur Mesure",
                "description": "Des créations artisanales sur mesure pour "
                               "vos anniversaires. Design personnalisé, "
                               "saveurs au choix. Commande 48h à l'avance.",
                "prix": 15000.0,
                "categorie": "gateau",
                "stock": 10,
                "disponible": True
            },
            {
                "nom": "Cupcakes Assortis (12 pièces)",
                "description": "Une boîte de 12 cupcakes moelleux aux "
                               "saveurs variées : vanille, chocolat, "
                               "fraise et passion. Parfaits pour offrir.",
                "prix": 5000.0,
                "categorie": "gateau",
                "stock": 20,
                "disponible": True
            },
            # Autres
            {
                "nom": "Pack Découverte ND's",
                "description": "Le coffret idéal pour découvrir l'univers "
                               "ND's REFRESHMENT : 3 jus au choix + "
                               "1 assortiment gourmand.",
                "prix": 5000.0,
                "categorie": "autre",
                "stock": 15,
                "disponible": True
            },
        ]

        product_objects = []
        for p in produits_data:
            product = Product(
                nom=p["nom"],
                description=p["description"],
                prix=p["prix"],
                categorie=p["categorie"],
                stock=p["stock"],
                disponible=p["disponible"],
                image="default.jpg"
            )
            db.session.add(product)
            product_objects.append(product)
            print(f"  ✓ Produit : {p['nom']} — {p['prix']:,.0f} FCFA")

        db.session.flush()

        # ── AVIS DE TEST ───────────────────────────────
        print("\n[4/5] Création des avis de test...")
        avis_data = [
            {
                "user": client_objects[0],
                "product": product_objects[0],
                "note": 5,
                "commentaire": "Excellent jus ! Le gingembre donne un "
                               "goût unique. Je commande chaque semaine.",
                "approuve": True
            },
            {
                "user": client_objects[1],
                "product": product_objects[2],
                "note": 5,
                "commentaire": "Le Baobab est une vraie découverte. "
                               "Très riche en vitamines et délicieux.",
                "approuve": True
            },
            {
                "user": client_objects[2],
                "product": product_objects[0],
                "note": 4,
                "commentaire": "Très bon jus, livraison rapide. "
                               "Je recommande vivement.",
                "approuve": True
            },
        ]

        for a in avis_data:
            review = Review(
                user_id=a["user"].id,
                product_id=a["product"].id,
                note=a["note"],
                commentaire=a["commentaire"],
                approuve=a["approuve"]
            )
            db.session.add(review)
            print(f"  ✓ Avis : {a['user'].prenom} sur {a['product'].nom}")

        # ── PROMOTION DE TEST ──────────────────────────
        print("\n[5/5] Création d'une promotion de test...")
        promo = Promotion(
            titre="Offre Lancement — Ananas Gingembre",
            description="Profitez de 20% de réduction sur notre "
                        "best-seller pour fêter le lancement du site !",
            product_id=product_objects[0].id,
            pourcentage=20.0,
            date_debut=datetime.utcnow(),
            date_fin=datetime.utcnow() + timedelta(days=30),
            active=True
        )
        db.session.add(promo)
        print(f"  ✓ Promotion : -20% sur Jus Ananas Gingembre (30 jours)")

        # ── COMMIT FINAL ───────────────────────────────
        db.session.commit()

        print("\n" + "="*50)
        print("Base de données peuplée avec succès !")
        print("="*50)
        print("\nComptes de test :")
        print(f"  Admin    : admin@nds-refreshment.cm / Admin@2024")
        print(f"  Client 1 : jean.fotso@test.cm / Client@2024")
        print(f"  Client 2 : clarisse.mbopi@test.cm / Client@2024")
        print(f"  Client 3 : paul.nguessang@test.cm / Client@2024")
        print(f"\nMot de passe constructeur : défini dans .env")
        print(f"Produits créés : {len(product_objects)}")
        print(f"Avis créés     : {len(avis_data)}")
        print(f"Promotions     : 1")

if __name__ == "__main__":
    seed_database()