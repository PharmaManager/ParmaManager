## moi meme
# Crée un fichier `managers.py` dans ton projet principal ou utils
from django.db import models

class GlobalCompteManager(models.Manager):
    def get_queryset(self):
        """
        Filtre automatiquement les données selon le compte injecté par le middleware.
        """
        request = self._get_request()
        qs = super().get_queryset()

        if request and hasattr(request, 'compte') and request.compte:
            return qs.filter(compte=request.compte)  # Filtrer selon le compte
        return qs.none()  # Aucune donnée si pas de compte trouvé

    def _get_request(self):
        """
        Récupère la requête globale.
        """
        from django.utils.deprecation import MiddlewareMixin
        return MiddlewareMixin.thread_local.get('request', None)
