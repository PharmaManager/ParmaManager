from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth import login,authenticate, logout
from django.contrib import messages
import json
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError

# Create your views here.
# fonction pour creer une compte
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Compte  # Importez le modèle Compte
import re
from django.shortcuts import get_object_or_404
from Produits.models import parametre  
import os
from .forms import PhotoProfilForm

def creation_compte(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']

        # Vérification des mots de passe
        if password != password_confirm:
            messages.error(request, "Les mots de passe ne sont pas identiques, veuillez réessayer.")
            return redirect("creation")

        # Vérification de la longueur et des caractères
        if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password) or not re.search(r'[!@#$%(),.?":{}|<>]', password):
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères, y compris des lettres, des chiffres et des caractères spéciaux.")
            return redirect("creation")

        # Vérification du format de l'adresse email
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "L'adresse email est invalide. Veuillez réessayer.")
            return redirect("creation")

        # Vérification de l'existence de l'email et du nom d'utilisateur
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà. Veuillez réessayer.")
            return redirect("creation")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cette adresse email existe déjà. Veuillez utiliser une autre adresse email.")
            return redirect("creation")

        try:
            # Démarrer une transaction atomique
            with transaction.atomic():
                # Création de l'utilisateur principal
                utilisateur_principal = User.objects.create_user(username=username, email=email, password=password)

                # Vérification si un compte existe déjà pour cet utilisateur
                if Compte.objects.filter(administrateur=utilisateur_principal).exists():
                    messages.error(request, "Un compte existe déjà pour cet utilisateur.")
                    return redirect("creation")

                # Création du compte associé
                compte = Compte.objects.create(nom=username, administrateur=utilisateur_principal)

                # Création du profil utilisateur associé
                UtilisateurProfil.objects.create(
                    utilisateur=utilisateur_principal,
                    compte=compte,
                    est_admin=True  # Par défaut, le créateur du compte est admin
                )

                # Définir le chemin du logo par défaut (dans le répertoire 'static')
                logo_path = os.path.join(settings.STATIC_URL, 'images/12.jpeg')  # Assurez-vous que ce chemin est correct

                # Création des paramètres par défaut pour le compte
                parametre.objects.create(
                    compte=compte,
                    user=utilisateur_principal,
                    name=f"Paramètre de {username}",
                    adresse="Adresse par défaut",
                    devise="FCFA",
                    email=email,
                    numero="0000000000",
                    fiscal="Non spécifié",
                    logo=f'images/12.jpeg',
                )
                
                
                        # Générer l'URL de la page de connexion
            login_url = request.build_absolute_uri(reverse('login'))

            # Envoi de l'email de bienvenue
            subject = "Bienvenue sur SuperPharma - Optimisez la gestion de votre pharmacie !"
            message = f"""
            Bonjour {username},

            Félicitations et bienvenue dans l'univers de SuperPharma !

            Nous sommes heureux de vous annoncer que votre compte a été créé avec succès. 🎉

            SuperPharma est l'outil idéal pour gérer efficacement votre pharmacie. Grâce à nos fonctionnalités avancées, vous pourrez :
            ✅ Gérer vos stocks en temps réel
            ✅ Émettre des devis et factures personnalisés
            ✅ Garder un œil sur l'expiration de vos produits
            ✅ Et bien plus encore !

            Notre équipe est à votre disposition pour vous accompagner à chaque étape de votre parcours. Nous vous invitons à vous connecter dès maintenant et à découvrir tout ce que SuperPharma a à offrir.

            Pour vous connecter, cliquez ici : {login_url}

            Nous vous remercions de votre confiance et nous avons hâte de vous voir tirer parti de toutes les fonctionnalités de SuperPharma pour une gestion optimale de votre pharmacie.

            À bientôt et bonne gestion !

            Cordialement,
            L'équipe SuperPharma
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,  # Utilise l'email par défaut défini dans settings.py
                [email],  # L'email du destinataire
                fail_silently=False,
            )

            # Si tout a fonctionné, on envoie un message de succès
            messages.success(request, "Félicitations ! Votre compte principal a été créé avec succès. Veuillez vous connecter.")
            return redirect('login')

        except Exception as e:
            # En cas d'exception, la transaction sera annulée et rien ne sera enregistré
            messages.error(request, f"Une erreur est survenue. Détails de l'erreur: {str(e)}")
            return redirect("creation")

    return render(request, "creation.html")
# compte pour les utilisateur d'un compte principal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import UtilisateurProfil

import re


@login_required
def creation_utilisateur_secondaire(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # Vérification des mots de passe
        if password != password_confirm:
            messages.error(request, "Les mots de passe ne sont pas identiques. Veuillez réessayer.")
            return redirect("creation_utilisateur_secondaire")

        # Vérification de la longueur et des caractères du mot de passe
        if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password) or not re.search(r'[!@#$%(),.?":{}|<>]', password):
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères, incluant des lettres, des chiffres et des caractères spéciaux.")
            return redirect("creation_utilisateur_secondaire")

        # Vérification du format de l'adresse email
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "L'adresse email est invalide. Veuillez réessayer.")
            return redirect("creation_utilisateur_secondaire")

        # Vérification de l'existence de l'email et du nom d'utilisateur
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà. Veuillez réessayer avec un autre.")
            return redirect("creation_utilisateur_secondaire")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cette adresse email est déjà utilisée. Veuillez réessayer avec une autre.")
            return redirect("creation_utilisateur_secondaire")

        # Vérification que l'utilisateur connecté a un compte
        try:
            compte = request.user.profil.compte  # Récupère le compte via le profil de l'utilisateur connecté
            compte_nom = compte.nom  # Récupère le nom du compte
        except AttributeError:
            messages.error(request, "Aucun compte administrateur associé à cet utilisateur. Veuillez contacter l'administrateur principal.")
            return redirect("creation_utilisateur_secondaire")

        # Création de l'utilisateur secondaire
        utilisateur_secondaire = User.objects.create_user(username=username, email=email, password=password)

        # Association de l'utilisateur secondaire au compte existant
        UtilisateurProfil.objects.create(utilisateur=utilisateur_secondaire, compte=compte, est_admin=False)
        
        
                # Générer l'URL de la page de connexion
        login_url = request.build_absolute_uri(reverse('login'))

        # Envoi de l'email de bienvenue
        subject = "Bienvenue sur SuperPharma - Votre accès en tant qu'utilisateur secondaire"
        message = f"""
        Bonjour {username},

        Nous sommes ravis de vous informer que vous êtes désormais un utilisateur secondaire du compte SuperPharma associé au compte '{compte_nom}'.

        En tant qu'utilisateur secondaire, vous avez désormais accès à toutes les fonctionnalités essentielles de SuperPharma pour vous aider dans la gestion de la pharmacie. Vous pourrez :
        ✅ Accéder à l'inventaire des produits
        ✅ Créer des devis et des factures
        ✅ Consulter l'historique des transactions

        Vous avez été ajouté à un compte existant, ce qui vous permet de profiter d'une gestion collaborative tout en maintenant la sécurité et l'efficacité.

        Pour vous connecter à votre compte, veuillez cliquer sur le lien suivant : {login_url}

        Nous vous remercions de faire partie de SuperPharma et de contribuer à la gestion optimale de votre pharmacie.

        Si vous avez des questions ou des besoins spécifiques, n'hésitez pas à contacter l'administrateur principal.

        Cordialement,
        L'équipe SuperPharma
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # Utilise l'email par défaut défini dans settings.py
            [email],  # L'email du destinataire
            fail_silently=False,
        )

        messages.success(request, "L'utilisateur secondaire a été créé et lié à votre compte avec succès. Un email de bienvenue a été envoyé.")
        return redirect("liste_utilisateurs")

    # Si ce n'est pas une requête POST, afficher le formulaire
    return render(request, "creation.html")

