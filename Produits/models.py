from django.db import models
from decimal import Decimal ,ROUND_HALF_UP
from django.shortcuts import  get_object_or_404
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.timezone import now
from celery import shared_task
from utilisateurs.models import Compte, UtilisateurProfil
import uuid
from django.utils.text import slugify



class Categories(models.Model):
     name =models.CharField(max_length=250)
     compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='categories')
     
     def __str__(self):
              return self. name
#parametre

#### Support
class ContactMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Utilisateur connecté
    compte = models.ForeignKey(Compte, on_delete=models.SET_NULL, null=True, blank=True)  # Compte de l'utilisateur
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    image = models.ImageField(upload_to='contact_images/', blank=True, null=True)  # Image facultative
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sujet} - {self.user.username if self.user else 'Anonyme'}"

    def save(self, *args, **kwargs):
        # Associer le message au compte de l'utilisateur si l'utilisateur est connecté
        if self.user:
            try:
                profil_utilisateur = UtilisateurProfil.objects.get(utilisateur=self.user)
                self.compte = profil_utilisateur.compte
            except UtilisateurProfil.DoesNotExist:
                pass  # Aucun profil trouvé, donc le champ compte reste vide
        super().save(*args, **kwargs)


class parametre(models.Model):
     compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='parametres')
     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parametre')
     name =models.CharField(max_length=200)
     #pays =models.CharField(max_length=100)
     adresse =models.CharField(max_length=60)
     devise =models.CharField(max_length=5)
     email  =models.EmailField()
     numero = models.CharField(max_length=15, verbose_name="Numéro de téléphone")
     fiscal = models.CharField(max_length=100, verbose_name="Régime fiscal")
     logo = models.ImageField(upload_to='images/', null=True, blank=True, )
     remarque = models.TextField(
        max_length=500, 
        blank=True, 
        null=True, 
        default="Les produits vendus ne sont ni échangés ni remboursés. Pour tout soucis, voir le vendeur."
    )
     
     class Meta:
        unique_together = ('compte',)
     def __str__(self):
               return f'{self.name} - {self.compte.nom}'
          


class Invoice(models.Model):
    ventes = models.ForeignKey('Vente', on_delete=models.CASCADE, related_name='factures')
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    date_achat = models.DateTimeField(auto_now_add=True)
    save_by = models.ForeignKey(User, on_delete=models.PROTECT)
    total_amount = models.DecimalField(max_digits=10000, decimal_places=2, default=0)
    last_udapted_date = models.DateTimeField(null=True , blank=True)
    paid = models.BooleanField(default=False)
    
    class Meta:
     
     verbose_name = 'Invoice'
     verbose_name_plural = 'Invoices'

    def __str__(self):
        return f"Facture {self.customer}_{self.date_achat}"
    @property
     
    def get_total(self):
        articles = self.article_set.all()
        total = sum(article.get_total for article in articles)

#classe pour les produits

class Produits(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    slug = models.SlugField(unique=True, blank=True)
 
    
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='produits')
    name = models.CharField(max_length=110)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    price = models.IntegerField()
    quantite = models.PositiveIntegerField(default=0)
    description = models.TextField()
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateField(default=now)
    image = models.ImageField(null=True, blank=True, upload_to='media/')

    class Meta:
        ordering = ['-date_ajout']

    @property
    def total_quantity(self):
        return sum(lot.quantite for lot in self.lots.all())

    def statut_quantite(self):
        if self.total_quantity == 0:
            return 'red'
        elif self.total_quantity <= 10:
            return 'yellow'
        else:
            return 'green'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)                # Génère une version "slugifiée" du nom (ex : "nom-du-produit")
            unique_part = str(uuid.uuid4())[:8]            # Récupère les 8 premiers caractères d'un UUID aléatoire
            self.slug = f"{base_slug}-{unique_part}"       # Concatène le slug du nom et la partie unique
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.name} - {self.compte}"
          
    
         

