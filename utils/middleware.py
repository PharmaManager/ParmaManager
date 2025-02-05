import threading
from django.utils.deprecation import MiddlewareMixin

from django.utils.timezone import now
from datetime import timedelta

# Crée un fichier `middleware.py` dans un dossier utils ou app principale
class GlobalCompteFilterMiddleware:
    """
    Middleware pour filtrer les données selon le compte de l'utilisateur connecté.
    Ne nécessite aucune modification des vues, modèles ou URLs.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Injecte le compte dans la requête
        if request.user.is_authenticated:
            # Vérifier si l'utilisateur a un profil avant d'y accéder
            profil = getattr(request.user, 'profil', None)
            request.compte = getattr(profil, 'compte', None) if profil else None
        else:
            request.compte = None

        return self.get_response(request)




# Dans utils/middleware.py
from django.utils.deprecation import MiddlewareMixin

class RequestStorageMiddleware(MiddlewareMixin):
    """
    Stocke globalement la requête en cours pour pouvoir y accéder dans les gestionnaires.
    """

    thread_local = threading.local()

    def process_request(self, request):
        self.thread_local.request = request

    def process_response(self, request, response):
        self.thread_local.request = None
        return response

############# deconnexion


class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')

            if last_activity:
                last_activity_time = now() - timedelta(hours=8)  # 12 heures
                if last_activity_time.timestamp() > last_activity:
                    request.session.flush()  # Supprime la session
                    request.session.clear_expired()

            request.session['last_activity'] = now().timestamp()

        response = self.get_response(request)
        return response


