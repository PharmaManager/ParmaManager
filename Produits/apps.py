from django.apps import AppConfig


class ProduitsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Produits'


#####################
# Dans apps.py ou un fichier utils
from django.db.models.signals import class_prepared
from django.dispatch import receiver
from utils.managers import GlobalCompteManager

@receiver(class_prepared)
def appliquer_filtrage_global(sender, **kwargs):
    """
    Applique automatiquement le manager GlobalCompteManager à tous les modèles.
    """
    if hasattr(sender, 'compte'):  # Appliquer uniquement aux modèles ayant un champ compte
        sender.add_to_class('objects', GlobalCompteManager())