class StockLot(models.Model):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='stocklot')
    produit = models.ForeignKey('Produits', on_delete=models.CASCADE, related_name='lots')
    quantite = models.PositiveIntegerField()
    date_expiration = models.DateField()
    date_derniere_notification = models.DateField(null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)  # Champ slug modifié

    def __str__(self):
        return f"{self.produit.name} - {self.quantite} unités (Expiration : {self.date_expiration})"

    def supprimer_si_vide(self):
        """Supprime le lot si la quantité est égale à zéro."""
        if self.quantite == 0:
            self.delete()

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.produit.name)                # Génère une version "slugifiée" du nom (ex : "nom-du-produit")
            unique_part = str(uuid.uuid4())[:8]            # Récupère les 8 premiers caractères d'un UUID aléatoire
            self.slug = f"{base_slug}-{unique_part}"       # Concatène le slug du nom et la partie unique
        super().save(*args, **kwargs)

# Signal pour vérifier les lots après une mise à jour
@receiver(post_save, sender=StockLot)
def verifier_lot_apres_mise_a_jour(sender, instance, **kwargs):
    """Supprime automatiquement le lot si la quantité est zéro."""
    if instance.quantite == 0:
        instance.delete()


#model achats

class ProduitsAchat(models.Model):
     #produit = models.ForeignKey(Produits, on_delete=models.CASCADE)
     name =models.CharField(max_length=110)
     #category = models.ForeignKey(Categories, on_delete=models.CASCADE)
     priceA =models.IntegerField()
     quantite=models.PositiveIntegerField(default=0)
     description =models.TextField()
     date_expirationM = models.DateField()
     date_achat =models.DateField()
     fournisseur = models.TextField()
         
     def __str__(self):
        return self. Produit.name
   
    


 
          
class Supplier(models.Model):
     SEX_TYPES = (
          ('M', 'Masculin'),
          ('F', 'Feminin'),
     )
     
     
     name =models.CharField(max_length=100)
     email = models.EmailField()
     numero = models.CharField(max_length=50)
     adress = models.CharField(max_length=60)
     sex = models.CharField(max_length=1, choices=SEX_TYPES)
     
     def __str__(self):
              return self. name
          
class Customer(models.Model):
     SEX_TYPES = (
          ('M', 'Masculin'),
          ('F', 'Feminin'),
     )
     
     compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='customer')
     name =models.CharField(max_length=100)
     email = models.EmailField()
     numero = models.CharField(max_length=50)
     adress = models.CharField(max_length=60)
     sex = models.CharField(max_length=1, choices=SEX_TYPES)
     
     def __str__(self):
              return self. name
class Fournisseur(models.Model):
    SEX_TYPES = (
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    )
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='fournisseur')
    name = models.CharField(max_length=100)  # Champ obligatoire
    email = models.EmailField(blank=True, null=True)  # Email optionnel
    numero = models.CharField(max_length=50, blank=True, null=True)  # Numéro optionnel
    adress = models.CharField(max_length=60, blank=True, null=True)  # Adresse optionnelle
    sex = models.CharField(max_length=1, choices=SEX_TYPES, blank=True, null=True)  # Sexe optionnel

    def __str__(self):
        return self.name

class Date_achat(models.Model):
     name = models.DateField()
    


class ProduitsVente(models.Model):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='produitsvente')
    produit = models.ForeignKey(Produits, on_delete=models.CASCADE)
    vente = models.ForeignKey('Vente', on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=50, decimal_places=2)

    def __str__(self):
        return f"Vente de {self.produit.name} ({self.quantite} articles)"

      
