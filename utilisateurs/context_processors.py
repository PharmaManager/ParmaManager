from .models import UtilisateurProfil

def is_compte_admin(request):
    if request.user.is_authenticated:
        try:
            profil = request.user.profil  # Lier UtilisateurProfil au modèle User
            return {'is_admin': profil.is_compte_admin}
        except UtilisateurProfil.DoesNotExist:
            return {'is_admin': False}
    return {'is_admin': False}
