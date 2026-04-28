import os
from app import create_app

# Chargement de la configuration selon l'environnement
config_name = os.getenv("FLASK_ENV", "development")

# Création de l'application Flask
app = create_app(config_name)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=app.config["DEBUG"]
    )