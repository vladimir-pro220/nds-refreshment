import os
from app import create_app

# Création de l'application Flask
app = create_app('development')

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )