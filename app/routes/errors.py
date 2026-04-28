"""
FICHIER : app/routes/errors.py
RÔLE    : Gestionnaires d'erreurs HTTP de l'application ND's REFRESHMENT
APPORT  : Affiche des pages d'erreur personnalisées (404, 500) au lieu
          des pages par défaut de Flask.
DÉPENDANCES : render_template (Flask)
"""
from flask import render_template


# ══════════════════════════════════════════════════════
# ERREUR 404 — PAGE NON TROUVÉE
# ══════════════════════════════════════════════════════

def page_404(e):
    """Affiche la page d'erreur 404 personnalisée."""
    return render_template("errors/404.html"), 404


# ══════════════════════════════════════════════════════
# ERREUR 500 — ERREUR INTERNE SERVEUR
# ══════════════════════════════════════════════════════

def page_500(e):
    """Affiche la page d'erreur 500 personnalisée."""
    return render_template("errors/500.html"), 500