#les utilisateurs
@login_required
def liste_utilisateurs(request):
    # Récupération du compte de l'administrateur connecté via son profil
    compte = request.user.profil.compte
    
    # Filtrage des utilisateurs qui appartiennent au même compte
    utilisateurs = User.objects.filter(profil__compte=compte)
    
    return render(request, "liste_utilisateurs.html", {"utilisateurs": utilisateurs})

@login_required
def supprimer_utilisateur(request, utilisateur_id):
    utilisateur = get_object_or_404(User, id=utilisateur_id)
    
    # Vérifier si l'utilisateur appartient au même compte que l'admin connecté
    if utilisateur.profil.compte != request.user.profil.compte:
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer cet utilisateur.")
        return redirect('liste_utilisateurs')
    
    # Vérifier si l'utilisateur connecté est un administrateur
    if utilisateur.profil.est_admin :
        messages.error(request, "Impossible de supprimer un administrateur.")
        return redirect('liste_utilisateurs')
    
    if request.method == "POST":
        
        nom_utilisateur = utilisateur.username
        email_utilisateur = utilisateur.email
        
        utilisateur.delete()
        
                # Envoyer un email à l'utilisateur supprimé
        subject = "Votre compte SuperPharma a été supprimé"
        message = f"""
        Bonjour {nom_utilisateur},

        Nous vous informons que votre compte SuperPharma a été supprimé par un administrateur.

        Si vous avez des questions concernant cette suppression ou si vous souhaitez en discuter, nous vous encourageons à contacter l'administrateur de votre compte SuperPharma.

        Nous vous remercions de votre compréhension.

        Cordialement,
        L'équipe SuperPharma
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # Utilise l'email par défaut défini dans settings.py
            [email_utilisateur],  # L'email de l'utilisateur supprimé
            fail_silently=False,
        )

        
        messages.success(request, "L'utilisateur a été supprimé avec succès. Un email de notification a été envoyé.")
        return redirect('liste_utilisateurs')
    
    return render(request, "supprimer_utilisateur.html", {"utilisateur": utilisateur})

@login_required
def modifier_utilisateur(request, utilisateur_id):
    utilisateur = get_object_or_404(User, id=utilisateur_id)
    
    # Vérifier si l'utilisateur appartient au même compte que l'admin connecté
    if utilisateur.profil.compte != request.user.profil.compte:
        messages.error(request, "Vous n'avez pas l'autorisation de modifier cet utilisateur.")
        return redirect('liste_utilisateurs')
    
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        
        # Vérification des champs
        if password or password_confirm:  # Si l'utilisateur souhaite modifier le mot de passe
            if password != password_confirm:
                messages.error(request, "Les mots de passe ne correspondent pas.")
                return redirect('modifier_utilisateur', utilisateur_id=utilisateur.id)
            if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password) or not re.search(r'[!@#$%(),.?":{}|<>]', password):
                messages.error(request, "Le mot de passe doit contenir au moins 8 caractères, y compris des lettres, des chiffres et des caractères spéciaux.")
                return redirect('modifier_utilisateur', utilisateur_id=utilisateur.id)
        
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Adresse email invalide. Veuillez réessayer.")
            return redirect('modifier_utilisateur', utilisateur_id=utilisateur.id)
        
        # Vérifier si un autre utilisateur a le même email ou nom d'utilisateur
        if User.objects.filter(username=username).exclude(id=utilisateur.id).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà utilisé.")
            return redirect('modifier_utilisateur', utilisateur_id=utilisateur.id)
        if User.objects.filter(email=email).exclude(id=utilisateur.id).exists():
            messages.error(request, "Cette adresse email est déjà utilisée.")
            return redirect('modifier_utilisateur', utilisateur_id=utilisateur.id)
        
         # Sauvegarder les informations avant la modification
        ancien_username = utilisateur.username
        ancien_email = utilisateur.email
        ancien_password_set = utilisateur.password  # Pour vérifier si le mot de passe a changé
        
        
        # Mettre à jour l'utilisateur
        utilisateur.username = username
        utilisateur.email = email
        if password:
            utilisateur.set_password(password)
        utilisateur.save()
        
                # Envoi de l'email avec les nouvelles informations ou les informations actuelles
        subject = "Modification de votre compte SuperPharma"
        if ancien_username != utilisateur.username or ancien_password_set != utilisateur.password:
            message = f"""
            Bonjour {utilisateur.username},

            Nous vous informons que votre compte SuperPharma a été modifié avec succès. Voici vos informations actualisées :

            - Nom d'utilisateur : {utilisateur.username}
            - Email : {utilisateur.email}
            - Mot de passe : Votre mot de passe a été modifié. Si vous ne l'avez pas fait vous-même, veuillez contacter l'administrateur immédiatement.

            Si vous avez des questions, n'hésitez pas à contacter votre administrateur de compte.

            Cordialement,
            L'équipe SuperPharma
            """
        else:
            message = f"""
            Bonjour {utilisateur.username},

            Nous vous informons que vos informations de compte SuperPharma ont été vérifiées et restent inchangées. Voici vos informations actuelles :

            - Nom d'utilisateur : {utilisateur.username}
            - Email : {utilisateur.email}
            - Mot de passe : Votre mot de passe reste inchangé.

            Si vous avez des questions, n'hésitez pas à contacter votre administrateur de compte.

            Cordialement,
            L'équipe SuperPharma
            """
        
        # Envoi de l'email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [utilisateur.email],
            fail_silently=False,
        )


        
        
        messages.success(request, "L'utilisateur a été modifié avec succès. Un email a été envoyé avec les détails.")
        return redirect('liste_utilisateurs')
    
    return render(request, "modifier_utilisateur.html", {"utilisateur": utilisateur})


        


#fonction pour se connecter

from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.urls import reverse

def connecter_compte(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authentifier l'utilisateur
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Vérifier si l'utilisateur a un compte associé
            if hasattr(user, 'profil') and hasattr(user.profil, 'compte'):
                compte = user.profil.compte  # Récupérer le compte associé à l'utilisateur
                
                # Exclure le compte "Ahoeke" (l'administrateur principal) de la vérification
                if compte.nom != "Ahoeke":  # Vérifier si ce n'est pas le compte "Ahoeke"
                    compte.verifier_abonnement()  # Vérifier l'abonnement

                    # Vérification de l'expiration de l'abonnement
                    if compte.abonnement_est_expire():
                        messages.error(request, "Votre abonnement a expiré. Veuillez renouveler votre paiement.")
                        return redirect("paypal_checkout")
                    
                    # Vérification de la fin de la période d'essai
                    if compte.date_fin_abonnement() < timezone.now():
                        messages.error(request, "Votre période d'essai est terminée. Veuillez procéder au paiement pour continuer.")
                        return redirect("paypal_checkout")

                    # Avertir si l'abonnement expire dans moins de 7 jours
                    jours_restants = compte.jours_restants()
                    if jours_restants <= 7:
                        messages.warning(request, f"Attention ! Votre abonnement expire dans {jours_restants} jours.")

            # Connexion de l'utilisateur si tout est valide
            login(request, user)
            
            # Générer l'URL de modification du mot de passe
            password_change_url = request.build_absolute_uri(reverse('modifierCode', kwargs={'uid': user.id}))
            
            # Envoyer un e-mail de notification avec le lien de modification du mot de passe
            send_mail(
                subject="Connexion à votre compte SuperPharma",
                message=f"""Bonjour {user.username},\n\n
