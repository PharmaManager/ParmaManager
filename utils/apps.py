# utils/apps.py
from django.apps import AppConfig

class UtilsConfig(AppConfig):
    name = 'utils'

    def ready(self):
        import utils.signals  # Charge les signaux
