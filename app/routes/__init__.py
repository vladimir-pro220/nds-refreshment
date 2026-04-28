"""
FICHIER : app/routes/__init__.py
RÔLE    : Centralisation et exposition de tous les blueprints
APPORT  : Point d'entrée unique pour l'enregistrement des routes dans
          create_app() et gestion des pages d'erreur globales.
DÉPENDANCES : tous les blueprints + flask
"""
from flask import render_template


# ── Pages d'erreur globales ────────────────────────────
class errors:
    @staticmethod
    def page_404(e):
        """Page 404 — ressource introuvable."""
        return render_template("errors/404.html"), 404

    @staticmethod
    def page_500(e):
        """Page 500 — erreur interne du serveur."""
        return render_template("errors/500.html"), 500

    @staticmethod
    def page_403(e):
        """Page 403 — accès refusé."""
        return render_template("errors/403.html"), 403