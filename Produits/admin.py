from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Categories)
admin.site.register(Vente)
admin.site.register(Produits)
admin.site.register(Facture_client)
admin.site.register(Customer)
admin.site.register(Fournisseur)
admin.site.register(StockLot)
admin.site.register(Notification)
admin.site.register(StockMinimum)
admin.site.register(Achat)
admin.site.register(FactureAchat)
admin.site.register(BonDeCommande)
admin.site.register(Devis)
admin.site.register(DevisFact)
admin.site.register(Compte)
admin.site.register(UtilisateurProfil)

