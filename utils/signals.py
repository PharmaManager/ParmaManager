# utils/signals.py
from django.db.models.signals import class_prepared
from django.dispatch import receiver
from utils.managers import GlobalCompteManager

@receiver(class_prepared)
def appliquer_filtrage_global(sender, **kwargs):
    """
    Applique le gestionnaire GlobalCompteManager aux modèles ayant un champ `compte`.
    Cela permet de filtrer automatiquement les objets liés à l'utilisateur connecté.
    """
    if hasattr(sender, 'compte'):  # Appliquer uniquement aux modèles ayant un champ `compte`
        sender.add_to_class('objects', GlobalCompteManager())
