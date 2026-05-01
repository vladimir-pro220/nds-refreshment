import sys
sys.path.insert(0, '.')
from app import create_app
from app.models import Product
from flask import session

app = create_app('development')
with app.app_context():
    print("=== PRODUITS EN BASE ===")
    produits = Product.query.all()
    for p in produits:
        print(f"  ID: {p.id} — {p.nom} — stock: {p.stock} — disponible: {p.disponible}")