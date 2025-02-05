from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

class Compte(models.Model):
    ETAT_CHOICES = [
        ('admin', 'Admin'),
        ('utilisateur', 'Utilisateur'),
    ]

    nom = models.CharField(max_length=100, unique=True)
    administrateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='compte')
    date_creation = models.DateTimeField(auto_now_add=True)
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='utilisateur')  # Etat du compte
    taille = models.CharField(max_length=20, blank=True, null=True)  # Taille du compte en fonction des utilisateurs
     
    abonnement_active = models.BooleanField(default=True)  
    paypal_subscription_id = models.CharField(max_length=100, blank=True, null=True)  
    dernier_paiement = models.DateTimeField(null=True, blank=True)  

    def __str__(self):
        return self.nom
    def date_fin_abonnement(self):
        """Retourne la date d'expiration de l'abonnement."""
        if self.nom == "Ahoeke":  
            return timezone.now() + timedelta(days=3650)  # Simule un abonnement illimité

        if self.dernier_paiement:
            return self.dernier_paiement + timedelta(days=30)
        return self.date_creation + timedelta(days=2)

    def jours_restants(self):
        """Retourne le nombre de jours restants avant expiration de l'abonnement."""
        if self.nom == "Ahoeke":
            return 9999  # Compte toujours actif

        delta = self.date_fin_abonnement() - timezone.now()
        return max(delta.days, 0)

    def abonnement_est_expire(self):
        """Vérifie si l'abonnement est expiré (hors période de grâce)."""
        if self.nom == "Ahoeke":
            return False  # Toujours actif

        return timezone.now() > self.date_fin_abonnement() + timedelta(days=7)

    def est_en_periode_grace(self):
        """Vérifie si l'utilisateur est dans la période de grâce (7 jours après expiration)."""
        if self.nom == "Ahoeke":
            return False  # Pas de période de grâce pour ce compte

        return self.date_fin_abonnement() < timezone.now() <= self.date_fin_abonnement() + timedelta(days=2)

    def verifier_abonnement(self):
        """Met à jour l'état de l'abonnement (actif ou non)."""
        if self.nom == "Ahoeke":
            self.abonnement_active = True  # Toujours actif
        else:
            self.abonnement_active = not self.abonnement_est_expire()
        self.save()
    def set_taille_compte(self):
        """Détermine la taille du compte en fonction du nombre d'utilisateurs."""
        # Vérification du nombre d'utilisateurs dans le compte
        nb_utilisateurs = self.utilisateurs.count()  # Utilisation de la relation inversée
        print(f"Debug: Nombre d'utilisateurs dans le compte '{self.nom}': {nb_utilisateurs}")  # Ajout d'un debug
        if nb_utilisateurs > 10:
            self.taille = "Grande"
        elif nb_utilisateurs > 5:
            self.taille = "Moyenne"
        else:
            self.taille = "Petite"
        self.save()

    def save(self, *args, **kwargs):
        """Override pour mettre à jour la taille du compte avant l'enregistrement et prévenir les doublons."""
        # Vérifier qu'un administrateur n'est pas déjà associé à un autre compte
        if self.pk is None:  # Si c'est un nouvel enregistrement
            if Compte.objects.filter(administrateur=self.administrateur).exists():
                raise ValueError(f"L'utilisateur {self.administrateur.username} est déjà un administrateur d'un autre compte.")
        
        # Sauvegarde standard
        super().save(*args, **kwargs)

        # Si la taille n'a pas été définie, l'ajuster
        if not self.taille:
            self.set_taille_compte()




    
from django.db import models
from django.contrib.auth.models import User

class UtilisateurProfil(models.Model):
    ROLE_CHOICES = [
        ('pharmacien', 'Pharmacien'),
        ('caissier', 'Caissier'),
        ('gestionnaire', 'Gestionnaire'),
        ('autre', 'Autre'),
    ]

    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='utilisateurs')
    est_admin = models.BooleanField(default=False)
    photo_profil = models.ImageField(upload_to='images/', null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='autre')  # Rôle de l'utilisateur
    etat_utilisateur = models.CharField(max_length=20, choices=[('admin', 'Admin'), ('utilisateur', 'Utilisateur')], default='utilisateur')  # Admin ou Utilisateur simple

    def __str__(self):
        return self.utilisateur.username

    @property
    def is_compte_admin(self):
        """Vérifie si l'utilisateur est administrateur du compte."""
        return self.est_admin

    @property
    def is_pharmacien(self):
        """Vérifie si l'utilisateur a le rôle pharmacien."""
        return self.role == 'pharmacien'

    @property
    def is_caissier(self):
        """Vérifie si l'utilisateur a le rôle caissier."""
        return self.role == 'caissier'

    @property
    def is_gestionnaire(self):
        """Vérifie si l'utilisateur a le rôle gestionnaire."""
        return self.role == 'gestionnaire'

    @property
    def is_utilisateur(self):
        """Vérifie si l'utilisateur est un utilisateur simple."""
        return self.etat_utilisateur == 'utilisateur'

    def get_permissions(self):
        """Retourne les permissions en fonction du rôle."""
        if self.is_compte_admin:
            return ['can_add', 'can_edit', 'can_delete', 'can_view']
        elif self.is_pharmacien:
            return ['can_view', 'can_edit']
        elif self.is_caissier:
            return ['can_view']
        else:
            return []

    def save(self, *args, **kwargs):
        """Override pour associer un utilisateur à son profil."""
        # Empêcher la mise à jour du compte à chaque enregistrement du profil
        save_compte = self.compte
        if save_compte:
            # Assurez-vous que set_taille_compte ne soit appelé qu'une seule fois
            # après le premier enregistrement ou mise à jour du profil
            taille_avant_save = save_compte.taille

        super().save(*args, **kwargs)

        # Si la taille a changé, mettez à jour la taille du compte
        if save_compte and save_compte.taille != taille_avant_save:
            save_compte.set_taille_compte()  # Calculer et mettre à jour la taille du compte