Vous venez de vous connecter à votre compte SuperPharma. Si ce n'est pas vous, veuillez changer votre mot de passe immédiatement en cliquant sur le lien ci-dessous :\n
{password_change_url}\n\n

Cordialement,\n
L'équipe SuperPharma
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            # Redirection vers la page d'accueil
            return redirect(f'/acc/')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
            return redirect("login")
    
    return render(request, 'login.html')






# fonction pour  la verification d'email

from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from django.utils.encoding import force_bytes, force_str  # Importez ici
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.utils.crypto import get_random_string
from datetime import  datetime, timedelta


import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

def verification_Mail(request):
    if request.method == "POST":
        email = request.POST.get('email')

        # Vérifier si l'email est valide
        if not email:
            messages.error(request, "Veuillez entrer une adresse email valide.")
            return redirect("verification")

        # Vérifier si un utilisateur est associé à cet email
        user = User.objects.filter(email=email).first()
        if not user:
            messages.error(request, "Aucun utilisateur trouvé avec cette adresse email.")
            return redirect("verification")

        # Générer un code aléatoire de 6 chiffres
        verification_code = random.randint(100000, 999999)

        # Définir l'heure d'expiration (30 minutes)
        expiration_time = timezone.now() + timedelta(minutes=30)

        # Sauvegarder les infos en session
        request.session["verification_code"] = str(verification_code)
        request.session["expiration_time"] = expiration_time.isoformat()
        request.session["user_id"] = user.id

        # Envoyer le code par email
        subject = "Code de vérification - SuperPharma"
        message = f"""
Bonjour {user.username},

Votre code de vérification est : {verification_code}

Ce code expirera dans 30 minutes. Si vous n'avez pas demandé cette action, veuillez ignorer cet email.

Cordialement,
L'équipe SuperPharma
"""
        from_email = settings.DEFAULT_FROM_EMAIL
        try:
            send_mail(subject, message, from_email, [email])
            messages.success(request, f"Un code de vérification a été envoyé à {email}.")
            return redirect("confirmation_code")  # Redirige vers la page de saisie du code
        except Exception as e:
            messages.error(request, f"Erreur lors de l'envoi de l'email : {str(e)}")
            return redirect("verification")

    return render(request, "verificaionMail.html")