class Vente(models.Model):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='vente')
    produit = models.ForeignKey(Produits, on_delete=models.CASCADE)
    facture = models.ForeignKey('Facture_client', on_delete=models.CASCADE, related_name="ventes")
    sale_date = models.DateTimeField(auto_now_add=True)
    quantite = models.PositiveIntegerField()
    remise = models.IntegerField(default=0, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    montant_total = models.DecimalField(max_digits=50, decimal_places=2, default=0)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Ajout de unique=True pour le champ UUID

    def save(self, *args, **kwargs):
        if not self.produit or not self.quantite:
            raise ValueError("Produit et quantité sont requis pour enregistrer une vente.")
        
        remise_decimal = Decimal(self.remise or 0)
        prix_unitaire = Decimal(self.produit.price)
        self.montant_total = prix_unitaire * Decimal(self.quantite) * (Decimal(1) - remise_decimal / Decimal(100))

        super(Vente, self).save(*args, **kwargs)

    def __str__(self):
        return f"Vente de {self.produit.name} à {str(self.customer)}"


class Facture_client(models.Model):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='fac')
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='factures')
    date_creation = models.DateTimeField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remise_globale = models.FloatField(default=0)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Ajout de unique=True pour le champ UUID

    def __str__(self):
        return f"Facture {self.id} - {self.customer.name}"

    def calculer_montant_total(self):
        total = Decimal(0)
        for vente in self.ventes.all():
            total += vente.montant_total
        
        total *= (Decimal(1) - Decimal(self.remise_globale) / Decimal(100))
        return total

    def save(self, *args, **kwargs):
        if self.pk:
            self.montant_total = self.calculer_montant_total()
        super(Facture_client, self).save(*args, **kwargs)





  
 

class FactureAchat(models.Model):
    
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='facachat')
    fournisseur= models.ForeignKey(Fournisseur, on_delete=models.CASCADE, related_name='fournisseur')
    date_creation = models.DateTimeField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remise_globale = models.FloatField(default=0)  # Remise globale en pourcentage
    date_expiration = models.DateField(null=True, blank=True)

    def calculer_montant_total(self):
        # Import local si nécessaire

        achats = self.achats.all()
        total_achats = sum(
            achat.montant_total() for achat in achats  # Utilise le montant total de l'achat
        )

        # Convertir la remise globale en Decimal
        remise_globale_decimal = Decimal(self.remise_globale) / 100
        total_apres_remise = total_achats * (1 - remise_globale_decimal)

        return total_apres_remise

    def save(self, *args, **kwargs):
        """
        Sauvegarde l'objet après calcul du montant total.
        """
        # Si l'objet n'a pas encore d'ID, sauvegardez d'abord pour permettre l'accès à `self.achats.all()`
        if not self.pk:
            super().save(*args, **kwargs)

        # Calculer et mettre à jour le montant total
        self.montant_total = self.calculer_montant_total()

        # Sauvegarder avec le montant mis à jour
        super().save(*args, **kwargs)



class Achat(models.Model):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='achat')
    produit = models.ForeignKey(Produits, on_delete=models.CASCADE, related_name="achats")
    facture = models.ForeignKey(FactureAchat, on_delete=models.CASCADE, related_name='achats')
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)  # Assurez-vous de ce champ
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # En pourcentage
    date_achat = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateField(null=True, blank=True)

    def montant_total(self):
       

        remise_decimal = Decimal(self.remise) / 100
        prix_total = Decimal(self.quantite) * self.prix_unitaire * (1 - remise_decimal)
        return prix_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def __str__(self):
        return f"{self.produit.name} - {self.quantite}"

      
# class Article(models.Model):
#      #invoice =  models.ForeignKey(Invoice, on_delete=models.CASCADE)
#      name = models.CharField(max_length=32)
#      quantite = models.IntegerField()
#      price = models.DecimalField(max_digits=10000, decimal_places=2)
#      total = models.DecimalField(max_digits=10000, decimal_places=2)
     
#      class Meta:
          
#           verbose_name = 'Article'
#           verbose_name_plural = 'Articles'
          
#      @property
#      def get_total(self):
#           total = self.quantite * self.price


