import sys
sys.path.insert(0, '.')
from app import create_app
from app.models import User, Product, Order, Review, Promotion

app = create_app('development')
with app.app_context():
    print('=== VÉRIFICATION BASE DE DONNÉES ===')
    print(f'Utilisateurs : {User.query.count()}')
    print(f'  - Admins   : {User.query.filter_by(role="admin").count()}')
    print(f'  - Clients  : {User.query.filter_by(role="client").count()}')
    print(f'Produits     : {Product.query.count()}')
    print(f'Avis         : {Review.query.count()}')
    print(f'Promotions   : {Promotion.query.count()}')
    print('=====================================')
    print('Tout est OK !')