def confirmation_code(request):
    if request.method == "POST":
        code = request.POST.get('verification_code')

        # Récupérer les données de session
        stored_code = request.session.get('verification_code')
        expiration_time_str = request.session.get('expiration_time')
        user_id = request.session.get('user_id')

        if not stored_code or not expiration_time_str:
            messages.error(request, "Code expiré ou invalide.")
            return redirect("verification")

        # Convertir l'heure d'expiration en datetime
        expiration_time = datetime.fromisoformat(expiration_time_str)

        # Vérifier si le code a expiré
        if timezone.now() > expiration_time:
            messages.error(request, "Le code a expiré.")
            return redirect("verification")

        # Vérifier si le code correspond
        if str(code) == str(stored_code):
            user = User.objects.get(id=user_id)
            return redirect("modifierCode", uid=user.id)  # Redirection vers la modification
        else:
            messages.error(request, "Code incorrect.")
            return redirect("confirmation_code")

    return render(request, "confirmation_code.html")


#fonction pour changer le MDP

import re
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
import re
from datetime import timedelta

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

import re
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User

def Changement_Code(request, uid):
    # Vérifier si l'ID utilisateur de l'URL correspond à celui de la session
    user_id = request.session.get("user_id")
    expiration_time_str = request.session.get("expiration_time")

    if not user_id or not expiration_time_str or int(user_id) != int(uid):
        messages.error(request, "Session invalide ou expirée. Veuillez recommencer.")
        return redirect("verification")

    try:
        expiration_time = datetime.fromisoformat(expiration_time_str)
    except ValueError:
        messages.error(request, "Erreur de session. Veuillez recommencer.")
        return redirect("verification")

    if timezone.now() > expiration_time:
        messages.error(request, "Le délai de modification a expiré. Veuillez recommencer.")
        return redirect("verification")

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
        return redirect("verification")

    if request.method == "POST":
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password == password_confirm:
            if len(password) < 8:
                messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
            elif not any(char.isdigit() for char in password):
                messages.error(request, "Le mot de passe doit contenir au moins un chiffre.")
            elif not any(char.isalpha() for char in password):
                messages.error(request, "Le mot de passe doit contenir au moins une lettre.")
            elif not re.search(r'[!@#$%(),.?":{}|<>]', password):
                messages.error(request, "Le mot de passe doit contenir au moins un caractère spécial (!@#$%(),.?\":{}|<>).")
            else:
                user.set_password(password)
                user.save()
                request.session.pop("user_id", None)
                request.session.pop("expiration_time", None)
                request.session.pop("verification_code", None)
                messages.success(request, "Votre mot de passe a été modifié avec succès. Connectez-vous.")
                return redirect("login")
        else:
            messages.error(request, "Les mots de passe ne correspondent pas.")

    return render(request, "nouveauMDP.html")





@login_required
def modifier_photo_profil(request, utilisateur_id):
    utilisateur = User.objects.get(id=utilisateur_id)
    if request.method == 'POST':
        form = PhotoProfilForm(request.POST, request.FILES, instance=utilisateur.profil)
        if form.is_valid():
            form.save()
            return redirect('liste_utilisateurs')
    else:
        form = PhotoProfilForm(instance=utilisateur.profil)
    
    return render(request, 'modifier_photo_profil.html', {'form': form})
# donction de deconnection




from django.http import JsonResponse

@login_required
def confirmer_abonnement(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user = request.user
        if hasattr(user, 'profil') and hasattr(user.profil, 'compte'):
            compte = user.profil.compte
            compte.paypal_subscription_id = data.get("subscriptionID")
            compte.abonnement_active = True
            compte.save()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)



def Deconnection(request):
    
    logout(request)
    return redirect("login")     