class LigneFacture(models.Model):
    facture = models.ForeignKey(Facture_client, related_name="lignes", on_delete=models.CASCADE)
    produit = models.ForeignKey('Produits', on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    remise = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Remise en pourcentage
    sous_total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Calcul de la remise en pourcentage et du sous-total
        remise_montant = (self.prix_unitaire * self.quantite) * (self.remise / 100 if self.remise else 0)
        self.sous_total = (self.prix_unitaire * self.quantite) - remise_montant
        super().save(*args, **kwargs)
        # Mettre à jour le total de la facture associée
        self.facture.update_total()

    def __str__(self):
        return f"Ligne facture pour {self.produit.nom}"

# LES MODEL POUR LE RAPPORT ET STASTIQUES
class HistoriquePrix(models.Model):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produits, on_delete=models.CASCADE)
    ancien_prix = models.DecimalField(max_digits=10, decimal_places=2)
    nouveau_prix = models.DecimalField(max_digits=10, decimal_places=2)
    date_modification = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prix modifié pour {self.produit.name} - {self.date_modification}"


class StockMinimum(models.Model):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produits, on_delete=models.CASCADE)
    quantite_minimum = models.PositiveIntegerField()
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Stock minimum pour {self.produit.name} : {self.quantite_minimum} unités"
    
    
# MODEL DE NOTIFICATION


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Notification(models.Model):
    TYPE_CHOICES = (
        ('expirant', 'Expiration imminente'),
        ('stock_minimum', 'Stock minimum atteint'),
        ('remise', 'Remise appliquée'),
        ('motivation', 'motivation'),
        ('proche_expiration', 'perime'),
        ('autre', 'Autre'),
    )
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    is_lu = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification - {self.type}"

    def marquer_comme_lu(self):
        self.is_lu = True
        self.save()

      

# Signal pour ajouter une notification d'expiration de produit


from datetime import datetime, timedelta
from django.utils.timezone import now

@receiver(post_save, sender=StockLot)
def verifier_expiration_lot(sender, instance, **kwargs):
    """Ajoute une notification si un produit en stock va expirer dans moins de 2 mois."""
    try:
        expiration_date = instance.date_expiration
        if expiration_date <= now().date() + timedelta(days=60):
            if instance.date_derniere_notification != now().date():
                # Envoyer une notification et mettre à jour la date
                Notification.objects.create(
                    type='expirant',
                    message=f"Le produit {instance.produit.name} expirera bientôt (expiration le {expiration_date})."
                )
                instance.date_derniere_notification = now().date()
                instance.save()
    except Exception as e:
        print(f"Erreur lors de la vérification de l'expiration : {e}")


@receiver(post_save, sender=StockLot)
def verifier_stock_minimum(sender, instance, **kwargs):
    """Ajoute une notification si le stock d'un produit est inférieur au minimum requis."""
    try:
        produit = instance.produit
        stock_total = instance.total_quantity
        if stock_total <= 10:  # Seuil minimum
            if instance.date_derniere_notification != now().date():
                # Envoyer une notification et mettre à jour la date
                Notification.objects.create(
                    type='stock_minimum',
                    message=f"Le stock du produit {produit.name} est inférieur ou égal au minimum requis (actuel : {stock_total})."
                )
                instance.date_derniere_notification = now().date()
                instance.save()
    except Exception as e:
        print(f"Erreur lors de la vérification du stock minimum : {e}")
        
        
@shared_task
def verifier_notifications_periodiques():
    """Tâche asynchrone qui vérifie les produits pour les notifications."""
    lots = StockLot.objects.all()
    for lot in lots:
        # Vérifier l'expiration
        expiration_date = lot.date_expiration
        if expiration_date <= now().date() + timedelta(days=60) and lot.date_derniere_notification != now().date():
            Notification.objects.create(
                type='expirant',
                message=f"Le produit {lot.produit.name} expirera bientôt (expiration le {expiration_date})."
            )
            lot.date_derniere_notification = now().date()
            lot.save()

        # Vérifier le stock minimum
        if lot.total_quantity <= 10 and lot.date_derniere_notification != now().date():
            Notification.objects.create(
                type='stock_minimum',
                message=f"Le stock du produit {lot.produit.name} est inférieur ou égal au minimum requis (actuel : {lot.total_quantity})."
            )
            lot.date_derniere_notification = now().date()
            lot.save()

