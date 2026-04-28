from flask import current_app


def login_admin(password):
    """
    Vérifie le mot de passe saisi sur la page de connexion admin.
    Accepte soit le mot de passe fixe (constructeur) soit le mot de passe
    modifiable (admin normal).
    Retourne un tuple (accès_autorisé, est_constructeur).
    """
    # Vérification mot de passe fixe (constructeur)
    admin_fixed = current_app.config.get("ADMIN_PASSWORD_FIXED")
    if password == admin_fixed:
        return True, True  # accès autorisé, c'est le constructeur

    # Vérification mot de passe modifiable (admin normal)
    from app.models import User
    admin = User.query.filter_by(role="admin").first()
    if not admin:
        return False, False

    if admin.check_password(password):
        return True, False  # accès autorisé, c'est l'admin normal

    return False, False  # accès refusé


def change_password_by_admin(old_password, new_password, confirm_password):
    """
    Permet à l'admin normal de changer son mot de passe modifiable.
    Vérifie l'ancien mot de passe avant d'autoriser le changement.
    Retourne un tuple (succès, message).
    """
    # Vérification que l'ancien mot de passe est correct
    from app.models import User
    from app.extensions import db
    admin = User.query.filter_by(role="admin").first()
    if not admin:
        return False, "Compte administrateur introuvable."

    if not admin.check_password(old_password):
        return False, "Ancien mot de passe incorrect."

    # Vérification de la confirmation
    if new_password != confirm_password:
        return False, "Les deux nouveaux mots de passe ne correspondent pas."

    # Vérification longueur minimale
    if len(new_password) < 8:
        return False, "Le nouveau mot de passe doit contenir au moins 8 caractères."

    # Vérification que le nouveau mot de passe n'est pas le mot de passe fixe
    admin_fixed = current_app.config.get("ADMIN_PASSWORD_FIXED")
    if new_password == admin_fixed:
        return False, "Ce mot de passe n'est pas autorisé."

    # Mise à jour du mot de passe
    admin.set_password(new_password)
    db.session.commit()
    return True, "Mot de passe modifié avec succès."


def reset_password_by_constructor(fixed_password, new_password, confirm_password):
    """
    Permet au constructeur de réinitialiser le mot de passe modifiable.
    Utilisé quand l'admin a oublié son mot de passe.
    Retourne un tuple (succès, message).
    """
    # Vérification du mot de passe fixe
    admin_fixed = current_app.config.get("ADMIN_PASSWORD_FIXED")
    if fixed_password != admin_fixed:
        return False, "Mot de passe fixe incorrect."

    # Vérification de la confirmation
    if new_password != confirm_password:
        return False, "Les deux nouveaux mots de passe ne correspondent pas."

    # Vérification longueur minimale
    if len(new_password) < 8:
        return False, "Le nouveau mot de passe doit contenir au moins 8 caractères."

    # Vérification que le nouveau mot de passe n'est pas le mot de passe fixe
    if new_password == admin_fixed:
        return False, "Ce mot de passe n'est pas autorisé."

    # Mise à jour du mot de passe
    from app.models import User
    from app.extensions import db
    admin = User.query.filter_by(role="admin").first()
    if not admin:
        return False, "Compte administrateur introuvable."

    admin.set_password(new_password)
    db.session.commit()
    return True, "Mot de passe administrateur réinitialisé avec succès."


def is_strong_password(password):
    """
    Vérifie que le mot de passe est suffisamment fort.
    Retourne un tuple (valide, message).
    """
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères."

    if not any(c.isupper() for c in password):
        return False, "Le mot de passe doit contenir au moins une majuscule."

    if not any(c.islower() for c in password):
        return False, "Le mot de passe doit contenir au moins une minuscule."

    if not any(c.isdigit() for c in password):
        return False, "Le mot de passe doit contenir au moins un chiffre."

    return True, "Mot de passe valide."