# BON DE COMMANDE ET DEVIS
class ProduitCommande(models.Model):
    produit = models.ForeignKey('Produits', on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.produit.name} x {self.quantite}"



class BonDeCommande(models.Model):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='boncommande')
    commandefac = models.ForeignKey('commandefact', on_delete=models.CASCADE, related_name="commandes")
    produit = models.ForeignKey(Produits, on_delete=models.CASCADE)
    date_commande = models.DateTimeField(default=datetime.now)
    quantite = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Convertir prix_unitaire en Decimal pour éviter les erreurs
        prix_unitaire_decimal = Decimal(self.prix_unitaire)
        
        # Calculer le total pour chaque ligne de commande
        self.total = Decimal(self.quantite) * prix_unitaire_decimal
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.produit.name} - {self.quantite}"

    def montant_total(self):
        # Calculer le montant total de cette ligne de commande
        return self.total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class commandefact(models.Model):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='commandefac')
    fournisseur = models.ForeignKey('Fournisseur', on_delete=models.CASCADE, related_name='fournisseurs')
    date_creation = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculer_montant_total(self):
        # Calculer le total des commandes associées
        commandes = self.commandes.all()
        total_commandes = sum(commande.total for commande in commandes)
        return total_commandes

    def save(self, *args, **kwargs):
        # Sauvegarder avant pour obtenir une clé primaire
        if not self.pk:
            super().save(*args, **kwargs)
        
        # Recalculer le total de la commande
        self.total = self.calculer_montant_total()
        super().save(*args, **kwargs)



    # def save(self, *args, **kwargs):
    #     if self.pk:  # Vérifie si la facture existe déjà
    #         self.total = self.calculer_montant_total()
    #     super(commandefact, self).save(*args, **kwargs)  

class Devis(models.Model):
    date_creation = models.DateTimeField(auto_now_add=True)  # Date de création
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='devis')
    client = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Client associé
    quantite = models.PositiveIntegerField()  # Quantité demandée
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)  # Prix unitaire du produit
    remise_specifique = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Remise spécifique au produit
    produit = models.ForeignKey('Produits', on_delete=models.CASCADE)  # Produit associé
    devisfac = models.ForeignKey('DevisFact', on_delete=models.CASCADE, related_name='deviss')
    date_expiration = models.DateField(null=True, blank=True)  # Date d'expiration
    
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Total avec remise spécifique
    
    createur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='createur_devis')
    modificateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='modificateur_devis', blank=True)

    def save(self, *args, **kwargs):
     self.quantite = self.quantite or 0
     self.prix_unitaire = Decimal(self.produit.price)  # Assurez-vous que produit.price est valide
     self.remise_specifique = self.remise_specifique or Decimal(0)
     self.total = Decimal(self.quantite) * self.prix_unitaire * (1 - self.remise_specifique / 100)
     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.produit.name} - {self.quantite}"

    def montant_total(self):
        # Calculer le montant total de cette ligne de commande
        return self.total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

   
class DevisFact(models.Model):
    STATUT_CHOICES = (
        ('en_cours', 'En cours'),
        ('valide', 'Validé'),
        ('refuse', 'Refusé'),
    )
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='devisfac')
    remise_globale = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Remise globale sur le devis
    remarque = models.TextField(null=True, blank=True)  # Remarque optionnelle
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='en_cours')  # Statut du devis
 
    client = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='devisfacs')
    date_creation = models.DateTimeField(auto_now_add=True)  # Date de création
    
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Total avec remise spécifique
    date_expiration = models.DateField(null=True, blank=True)  # Date d'expiration de chaque produit
    
    
    def calculer_montant_total(self):
        deviss = self.deviss.all()
        total_deviss = sum(devis.total for devis in deviss)
        return total_deviss

    def save(self, *args, **kwargs):
        if self.pk:  # Si la facture existe déjà
            self.total = self.calculer_montant_total() * (1 - self.remise_globale / 100)
        super().save(*args, **kwargs)


    

   

