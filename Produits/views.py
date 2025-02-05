from django.shortcuts import HttpResponse, render,redirect, get_object_or_404, HttpResponseRedirect
import mimetypes
from .models import Produits, Vente, Facture_client, Customer
from django.db import transaction
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.views.generic import ListView,CreateView,UpdateView,DetailView,DeleteView
from .forms import CategoryForm, ContactMessageForm
from .forms import AjoutProduit , AjoutVentemultiple,DevisFactForm ,DevisForm,AjoutA,formParametre,StockLotExpirationForm,BonDeCommandeForm
from django.core.paginator import Paginator
from django.contrib import messages
from datetime import datetime,date, timedelta
from decimal import Decimal, InvalidOperation
from .models import *
from django.db.models.functions import TruncMonth
from django.db.models import Sum,Count, F,ExpressionWrapper, DecimalField
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import parametre
from utilisateurs.models import Compte, UtilisateurProfil
from django.http import HttpResponseForbidden
from django.http import Http404
from django.core.mail import EmailMessage

import json





import logging

# Configurez un logger pour voir les erreurs dans le terminal
logger = logging.getLogger(__name__)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
# Create your views here.




######### support

from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ContactMessageForm
from .models import ContactMessage

@login_required
def contact_view(request):
    if request.method == 'POST':
        form = ContactMessageForm(request.POST, request.FILES)
        if form.is_valid():
            # Ajouter l'utilisateur connecté au message
            contact_message = form.save(commit=False)
            contact_message.user = request.user
            contact_message.save()

            # Email
            subject = f"Message de support de {request.user.username}"
            message_body = contact_message.message
            sender_email = request.user.email  # Email de l'utilisateur
            recipient_email = 'fantchewoukomiahoeke@gmail.com'  # L'email où l'administrateur reçoit les messages

            # Création de l'email
            email = EmailMessage(
                subject,
                message_body,
                sender_email,
                [recipient_email]
            )

            # Vérifier s'il y a une image jointe
            if contact_message.image:
                image_file = contact_message.image  # Fichier image
                image_name = image_file.name  # Nom du fichier
                image_content = image_file.read()  # Lire le contenu

                # Déterminer le type MIME
                mime_type, _ = mimetypes.guess_type(image_name)
                if not mime_type:
                    mime_type = 'application/octet-stream'  # Type par défaut

                # Ajouter la pièce jointe
                email.attach(image_name, image_content, mime_type)

            # Envoyer l'email
            email.send()

            messages.success(request, 'Votre message a été envoyé avec succès !')
            return redirect('contact')
    else:
        form = ContactMessageForm()

    return render(request, 'contact.html', {'form': form})


@login_required(login_url='login')
def annuler_modification(request):
    # Redirige vers la liste des produits ou une autre page
    return redirect('produits')
@login_required(login_url='login')
def Acceuil(request):
    # Redirige vers la liste des produits ou une autre page
    return render(request,'acceuil.html')

@login_required(login_url='login')
def afficher_facture(request, facture_id):
    """
    Affiche les détails d'une facture spécifique liée au compte utilisateur.
    """
    # Récupérer la facture liée au compte utilisateur
    facture = get_object_or_404(Facture_client, id=facture_id, compte=request.user.profil.compte)
    
    # Récupérer les ventes associées à cette facture
    ventes = facture.ventes.all()  # Utilisation du related_name 'ventes'

    # Récupérer les paramètres liés au compte utilisateur
    n = get_object_or_404(parametre, compte=request.user.profil.compte)  # Filtrer par compte de l'utilisateur connecté
    
    # Contexte envoyé au template
    context = {
        'facture': facture,
        'ventes': ventes,
        'parametre': n
    }
    
    return render(request, 'facture.html', context)




@login_required(login_url='login')
def Acc(request):
    utilisateur = request.user

    # Vérification si l'utilisateur est un administrateur du compte
    try:
        compte = Compte.objects.get(administrateur=utilisateur)
    except Compte.DoesNotExist:
        # Si l'utilisateur n'est pas administrateur, on vérifie s'il est un utilisateur simple
        try:
            profil = UtilisateurProfil.objects.get(utilisateur=utilisateur)
            compte = profil.compte
        except UtilisateurProfil.DoesNotExist:
            # Si aucun compte n'est trouvé, redirection vers la page de connexion
            return redirect('login')

    # Récupération des paramètres globaux
    n = get_object_or_404(parametre, compte=request.user.profil.compte)

    # Ajout des informations dans le contexte
    context = {
        'parametre': n,
        'compte': compte,
        'utilisateur': utilisateur,
    }

    return render(request, 'acc.html', context)

 
    


class affichage(LoginRequiredMixin, ListView):
    template_name = 'home.html'
    
    def get_queryset(self):
        # Récupération du compte de l'utilisateur connecté
        compte = self.request.user.profil.compte
        
        # Filtrage des produits en fonction du compte
        queryset = Produits.objects.filter(compte=compte)  # Remplacez 'compte' par le bon champ de relation
        return queryset
    
    def get_context_data(self, **kwargs):
        # Récupération du premier paramètre pour le compte de l'utilisateur
        compte = self.request.user.profil.compte
        n = get_object_or_404(parametre, compte=compte) 
        
        # Appeler la méthode de la classe parente pour obtenir le contexte
        context = super().get_context_data(**kwargs)
        
        # Ajouter la variable 'n' au contexte
        context['parametre'] = n
        
        # Ajouter la quantité totale en stock pour chaque produit du compte
        produits = context['object_list']  # Liste des produits retournée par get_queryset
        for produit in produits:
            # Calculer la quantité totale en stock du produit
            total_stock = produit.lots.filter(compte=compte).aggregate(total_stock=Sum('quantite'))['total_stock'] or 0
            produit.total_stock = total_stock  # Ajouter la quantité totale en stock à l'objet produit
            
        return context

    
    
class ProductList(LoginRequiredMixin, ListView):
    model = Produits
    template_name = 'EEEEE.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        """Précharge les lots pour optimiser les requêtes et filtre les produits par compte."""
        # Récupérer le compte de l'utilisateur connecté
        compte = self.request.user.profil.compte
        
        # Filtrer les produits par le compte de l'utilisateur
        return Produits.objects.prefetch_related('lots').filter(compte=compte)
    
    def get_context_data(self, **kwargs):
        
        compte = self.request.user.profil.compte
        param = get_object_or_404(parametre, compte=compte) 
        
        context = super().get_context_data(**kwargs)
        
        # Ajouter parametre au contexte
          # Récupérer le premier paramètre (ou celui que vous voulez)
        context['parametre'] = param  # Ajoute l'objet parametre au contexte

        return context
#achats

class affichageAchat(LoginRequiredMixin, ListView):
    # affichage du template
    template_name = 'achat.html'
    
    # Filtrage des produits par le compte de l'utilisateur
    def get_queryset(self):
        # Récupérer le compte de l'utilisateur connecté
        compte = self.request.user.profil.compte
        
        # Retourne les produits associés au compte de l'utilisateur
        return Produits.objects.filter(compte=compte)

class AjoutProduits(LoginRequiredMixin, CreateView):
    model = Produits
    form_class = AjoutProduit
    template_name = 'ajout-donnees.html'
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Passer le compte de l'utilisateur connecté au formulaire
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def form_valid(self, form):
        # Associer le produit au compte de l'utilisateur connecté
        compte = self.request.user.profil.compte
        form.instance.compte = compte
        
        
        return super().form_valid(form)



   
# classe pour les parametre 
class foncParametre(LoginRequiredMixin, UpdateView):
    model = parametre
    form_class = formParametre
    template_name = 'parametre.html'

    def get_object(self, queryset=None):
        compte = self.request.user.profil.compte  # Récupérer le compte de l'utilisateur connecté
        # Vérifier si un parametre existe déjà pour ce compte
        try:
            obj = parametre.objects.get(compte=compte)
        except parametre.DoesNotExist:
            obj = parametre.objects.create(compte=compte, user=self.request.user)
        return obj

    def form_valid(self, form):
        # Associe le compte à l'instance et l'utilisateur à l'instance du paramètre
        compte = self.request.user.profil.compte
        form.instance.compte = compte
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Les paramètres ont été mis à jour avec succès.")
        return reverse('home')  # Redirection après validation

 
 #fonction de modification
 
class Update_donnees(LoginRequiredMixin, UpdateView):
    model = Produits
    form_class = AjoutProduit
    template_name = 'modification.html'
    success_url = reverse_lazy('home')

    def get_queryset(self):
        # Récupère uniquement les produits associés au compte de l'utilisateur connecté
        compte = self.request.user.profil.compte
        return Produits.objects.filter(compte=compte)

    def get_object(self, queryset=None):
        # Récupérer l'objet avec le UUID + Slug au lieu de l'ID
        obj = get_object_or_404(Produits, uuid=self.kwargs['uuid'], slug=self.kwargs['slug'])

        # Vérifier si l'utilisateur a le droit de modifier cet objet
        if obj.compte != self.request.user.profil.compte:
            raise PermissionDenied
        return obj

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte  # Passer le compte de l'utilisateur connecté
        return kwargs

    
 # modification du stock 


@login_required(login_url='login')
def modifier_lots_produit(request, uuid, slug):
    compte = request.user.profil.compte  # Récupérer le compte de l'utilisateur connecté
    produit = Produits.objects.get(uuid=uuid, compte=compte)  # Utiliser le uuid pour trouver le produit

    # Vérifier que le slug du produit correspond bien
    if produit.slug != slug:
        raise Http404("Produit introuvable ou slug incorrect.")

    # Filtrer les lots associés à ce produit
    lots = StockLot.objects.filter(produit=produit).order_by('date_expiration')

    paginator = Paginator(lots, 10)  # 10 lots par page
    page_number = request.GET.get('page')
    page_lots = paginator.get_page(page_number)

    if request.method == 'POST':
        has_errors = False
        for lot in lots:
            form = StockLotExpirationForm(request.POST, prefix=f'lot_{lot.id}', instance=lot)
            if form.is_valid():
                form.save()
            else:
                has_errors = True

        if has_errors:
            messages.error(request, "Certains lots n'ont pas été mis à jour à cause d'erreurs. Vérifiez les dates d'expiration.")
            return render(request, 'modifier_lots_produit.html')
        else:
            messages.success(request, "Les dates d'expiration des lots ont été mises à jour avec succès.")

        return redirect('produits')

    forms = [
        {
            'lot': lot,
            'form': StockLotExpirationForm(prefix=f'lot_{lot.id}', instance=lot)
        }
        for lot in page_lots
    ]

    return render(request, 'modifier_lots_produit.html', {
        'forms': forms,
        'produit': produit,
        'page_lots': page_lots
    })

    
    
    
    #### supprimer lot
@login_required(login_url='login')
def supprimer_lot(request, lot_id):
    compte = request.user.profil.compte  # Récupérer le compte de l'utilisateur connecté
    
    # Récupérer le lot à supprimer, et s'assurer qu'il appartient au compte de l'utilisateur
    lot = get_object_or_404(StockLot, id=lot_id, produit__compte=compte)

    # Vérifier que le lot appartient bien au compte de l'utilisateur
    if lot.produit.compte != compte:
        messages.error(request, "Vous n'avez pas la permission de supprimer ce lot.")
        return HttpResponseForbidden("Accès interdit")

    # Supprimer le lot
    lot.delete()

    # Message de succès après la suppression
    messages.success(request, f"Le lot du produit {lot.produit.name} a été supprimé avec succès.")
    
    # Rediriger vers la page de gestion des lots ou la liste des produits
    return redirect('produits')

#class supprimer
class delete(LoginRequiredMixin, DeleteView):
    model = Produits
    template_name = 'delete.html'
    context_object_name = 'n'
    success_url = reverse_lazy('home')

    def get_queryset(self):
        # Récupère uniquement les produits associés au compte de l'utilisateur connecté
        compte = self.request.user.profil.compte
        return Produits.objects.filter(compte=compte)

    def get_object(self, queryset=None):
        # Récupérer l'objet produit basé sur l'UUID et le Slug
        uuid = self.kwargs.get('uuid')
        slug = self.kwargs.get('slug')
        obj = get_object_or_404(Produits, uuid=uuid, slug=slug, compte=self.request.user.profil.compte)
        if obj.compte != self.request.user.profil.compte:
            raise PermissionDenied
        return obj
    
    

# @login_required(login_url ='login')
# def supprimer(request, id):
#     if request.method =="POST":
#         produit = get_object_or_404(Produits, id=id)
#         produit.delete()
#         return JsonResponse({'success':True, 'message': "Le produit a été supprimé avec succès"})
#     return JsonResponse({'success': False, 'message': "Methode non autorisée" })
 
 
 
#fonction de recherche
@login_required(login_url='login')
def recherche(request):
    query = request.GET.get('produit')
    # Filtrer les produits liés au compte de l'utilisateur connecté
    donnees = Produits.objects.filter(name__icontains=query, compte__utilisateurs__utilisateur=request.user)
    param = parametre.objects.filter(compte__utilisateurs__utilisateur=request.user).first()  # Récupérer les paramètres associés au compte de l'utilisateur connecté
        
    context = {
        'donnees': donnees,
        'parametre': param,
    } 
    return render(request, 'resultat_recherche.html', context)



# recherche dans le stocks
@login_required(login_url='login')
def rechercher_stock(request):
    query = request.GET.get('produit')  # Récupère la recherche entrée par l'utilisateur
    # Filtrer les résultats de stock pour le compte de l'utilisateur connecté
    results = StockLot.objects.filter(produit__name__icontains=query, produit__compte__utilisateurs__utilisateur=request.user)
    param = parametre.objects.filter(compte__utilisateurs__utilisateur=request.user).first()  # Récupérer les paramètres associés au compte de l'utilisateur connecté

    # Obtenir les produits liés aux résultats
    produits = set(result.produit for result in results)

    context = {
        'object_list': produits,  # Liste des produits
        'parametre': param,
    }
    return render(request, 'recherche_stock.html', context)



#class pour voir les details
class edit(LoginRequiredMixin, DetailView):
    model = Produits
    template_name = 'detail.html'
    context_object_name = 'n'

    def get_queryset(self):
        # Assurez-vous de filtrer pour que seuls les produits du compte de l'utilisateur connecté soient accessibles
        return Produits.objects.filter(compte__utilisateurs__utilisateur=self.request.user)

    def get_object(self, queryset=None):
        # Récupérer l'objet produit basé sur l'UUID et le Slug
        uuid = self.kwargs.get('uuid')
        slug = self.kwargs.get('slug')
        # Filtrer selon le compte de l'utilisateur connecté pour plus de sécurité
        obj = get_object_or_404(Produits, uuid=uuid, slug=slug, compte__utilisateurs__utilisateur=self.request.user)
        return obj
class editstock(LoginRequiredMixin, DetailView):
    model = Produits
    template_name = 'detail_stock.html'
    context_object_name = 'product'
    
   
    def get_queryset(self):
        compte = self.request.user.profil.compte
        # Assurez-vous de filtrer pour que seuls les produits du compte de l'utilisateur connecté soient accessibles
        return Produits.objects.prefetch_related('lots').filter(compte=compte)

    def get_object(self, queryset=None):
        # Récupérer l'objet produit basé sur l'UUID et le Slug
        uuid = self.kwargs.get('uuid')
        slug = self.kwargs.get('slug')
        # Filtrer selon le compte de l'utilisateur connecté pour plus de sécurité
        obj = get_object_or_404(StockLot, uuid=uuid, slug=slug, compte__utilisateurs__utilisateur=self.request.user)
        return obj

    
@login_required(login_url='login')
def details_facture(request, facture_id):
    # Récupérer la facture avec ses ventes associées, filtrées par le compte de l'utilisateur connecté
    facture = get_object_or_404(Facture_client, id=facture_id, compte=request.user.profil.compte)
    
    # Récupérer les devis associés à ce devis spécifique et les lier au compte utilisateur
    factures = Vente.objects.filter(facture=facture, compte=request.user.profil.compte)
    
    # Récupérer les paramètres (parametre) liés au compte utilisateur si nécessaire
    param = get_object_or_404(parametre, compte=request.user.profil.compte)
    # Contexte envoyé au template
    context = {
        'facture': facture,
        'factures': factures,
        'parametre': param,
    }
   
    return render(request, 'details_facture.html', context)

@login_required(login_url='login')
def rechercher_facture(request):
    # Fonction de recherche basée sur l'ID de la facture, filtrée par le compte de l'utilisateur connecté
    query = request.GET.get('query', '').strip()
    facture = None
    if query:
        try:
            facture = Facture_client.objects.get(id=query, compte__utilisateurs__utilisateur=request.user)
        except Facture_client.DoesNotExist:
            facture = None

    return render(request, 'rechercher_facture.html', {'facture': facture, 'query': query})
@login_required(login_url='login')
def recherche_devis(request):
    # Fonction de recherche basée sur l'ID du devis, filtrée par le compte de l'utilisateur connecté
    query = request.GET.get('query', '').strip()
    devisfac = None
    if query:
        try:
            devisfac = DevisFact.objects.get(id=query, compte__utilisateurs__utilisateur=request.user)
        except DevisFact.DoesNotExist:
            devisfac = None

    return render(request, 'rechercher_devisfac.html', {'devisfac': devisfac, 'query': query})

@login_required(login_url='login')
def rechercher_bon_commande(request):
    # Fonction de recherche basée sur l'ID du bon de commande, filtrée par le compte de l'utilisateur connecté
    query = request.GET.get('query', '').strip()
    boncommandefac = None
    if query:
        try:
            boncommandefac = commandefact.objects.get(id=query, compte__utilisateurs__utilisateur=request.user)
        except commandefact.DoesNotExist:
            boncommandefac = None

    return render(request, 'rechercher_commande.html', {'boncommandefac': boncommandefac, 'query': query})

@login_required(login_url='login')
def rechercher_factureAchat(request):
    # Fonction de recherche basée sur l'ID de la facture d'achat, filtrée par le compte de l'utilisateur connecté
    query = request.GET.get('query', '').strip()
    factureA = None
    if query:
        try:
            factureA = FactureAchat.objects.get(id=query, compte__utilisateurs__utilisateur=request.user)
            
        
        except FactureAchat.DoesNotExist:
            factureA = None
    
    return render(request, 'rechercher_facttureAchat.html', {'factureA': factureA, 'query': query})

# @login_required(login_url='login')
# def rechercher_facture(request):
#     # Fonction de recherche basée sur l'ID de la facture, filtrée par le compte de l'utilisateur connecté
#     query = request.GET.get('query', '').strip()
#     facture = None
#     if query:
#         try:
#             facture = Facture_client.objects.get(id=query, compte__utilisateurs__utilisateur=request.user)
#         except Facture_client.DoesNotExist:
#             facture = None

#     return render(request, 'rechercher_facture.html', {'facture': facture, 'query': query})
@login_required(login_url='login')
def get_product_details(request, produit_id):
    try:
        # Filtrer le produit par le compte de l'utilisateur connecté
        produit = Produits.objects.get(id=produit_id, compte__utilisateurs__utilisateur=request.user)
        return JsonResponse({
            'id': produit.id,
            'name': produit.name,  # Ajout du nom du produit
            'price': produit.price,
            'stock': produit.quantite
        })
    except Produits.DoesNotExist:
        return JsonResponse({'error': 'Produit introuvable'}, status=404)








@login_required(login_url='login')
def VenteProduits(request):
    erreurs_stock = []
    erreurs_validation = []

    # Filtrer les produits associés au compte de l'utilisateur connecté
    produits = Produits.objects.filter(compte__utilisateurs__utilisateur=request.user).prefetch_related('lots').all()

    if request.method == 'POST':
        try:
            # Récupération des informations client
            customer_name = request.POST.get('customer')
            if not customer_name:
                raise ValueError("Le nom du client est requis.")

            remise_globale = Decimal(request.POST.get('remise_globale', 0))
            if remise_globale < 0 or remise_globale > 100:
                raise ValueError("La remise globale doit être comprise entre 0 et 100.")

            # Lier le client au compte de l'utilisateur connecté
            customer, _ = Customer.objects.get_or_create(name=customer_name, compte=request.user.profil.compte)
            ventes = []
            total_facture = Decimal(0)

            # Validation initiale des stocks et remises
            for key in request.POST:
                if key.startswith('produit_'):
                    index = key.split('_')[1]
                    produit_id = request.POST.get(f'produit_{index}')
                    quantite_demandee = int(request.POST.get(f'quantite_{index}', 0))
                    remise = Decimal(request.POST.get(f'remise_{index}', 0))

                    if remise < 0 or remise > 100:
                        erreurs_validation.append(f"La remise de la ligne {index} doit être comprise entre 0 et 100.")

                    if produit_id and quantite_demandee > 0:
                        try:
                            produit = Produits.objects.get(id=produit_id, compte=request.user.profil.compte)
                            total_stock_lots = produit.lots.filter(quantite__gt=0).aggregate(total=Sum('quantite'))['total'] or 0
                            if quantite_demandee > total_stock_lots:
                                erreurs_stock.append(f"Stock insuffisant pour {produit.name}. Disponible : {total_stock_lots}.")
                        except Produits.DoesNotExist:
                            erreurs_validation.append(f"Le produit avec l'ID {produit_id} n'existe pas ou n'appartient pas à ce compte.")
                    else:
                        erreurs_validation.append(f"Produit ou quantité invalide pour la ligne {index}.")

            if erreurs_stock or erreurs_validation:
                raise ValueError("Des erreurs de validation sont survenues.")

            # Traitement des ventes et mise à jour des lots
            for key in request.POST:
                if key.startswith('produit_'):
                    index = key.split('_')[1]
                    produit_id = request.POST.get(f'produit_{index}')
                    quantite_demandee = int(request.POST.get(f'quantite_{index}', 0))
                    remise = Decimal(request.POST.get(f'remise_{index}', 0))

                    if produit_id and quantite_demandee > 0:
                        produit = Produits.objects.get(id=produit_id, compte=request.user.profil.compte)
                        lots = produit.lots.filter(quantite__gt=0).order_by('date_expiration')
                        montant_total_vente = Decimal(0)

                        for lot in lots:
                            if quantite_demandee == 0:
                                break

                            if lot.quantite >= quantite_demandee:
                                montant_total_vente += produit.price * quantite_demandee * (1 - remise / 100)
                                lot.quantite -= quantite_demandee
                                quantite_demandee = 0
                            else:
                                montant_total_vente += produit.price * lot.quantite * (1 - remise / 100)
                                quantite_demandee -= lot.quantite
                                lot.quantite = 0

                            lot.save()  # Sauvegarde du lot après modification

                        if quantite_demandee > 0:
                            raise ValueError(f"Stock insuffisant pour {produit.name} après revalidation.")

                        vente = Vente(
                            produit=produit,
                            quantite=int(request.POST.get(f'quantite_{index}', 0)),
                            remise=remise,
                            customer=customer,
                            montant_total=montant_total_vente,
                            compte=request.user.profil.compte  # Lier la vente au compte
                        )
                        ventes.append(vente)
                        total_facture += montant_total_vente

            # Application de la remise globale
            total_facture *= (1 - remise_globale / 100)

            # Démarrage de la transaction pour sauvegarder la facture et les ventes
            with transaction.atomic():
                # Création de la facture associée au compte de l'utilisateur
                facture = Facture_client(
                    customer=customer,
                    remise_globale=remise_globale,
                    montant_total=total_facture,
                    compte=request.user.profil.compte  # Lier la facture au compte
                )
                facture.save()  # Sauvegarder la facture dans la transaction

                # Sauvegarde des ventes
                for vente in ventes:
                    vente.facture = facture
                    vente.save()

            messages.success(request, f"Facture créée avec succès pour {customer.name}.")
            return redirect('facture', facture_id=facture.id)

        except ValueError as ve:
            messages.error(request, f"Erreur de validation : {str(ve)}")
        except Exception as e:
            messages.error(request, f"Une erreur inattendue est survenue : {str(e)}")
    else:
        messages.info(request, "Veuillez remplir les informations pour effectuer une vente.")

    context = {
        'produits': produits,
        'erreurs_stock': erreurs_stock,
        'erreurs_validation': erreurs_validation,
    }
    return render(request, 'formulaire-vente-multiple.html', context)





@login_required(login_url='login')
def historique_ventes(request):
    # Récupérer toutes les factures avec leurs ventes associées, filtrées par le compte de l'utilisateur connecté
    #factures = Facture_client.objects.filter(ventes__produit__compte__utilisateurs__utilisateur=request.user).prefetch_related('ventes__produit').all()
    
    compte = request.user.profil.compte  # Utilisation du profil pour accéder au compte de l'utilisateur connecté

    # Afficher toutes les factures liées au compte de l'utilisateur connecté
    factures = Facture_client.objects.filter(compte=compte).order_by('-date_creation')
    
    param = get_object_or_404(parametre, compte=request.user.profil.compte)

    return render(request, 'historique_ventes.html', {'factures': factures, 'parametre': param})





# fonction d'achat
@login_required(login_url='login')
def creer_achat(request):
    compte = request.user.profil.compte  # Récupérer le compte de l'utilisateur connecté

    # Filtrer les produits et fournisseurs associés au compte
    produits = Produits.objects.filter(compte=compte)
    fournisseurs = Fournisseur.objects.filter(compte=compte)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                fournisseur_name = request.POST.get('fournisseur')
                if not fournisseur_name:
                    raise ValueError("Le nom du fournisseur est requis.")
                
                remise_globale = Decimal(request.POST.get('remise_globale', 0))

                # Validation des champs globaux
                if remise_globale < 0 or remise_globale > 100:
                    raise ValueError("La remise globale doit être entre 0 et 100.")
                
                # Lier le fournisseur au compte de l'utilisateur
                fournisseur, _ = Fournisseur.objects.get_or_create(name=fournisseur_name, compte=compte)
                
                # Création de la facture d'achat associée au compte de l'utilisateur
                facture = FactureAchat(fournisseur=fournisseur, remise_globale=remise_globale, compte=compte)
                facture.save()

                # Création des lignes d'achat et des lots
                for key in request.POST:
                    if key.startswith('produit_'):
                        index = key.split('_')[1]
                        produit_id = request.POST.get(f'produit_{index}')
                        quantite = int(request.POST.get(f'quantite_{index}', 0))
                        remise = float(request.POST.get(f'remise_{index}', 0))
                        prix_unitaire = float(request.POST.get(f'prix_unitaire_{index}', 0))
                        date_expiration = request.POST.get(f'date_expiration_{index}')

                        # Validation des champs individuels
                        if quantite < 0:
                            raise ValueError("La quantité doit être supérieure ou égale à zéro.")
                        if prix_unitaire <= 0:
                            raise ValueError("Le prix unitaire doit être supérieur à zéro.")
                        if fournisseur is None:
                            raise ValueError("Le fournisseur est obligatoire.")
                        if remise < 0 or remise > 100:
                            raise ValueError("La remise doit être entre 0 et 100.")
                        if quantite > 0 and not date_expiration:
                            raise ValueError("La date d'expiration est requise lorsque la quantité est supérieure à zéro.")

                        # Récupération du produit et lier au compte
                        produit = Produits.objects.get(id=produit_id, compte=compte)

                        # Création de la ligne d'achat
                        achat = Achat(
                            produit=produit,
                            facture=facture,
                            quantite=quantite,
                            remise=remise,
                            prix_unitaire=prix_unitaire,
                            date_expiration=date_expiration,
                            compte=compte  # Lier l'achat au compte
                        )
                        achat.save()

                        # Mise à jour du stock global du produit
                        if quantite > 0:
                            produit.quantite += quantite
                            produit.save()

                            # Vérification et mise à jour des lots
                            lot_mis_a_jour = False
                            try:
                                # Priorité à un lot avec la même date d'expiration
                                lot_exist = StockLot.objects.get(produit=produit, date_expiration=date_expiration, compte=compte)
                                lot_exist.quantite += quantite
                                lot_exist.save()
                                lot_mis_a_jour = True
                            except StockLot.DoesNotExist:
                                # Si aucun lot avec la même date n'existe, chercher le premier lot avec quantité zéro
                                lot_zero = StockLot.objects.filter(produit=produit, quantite=0, compte=compte).first()
                                if lot_zero:
                                    lot_zero.quantite = quantite
                                    lot_zero.date_expiration = date_expiration
                                    lot_zero.save()
                                    lot_mis_a_jour = True

                            # Si aucun lot n'a été mis à jour, créer un nouveau lot
                            if not lot_mis_a_jour:
                                StockLot.objects.create(
                                    produit=produit,
                                    quantite=quantite,
                                    date_expiration=date_expiration,
                                    compte=compte  # Lier le lot au compte
                                )

                # Supprimer les lots restants avec quantité zéro après toutes les mises à jour
                StockLot.objects.filter(quantite=0, compte=compte).delete()

                # Succès
                messages.success(request, "Achat enregistré avec succès.")
                return redirect('historique_achats')

        except Exception as e:
            # Gestion des erreurs
            messages.error(request, f"Erreur : {str(e)}")

    context = {'produits': produits, 'fournisseurs': fournisseurs}
    return render(request, 'creer_achat.html', context)






@login_required(login_url='login')
def historique_achats(request):
    # Récupérer le compte de l'utilisateur connecté via son profil
    compte = request.user.profil.compte  # Utilisation du profil pour accéder au compte de l'utilisateur connecté

    # Afficher toutes les factures liées au compte de l'utilisateur connecté
    factures = FactureAchat.objects.filter(compte=compte).order_by('-date_creation')
    
    for facture in factures:
        facture.montant_total = round(facture.calculer_montant_total() , 2)  # Assurez-vous que le montant est calculé

    
    # Récupérer les paramètres associés au compte de l'utilisateur connecté
    param = get_object_or_404(parametre, compte=compte)
    
    context = {'factures': factures, 'parametre': param}
    return render(request, 'historique_achats.html', context)



@login_required(login_url='login')
def details_facture_achat(request, facture_pk):
    # Récupérer la facture et le compte de l'utilisateur connecté
    facture = get_object_or_404(FactureAchat, pk=facture_pk)
    compte = request.user.profil.compte

    factures = FactureAchat.objects.filter(compte=compte)

    for facture in factures:
        facture.montant_total = round(facture.calculer_montant_total() , 2) # Assurez-vous que le montant est calculé

    # Vérifier si la facture appartient au compte de l'utilisateur connecté
    if facture.compte == compte:
        achats = Achat.objects.filter(facture=facture)
        param = get_object_or_404(parametre, compte=request.user.profil.compte)
        context = {
            'facture': facture,
            'achats': achats,
            'parametre': param,
        }
        return render(request, 'details_facture_achat.html', context)
    else:
        # Si l'utilisateur n'a pas la permission de voir cette facture
        messages.error(request, "Vous n'avez pas la permission de voir cette facture.")
        return redirect('historique_achats')




@login_required(login_url='login')
def supprimer_facture_achat(request, facture_pk):
    # Récupérer la facture d'achat à supprimer
    facture = get_object_or_404(FactureAchat, pk=facture_pk)

    # Vérifier si la facture appartient au compte de l'utilisateur connecté
    if facture.compte != request.user.profil.compte:
        messages.error(request, "Vous n'avez pas la permission de supprimer cette facture.")
        return redirect('historique_achats')

    if request.method == 'POST':
        # Supprimer la facture
        facture.delete()
        messages.success(request, "La facture a été supprimée avec succès.")
        return redirect('historique_achats')

    # Si la méthode n'est pas POST, afficher une page de confirmation
    return render(request, 'suppression_achat_histo.html', {'facture': facture})
@login_required(login_url='login')
def supprimer_facture_vente(request, facture_pk):
    # Récupérer la facture d'achat à supprimer
    facture = get_object_or_404(Facture_client, pk=facture_pk)

    # Vérifier si la facture appartient au compte de l'utilisateur connecté
    if facture.compte != request.user.profil.compte:
        messages.error(request, "Vous n'avez pas la permission de supprimer cette facture.")
        return redirect('historique_ventes')

    if request.method == 'POST':
        # Supprimer la facture
        facture.delete()
        messages.success(request, "La facture a été supprimée avec succès.")
        return redirect('historique_ventes')

    # Si la méthode n'est pas POST, afficher une page de confirmation
    return render(request, 'suppression_vente_histo.html', {'facture': facture})
@login_required(login_url='login')
def supprimer_facture_devis(request, devis_pk):
    # Récupérer la facture d'achat à supprimer
    devis = get_object_or_404(DevisFact, pk=devis_pk)

    # Vérifier si la facture appartient au compte de l'utilisateur connecté
    if devis.compte != request.user.profil.compte:
        messages.error(request, "Vous n'avez pas la permission de supprimer ce devis.")
        return redirect('historique_devis')

    if request.method == 'POST':
        # Supprimer la facture
        devis.delete()
        messages.success(request, "Le devis a été supprimée avec succès.")
        return redirect('historique_devis')

    # Si la méthode n'est pas POST, afficher une page de confirmation
    return render(request, 'suppression_devis_histo.html', {'devis': devis})
@login_required(login_url='login')
def supprimer_facture_commande(request, bon_pk):
    # Récupérer la facture d'achat à supprimer
    bon = get_object_or_404(commandefact, pk=bon_pk)

    # Vérifier si la facture appartient au compte de l'utilisateur connecté
    if bon.compte != request.user.profil.compte:
        messages.error(request, "Vous n'avez pas la permission de supprimer ce bon de commande.")
        return redirect('historique_commande')

    if request.method == 'POST':
        # Supprimer la facture
        bon.delete()
        messages.success(request, "Le bon de commande a été supprimée avec succès.")
        return redirect('historique_commande')

    # Si la méthode n'est pas POST, afficher une page de confirmation
    return render(request, 'suppression_commande_histo.html', {'bon': bon})

def AchatProduits(request, id):
    
    produit = get_object_or_404(Produits, id=id)
    message = None
    form = AjoutA(request.POST)
    
    context = {
            'produit':produit,
            'form': form,
            'message':message
        }
    
    
    if request.method == 'POST':
        
        form = AjoutA(request.POST)
        #context = {}
        
        if form.is_valid():
            
            quantite = form.cleaned_data['quantite']
            fournisseur = form.cleaned_data['fournisseur']
            date_achat = form.cleaned_data['date_achat']
            priceA = form.cleaned_data['priceA']
            date_expirationM = form.cleaned_data['date_expirationM']
            
            
                
           
            fournisseur, _=Fournisseur.objects.get_or_create(name = fournisseur)
            
           
                
          
            sale = ProduitsAchat(produit = produit,priceA =priceA,date_expirationM=date_expirationM, quantite = quantite,date_achat = date_achat, fournisseur = fournisseur)
                
            sale.save()
                
            produit.quantite += quantite
            produit.save()
                
            return redirect('achat-donnee.html', sale_id = sale.id)
            
       
    return render(request, 'achat-donnee.html', context)


#fonction pour le recu
@login_required(login_url='login')
def Saverecu(request, id):
    
    vente = get_object_or_404(Vente, id=id)
    customer = vente.customer,
    quantite = vente.quantite,
    total_amount = vente.total_amount,
    produit = vente.produit,
    
    recu = Facture_client(
        customer = customer,
        quantite = quantite,
        total_amount =  total_amount,
        produit = produit
    )
    
    recu.save()
    return redirect('facture', sale_id = id)

#fonction pour la facture
@login_required(login_url='login')
def Facture(request, sale_id):
    
    sale = get_object_or_404(Vente, id = sale_id)
    customer = sale.customer
    produit  = sale.produit
    quantite = sale.quantite
    sale_date = sale.sale_date
    total_amount = sale.total_amount
    n = get_object_or_404(parametre, compte=request.user.profil.compte)
    
    context = {
        'sale': sale,
        'customer': customer,
        'produit': produit,
        'quantite': quantite,
        'sale_date': sale_date,
        'id': sale.id,
        'prix_unitaire': produit.price,
        'total_amount': total_amount,
        'parametre' : n
    }
    
    return render (request, 'facture-client.html', context)

   


# vue pour les rapports et stastiques
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth

@login_required(login_url='login')
def rapports_statistiques(request):
    # Récupération du mois courant
    mois_courant = timezone.now().replace(day=1)  # Début du mois courant
    mois_actuelle = timezone.now()  # Début du mois courant

    # Ventes par produit : Limitées au mois courant et au compte de l'utilisateur
    ventes_par_produit = list(Vente.objects.filter(
        sale_date__month=mois_courant.month,
        compte=request.user.profil.compte  # Lier les ventes au compte de l'utilisateur
    ).values('produit__name').annotate(
        total_quantite=Sum('quantite')
    ).order_by('-total_quantite')[:15])

    # Ventes par client : Limitées au mois courant et au compte de l'utilisateur
    ventes_par_client = list(Vente.objects.filter(
        sale_date__month=mois_courant.month,
        compte=request.user.profil.compte  # Lier les ventes au compte de l'utilisateur
    ).values('customer__name').annotate(
        total_achats=Sum('montant_total')
    ).order_by('-total_achats'))

    # Ventes par mois : Utilisation de TruncMonth pour récupérer les ventes par mois
    ventes_par_mois = list(Vente.objects.filter(
        sale_date__month=mois_courant.month,
        compte=request.user.profil.compte  # Lier les ventes au compte de l'utilisateur
    ).annotate(
        mois=TruncMonth('sale_date')
    ).values('mois').annotate(
        total_ventes=Sum('montant_total')
    ).order_by('mois'))

    # Formater la date mois en YYYY-MM
    for item in ventes_par_mois:
        item['mois'] = item['mois'].strftime('%Y-%m')

    # Si aucune vente n'est trouvée pour le mois courant, on ajoute une entrée avec total_ventes = 0
    if not ventes_par_mois:
        ventes_par_mois = [{'mois': mois_courant, 'total_ventes': 0}]

    # Produits proches de l’expiration : Filtrer par compte de l'utilisateur
    produits_proches_expiration = StockLot.objects.filter(
        date_expiration__lte=timezone.now() + timedelta(days=30),
        compte=request.user.profil.compte  # Lier les lots de stock au compte de l'utilisateur
    )

    # Clients fidèles : Top 5 par montant total, limité au mois courant et au compte de l'utilisateur
    clients_fideles = list(Vente.objects.filter(
        sale_date__month=mois_courant.month,
        compte=request.user.profil.compte # Lier les ventes au compte de l'utilisateur
    ).values('customer__name').annotate(
        total_achats=Sum('montant_total')
    ).order_by('-total_achats')[:5])

    # Stocks produits : Quantité totale par produit et lié au compte de l'utilisateur
    stock_par_produit = Produits.objects.filter(
        compte=request.user.profil.compte  # Lier les produits au compte de l'utilisateur
    ).annotate(
        total_quantity=Sum('lots__quantite')
    ).order_by('-total_quantity')

    # Achats par fournisseur : Filtrer par le compte de l'utilisateur
    achats_par_fournisseur = FactureAchat.objects.filter(
        compte=request.user.profil.compte  # Lier les achats au compte de l'utilisateur
    ).annotate(
        total_achats=Sum('achats__prix_unitaire')
    ).order_by('-total_achats')

    # Résumé global pour le mois courant et le compte de l'utilisateur
    total_ventes = Vente.objects.filter(
        sale_date__month=mois_courant.month,
        compte=request.user.profil.compte  # Lier les ventes au compte de l'utilisateur
    ).aggregate(total=Sum('montant_total'))['total'] or 0

    total_produits = Produits.objects.filter(
        compte=request.user.profil.compte  # Lier les produits au compte de l'utilisateur
    ).aggregate(total=Count('id'))['total'] or 0

    total_clients = Customer.objects.filter(
        compte=request.user.profil.compte  # Lier les clients au compte de l'utilisateur
    ).aggregate(total=Count('id'))['total'] or 0

    param = get_object_or_404(parametre, compte=request.user.profil.compte)

    context = {
        'ventes_par_produit': ventes_par_produit,
        'ventes_par_client': ventes_par_client,
        'ventes_par_mois': ventes_par_mois,
        'produits_proches_expiration': produits_proches_expiration,
        'clients_fideles': clients_fideles,
        'stock_par_produit': stock_par_produit,
        'achats_par_fournisseur': achats_par_fournisseur,
        'total_ventes': total_ventes,
        'total_produits': total_produits,
        'total_clients': total_clients,
        'parametre': param,
        'mois_actuelle': mois_actuelle,
    }

    return render(request, 'statistiques.html', context)





# VUE DE NOTIFICATION
@login_required(login_url='login')
def notifications(request):
    notifications = Notification.objects.filter(is_lu=False).order_by('-date_creation')
    if request.method == 'POST':
        notification_ids = request.POST.getlist('notification_ids')
        Notification.objects.filter(id__in=notification_ids).update(is_lu=True)

    return render(request, 'notifications.html', {'notifications': notifications})

from django.db.models import Sum
from datetime import datetime, timedelta

from datetime import datetime, timedelta
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from .models import StockLot, Notification

from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
from itertools import groupby
from operator import itemgetter
from django.db.models import Sum

def verifier_notifications(request):
    """Vérifie et envoie les notifications (motivations, stock, expiration)."""
    now = datetime.now().date()

    if not hasattr(request.user, 'profil') or not hasattr(request.user.profil, 'compte'):
        return JsonResponse({"error": "Aucun profil ou compte associé à l'utilisateur."}, status=400)

    compte_admin = request.user.profil.compte

    # 1. Notification de motivation (envoyée une fois à la première connexion et chaque début de mois)
    derniere_motivation = Notification.objects.filter(compte=compte_admin, type='motivation').order_by('-date_creation').first()
    if not derniere_motivation or derniere_motivation.date_creation.date().month != now.month:
        Notification.objects.create(
            compte=compte_admin,
            type='motivation',
            message="Bienvenue sur SuperPharma ! Félicitations pour avoir choisi notre solution. Profitez de toutes nos fonctionnalités pour une gestion fluide et optimale de votre pharmacie. Avec SuperPharma, maximisez l'efficacité, restez à jour et offrez à vos clients un service de qualité. Nous sommes là pour vous accompagner à chaque étape !"
        )

    # 2. Vérification des notifications pour les produits (indépendant des actions sur les produits)
    lots = StockLot.objects.filter(produit__compte=compte_admin)
    for lot in lots:
        total_quantite = StockLot.objects.filter(produit=lot.produit, produit__compte=compte_admin).aggregate(total=Sum('quantite'))['total'] or 0

        # Notification de stock minimum
        if total_quantite <= 10:
            Notification.objects.get_or_create(
                compte=compte_admin,
                type='stock_minimum',
                message=f"Le stock du médicament {lot.produit.name} est bas ({total_quantite} restants).",
                defaults={'date_creation': now}
            )

        # Notification d'expiration imminente
        if lot.date_expiration <= now + timedelta(days=60):
            Notification.objects.get_or_create(
                compte=compte_admin,
                type='expirant',
                message=f"Le médicament {lot.produit.name} expire bientôt (le {lot.date_expiration}).",
                defaults={'date_creation': now}
            )

        # Notification de produit périmé
        if lot.date_expiration < now:
            Notification.objects.get_or_create(
                compte=compte_admin,
                type='Perimé',
                message=f"Le lot du médicament {lot.produit.name} est périmé et doit être supprimer du stock .",
                defaults={'date_creation': now}
            )

    # Récupération des notifications non lues
    unread_notifications = Notification.objects.filter(is_lu=False, compte=compte_admin)

    # Regroupement des notifications par date
    notifications_by_date = {}
    for notification in unread_notifications:
        date = notification.date_creation.date()
        if date not in notifications_by_date:
            notifications_by_date[date] = []
        notifications_by_date[date].append(notification)

    # Assurez-vous que la motivation est toujours en haut du groupe
    for date, notifications in notifications_by_date.items():
        notifications.sort(key=lambda x: 0 if x.type == 'motivation' else 1)

    count_unread_notifications = unread_notifications.count()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        notifications_data = [{"id": n.id, "type": n.type, "message": n.message, "is_lu": n.is_lu} for n in unread_notifications]
        return JsonResponse({
            "notifications": notifications_data,
            "unread_count": count_unread_notifications
        })

    return render(request, 'notifications.html', {
        'notifications_by_date': notifications_by_date,
        'unread_count': count_unread_notifications
    })

from django.http import JsonResponse
from .models import Notification

from django.http import JsonResponse
from .models import Notification

def marquer_notifications_lues(request):
    """Marque les notifications sélectionnées comme lues."""
    if request.method == "POST":
        notification_ids = request.POST.getlist('notification_ids[]')
        if notification_ids:
            notifications = Notification.objects.filter(id__in=notification_ids)
            notifications.update(is_lu=True)
            
            # Retourner les notifications mises à jour
            updated_notifications = list(notifications.values('id'))
            return JsonResponse({"status": "Notifications marquées comme lues", "updated_notifications": updated_notifications})
        return JsonResponse({"error": "Aucune notification sélectionnée"}, status=400)
    return JsonResponse({"error": "Requête invalide"}, status=400)










# BON DE COMMANDE ET DEVI
# Bon de commande

@login_required(login_url='login')
def creer_bon_de_commande(request):
    # Récupérer le compte de l'utilisateur connecté
    compte_utilisateur = request.user.profil.compte
    
    # Récupérer tous les produits associés au compte de l'utilisateur
    produits = Produits.objects.filter(compte=compte_utilisateur)

    if request.method == 'POST':
        try:
            with transaction.atomic():  # Démarrer une transaction atomique
                fournisseur_name = request.POST.get('fournisseur')
                
                if not fournisseur_name:
                    raise ValueError("Le nom du fournisseur est requis.")
                
                # Si le fournisseur n'existe pas, le créer et lier au compte de l'utilisateur
                fournisseur, _ = Fournisseur.objects.get_or_create(name=fournisseur_name, compte=compte_utilisateur)

                # Création de la facture d'achat liée au compte de l'utilisateur connecté
                commandefac = commandefact(fournisseur=fournisseur, compte=compte_utilisateur)
                commandefac.save()

                # Création des lignes de commande
                for key in request.POST:
                    if key.startswith('produit_'):
                        index = key.split('_')[1]
                        produit_id = request.POST.get(f'produit_{index}')
                        quantite = int(request.POST.get(f'quantite_{index}', 0))
                        prix_unitaire = float(request.POST.get(f'prix_unitaire_{index}', 0))

                        # Validation des champs individuels
                        if quantite < 0:
                            raise ValueError("La quantité doit être supérieure ou égale à zéro.")
                        if prix_unitaire <= 0:
                            raise ValueError("Le prix unitaire doit être supérieur à zéro.")
                        if fournisseur is None:
                            raise ValueError("Le fournisseur est obligatoire.")
                        
                        # Récupération du produit associé au compte de l'utilisateur
                        try:
                            produit = Produits.objects.get(id=produit_id, compte=compte_utilisateur)  # Lier au compte
                        except Produits.DoesNotExist:
                            raise ValueError(f"Le produit avec l'ID {produit_id} n'existe pas ou n'est pas lié à votre compte.")

                        # Création de la ligne d'achat liée au compte de l'utilisateur connecté
                        commande = BonDeCommande(
                            produit=produit,
                            commandefac=commandefac,
                            quantite=quantite,
                            prix_unitaire=prix_unitaire,
                            compte=compte_utilisateur  # Lier la commande au compte de l'utilisateur
                        )
                        commande.save()

                # Mise à jour du total du bon de commande
                commandefac.total = commandefac.calculer_montant_total()
                commandefac.save()

                # Succès
                messages.success(request, "Bon de commande enregistré avec succès.")
                return redirect('afficher_bon_commande', commandefac_id=commandefac.id)

        except Exception as e:
            # Annulation de la transaction en cas d'erreur
            transaction.rollback()  # Annuler la transaction
            messages.error(request, f"Erreur : {str(e)}")  # Afficher le message d'erreur

    # Filtrer les fournisseurs et produits associés au compte de l'utilisateur
    fournisseurs = Fournisseur.objects.filter(compte=compte_utilisateur)
    produits = Produits.objects.filter(compte=compte_utilisateur)
    return render(request, 'creer_bon_de_commande.html', {'fournisseurs': fournisseurs, 'produits': produits})
# Devis


@login_required(login_url='login')
def afficher_bon_commande(request, commandefac_id):
    """
    Affiche le bon de commande en fonction de l'ID de la commande passée en paramètre.
    """
    # Récupérer le compte de l'utilisateur connecté
    compte_utilisateur = request.user.profil.compte

    # Récupérer le bon de commande lié au compte de l'utilisateur
    commandefac = get_object_or_404(commandefact, id=commandefac_id, compte=compte_utilisateur)

    # Récupérer les produits associés à ce bon de commande (les items de commande)
    commandes = commandefac.commandes.all()

    # Récupérer les paramètres du compte de l'utilisateur
    n = get_object_or_404(parametre, compte=compte_utilisateur)

    # Contexte envoyé au template
    context = {
        'commandefac': commandefac,
        'commandes': commandes,
        'parametre': n
    }

    return render(request, 'boncommande.html', context)

    
 
    
@login_required(login_url='login')
def afficher_details_bon_commande(request, bon_id):
    """
    Affiche les détails d'un bon de commande spécifique.
    """
    # Récupérer le bon de commande en fonction de l'ID passé en paramètre et le lier au compte utilisateur
    commandefac = get_object_or_404(commandefact, id=bon_id, compte=request.user.profil.compte)

    # Récupérer les commandes associées à ce bon de commande et les lier au compte utilisateur
    commandes = BonDeCommande.objects.filter(commandefac=commandefac, compte=request.user.profil.compte)

    # Récupérer les paramètres (parametre) liés au compte utilisateur si nécessaire
    param = get_object_or_404(parametre, compte=request.user.profil.compte) # Adapte selon tes besoins pour lier parametre au compte
    
    # Contexte envoyé au template
    context = {
        'commandefac': commandefac,
        'commandes': commandes,
        'parametre': param,
    }

    return render(request, 'details_bon_commande.html', context)




# devis






from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.db.models import Sum
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
@login_required(login_url='login')
def creer_devis(request):
   
    erreurs_stock = []
    erreurs_validation = []
    compte_utilisateur = request.user.profil.compte  # Récupérer le compte de l'utilisateur connecté
    produits = Produits.objects.filter(compte=compte_utilisateur).prefetch_related('lots').all()  # Filtrer les produits par compte

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Récupération et validation du nom du client
                client_name = request.POST.get('client')
                if not client_name:
                    raise ValueError("Le champ 'client' est requis.")
                
                # Récupération ou création du client lié au compte de l'utilisateur
                customer, _ = Customer.objects.get_or_create(name=client_name, compte=compte_utilisateur)

                # Récupération et validation de la remise globale
                remise_globale_str = request.POST.get('remise_globale', '0')
                try:
                    remise_globale = Decimal(remise_globale_str) if remise_globale_str.strip() else Decimal(0)
                    if remise_globale < 0 or remise_globale > 100:
                        raise ValueError("La remise globale doit être comprise entre 0 et 100.")
                except (InvalidOperation, ValueError):
                    raise ValueError("La remise globale est invalide.")

                # Récupération de la remarque et date d'expiration du devis
                date_expiration_devis = request.POST.get('date_expiration', None)
                remarque_devis = request.POST.get('remarque', '')

                devis_items = []
                total_devisfac = Decimal(0)

                # Parcours des produits soumis dans le formulaire
                for key in request.POST:
                    if key.startswith('produit_'):
                        index = key.split('_')[1]
                        produit_id = request.POST.get(f'produit_{index}')
                        quantite_str = request.POST.get(f'quantite_{index}', '0')
                        remise_str = request.POST.get(f'remise_specifique_{index}', '0')
                        date_expiration = request.POST.get(f'date_expiration_{index}', None)

                        try:
                            quantite = int(quantite_str) if quantite_str.strip() else 0
                            remise = Decimal(remise_str) if remise_str.strip() else Decimal(0)
                            if remise < 0 or remise > 100:
                                raise ValueError(f"Remise spécifique pour la ligne {index} invalide.")
                        except (ValueError, InvalidOperation):
                            erreurs_validation.append(f"Les données pour la ligne {index} sont invalides.")
                            continue

                        if produit_id and quantite > 0:
                            try:
                                # Récupérer le produit lié au compte de l'utilisateur
                                produit = Produits.objects.get(id=produit_id, compte=compte_utilisateur)
                                total_stock_lots = produit.lots.filter(quantite__gt=0).aggregate(total=Sum('quantite'))['total'] or 0
                                if quantite > total_stock_lots:
                                    erreurs_stock.append(f"Stock insuffisant pour {produit.name}. Disponible : {total_stock_lots}.")
                                    continue
                               

                                montant_total_produit = produit.price * quantite * (1 - remise / 100)

                                devis_items.append(Devis(
                                    produit=produit,
                                    quantite=quantite,
                                    date_expiration=date_expiration,
                                    remise_specifique=remise,
                                    client=customer,
                                    total=montant_total_produit,
                                    createur=request.user,  # Ajout du créateur
                                    compte=compte_utilisateur  # Lier le devis au compte de l'utilisateur
                                ))
                                total_devisfac += montant_total_produit
                               

                            except Produits.DoesNotExist:
                                erreurs_validation.append(f"Produit introuvable pour la ligne {index}.")
                        else:
                            erreurs_validation.append(f"Produit ou quantité invalide pour la ligne {index}.")

                if erreurs_stock or erreurs_validation:
                    raise ValueError("Des erreurs de validation ou de stock sont survenues.")

                # Application de la remise globale  
                total_devisfac *= (1 - remise_globale / 100)

                # Création de la facture de devis avec remarque et date d'expiration, et lier au compte de l'utilisateur
                devisfac = DevisFact(
                    client=customer,
                    remise_globale=remise_globale,
                    total=total_devisfac,
                    date_expiration=date_expiration_devis,
                    remarque=remarque_devis,  # Ajout de la remarque
                    compte=compte_utilisateur  # Lier le devis au compte de l'utilisateur
                )
                devisfac.save()

                # Sauvegarde des lignes de devis et lier au compte de l'utilisateur
                for devis_item in devis_items:
                    devis_item.devisfac = devisfac
                    devis_item.save()

                messages.success(request, f"Devis créé avec succès pour {customer.name}.")
                return redirect('afficher_devis',    devisfac_id=devisfac.id)

        except ValueError as ve:
            messages.error(request, f"Erreur de validation : {ve}")
        except Exception as e:
            messages.error(request, f"Une erreur inattendue est survenue : {type(e).__name__} - {str(e)}")
    else:
        messages.info(request, "Veuillez remplir les informations pour établir un devis.")

    context = {
        'produits': produits,
        'erreurs_stock': erreurs_stock,
        'erreurs_validation': erreurs_validation,
    }
    return render(request, 'creer_devis.html', context)









@login_required(login_url='login')
def devis_detail(request, devis_id):
    """
    Affiche les détails d'un devis spécifique.
    """
    # Récupérer le devis en fonction de l'ID passé en paramètre et le lier au compte utilisateur
    devisfac = get_object_or_404(DevisFact, id=devis_id, compte=request.user.profil.compte)
    
    # Récupérer les devis associés à ce devis spécifique et les lier au compte utilisateur
    deviss = Devis.objects.filter(devisfac=devisfac, compte=request.user.profil.compte)
    
    # Récupérer les paramètres (parametre) liés au compte utilisateur si nécessaire
    param = get_object_or_404(parametre, compte=request.user.profil.compte)
    # Contexte envoyé au template
    context = {
        'devisfac': devisfac,
        'deviss': deviss,
        'parametre': param,
    }
   
    return render(request, 'devis_detail.html', context)



# Historique des commandes et devis
@login_required(login_url='login')
def historique_commande(request):
    """
    Affiche l'historique des commandes associées au compte utilisateur.
    """
    commandes = commandefact.objects.filter(compte = request.user.profil.compte).order_by('-date_creation')
    n = get_object_or_404(parametre, compte=request.user.profil.compte)
    return render(request, 'historique_commande.html', {'commandes': commandes, 'parametre': n})
@login_required(login_url='login')
def historique_devis(request):
    """
    Affiche l'historique des devis associés au compte utilisateur.
    """
    deviss = DevisFact.objects.filter(compte = request.user.profil.compte).order_by('-date_creation')
    n = get_object_or_404(parametre, compte=request.user.profil.compte)
    return render(request, 'historique_devis.html', {'deviss': deviss, 'parametre': n})



@login_required(login_url='login')
def afficher_deviss(request, devisfac_id):
    """
    Affiche le bon de commande en fonction de l'ID de la commande passée en paramètre.
    """
    # Récupérer le compte de l'utilisateur connecté
    compte_utilisateur = request.user.profil.compte

    # Récupérer le devis lié au compte de l'utilisateur
    devisfac = get_object_or_404(DevisFact, id=devisfac_id, compte=compte_utilisateur)

    # Récupérer les produits associés à ce devis (les items de devis)
    deviss = devisfac.deviss.all()
    totalavant = devisfac.total / (1 - devisfac.remise_globale / 100)
    # Récupérer les paramètres du compte de l'utilisateur
    n = get_object_or_404(parametre, compte=compte_utilisateur)

    # Contexte envoyé au template
    context = {
        'devisfac': devisfac,
        'deviss': deviss,
        'parametre': n,
        'totalavant': totalavant
        
    }

    return render(request, 'devis.html', context)

####### ajouter categrie

from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from .models import Categories
from .forms import CategoryForm

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Categories
    form_class = CategoryForm
    template_name = 'category_create.html'
    success_url = reverse_lazy('category_list')  # Redirige après succès

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Passer l'utilisateur connecté au formulaire
        return kwargs

    def form_valid(self, form):
        compte = self.request.user.profil.compte
        form.instance.compte = compte
        
        # Vérifier si l'utilisateur est administrateur du compte
        if not compte.utilisateurs.filter(utilisateur=self.request.user, est_admin=True).exists():
            return HttpResponseForbidden("Vous n'êtes pas autorisé à ajouter une catégorie.")
        
        return super().form_valid(form)
    
########### LISTE CATEGORIE
class CategoryListView(LoginRequiredMixin, ListView):
    model = Categories
    template_name = 'category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        # Récupère les catégories associées au compte de l'utilisateur connecté
        compte = self.request.user.profil.compte
        return Categories.objects.filter(compte=compte)


######### MODIFIER CATEGORIE

class CategoryEditView(LoginRequiredMixin, UpdateView):
    model = Categories
    form_class = CategoryForm
    template_name = 'category_edit.html'
    success_url = reverse_lazy('category_list')  # Redirige après succès

    def get_object(self, queryset=None):
        # Récupère la catégorie pour l'utilisateur connecté
        obj = super().get_object(queryset)
        compte = self.request.user.profil.compte
        # Vérifie que la catégorie appartient bien au compte de l'utilisateur connecté
        if obj.compte != compte:
            raise HttpResponseForbidden("Vous n'êtes pas autorisé à modifier cette catégorie.")
        return obj

    def form_valid(self, form):
        # Ajouter l'utilisateur actuel à la catégorie modifiée (si nécessaire)
        compte = self.request.user.profil.compte
        form.instance.compte = compte  # Associe la catégorie au compte de l'utilisateur
        return super().form_valid(form)
    
    #######33 SUPPRIMER 
class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Categories
    template_name = 'category_confirm_delete.html'
    success_url = reverse_lazy('category_list')  # Redirige après suppression

    def get_object(self, queryset=None):
        # Récupère la catégorie pour l'utilisateur connecté
        obj = super().get_object(queryset)
        compte = self.request.user.profil.compte
        # Vérifie que la catégorie appartient bien au compte de l'utilisateur connecté
        if obj.compte != compte:
            raise HttpResponseForbidden("Vous n'êtes pas autorisé à supprimer cette catégorie.")
        return obj

    def delete(self, request, *args, **kwargs):
        # Appel à la suppression du modèle
        obj = self.get_object()
        obj.delete()
        return super().delete(request, *args, **kwargs)
    
    
    
    
from django.http import HttpResponseForbidden
from functools import wraps

from django.shortcuts import render

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, '403.html', {'message': 'Vous devez être connecté.'}, status=403)
        
        try:
            if not request.user.profil.is_compte_admin:
                return render(request, '403.html', {'message': 'Accès réservé aux administrateurs.'}, status=403)
        except AttributeError:
            return render(request, '403.html', {'message': 'Accès interdit.'}, status=403)
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


#####"""

# Vue pour le tableau de bord administrateur du compte
@admin_required
def admin_account_dashboard(request):
    utilisateurs = UtilisateurProfil.objects.filter(compte=request.user.profil.compte)

    compte = request.user.profil.compte # Récupérer le compte associé à l'utilisateur connecté
    nb_utilisateurs = compte.utilisateurs.count() 

    context = {
        'utilisateurs': utilisateurs,
        'nb_utilisateurs':  nb_utilisateurs,
        'compte': compte,  # Passer l'objet compte dans le contexte
        'creation_utilisateur_url': reverse('creation_utilisateur_secondaire'),
        'liste_utilisateurs_url': reverse('liste_utilisateurs'),
        'ajouter_categorie_url': reverse('ajouter_categorie'),
        'liste_categories_url': reverse('category_list'),
    }
    return render(request, 'admin_dashboard.html', context)


#########paypal

import paypalrestsdk

from django.shortcuts import render
from django.http import JsonResponse
import requests
from django.conf import settings

def paypal_checkout(request):
    return render(request, "payment/checkout.html", {
        "paypal_client_id": settings.PAYPAL_CLIENT_ID,
        "paypal_plan_id": settings.PAYPAL_PLAN_ID
    })





def payment_success(request):
    subscription_id = request.GET.get("subscription_id", "")

    if request.user.is_authenticated:
        try:
            compte = request.user.profil.compte
            compte.paypal_subscription_id = subscription_id
            compte.abonnement_active = True
            compte.dernier_paiement = now()
            compte.save()
            messages.success(request, "Paiement réussi ! Abonnement activé.")
        except Compte.DoesNotExist:
            messages.error(request, "Aucun compte trouvé.")
    
    return render(request, "payment/success.html")

def payment_cancel(request):
    return render(request, "payment/cancel.html")

from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

import json
import logging
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Compte
from .paypal import verify_paypal_webhook

logger = logging.getLogger(__name__)

@csrf_exempt
def paypal_webhook(request):
    """Gère les notifications PayPal et met à jour l'abonnement des comptes."""
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        logger.error("Webhook PayPal: JSON invalide")
        return JsonResponse({"error": "JSON invalide"}, status=400)

    # Vérifier la signature du webhook PayPal pour éviter la fraude
    if not verify_paypal_webhook(request.headers, payload):
        logger.warning("Webhook PayPal: Signature invalide")
        return JsonResponse({"error": "Signature invalide"}, status=400)

    event_type = payload.get("event_type")
    subscription_id = payload.get("resource", {}).get("subscription_id")

    if not subscription_id:
        logger.warning("Webhook PayPal: Aucun ID d'abonnement reçu")
        return JsonResponse({"error": "Aucun ID d'abonnement reçu"}, status=400)

    try:
        compte = Compte.objects.get(paypal_subscription_id=subscription_id)
    except Compte.DoesNotExist:
        logger.warning(f"Webhook PayPal: Compte non trouvé pour l'ID {subscription_id}")
        return JsonResponse({"error": "Compte non trouvé"}, status=404)

    try:
        if event_type == "BILLING.SUBSCRIPTION.PAYMENT.SUCCEEDED":
            now = timezone.now()
            if compte.dernier_paiement is None or compte.dernier_paiement.date() != now.date():
                compte.dernier_paiement = now
                compte.abonnement_active = True
                compte.save()
                logger.info(f"Paiement réussi pour le compte {compte.id}, abonnement activé.")
            return JsonResponse({"status": "Paiement enregistré"}, status=200)

        elif event_type == "BILLING.SUBSCRIPTION.ACTIVATED":
            if not compte.abonnement_active:
                compte.abonnement_active = True
                compte.save()
                logger.info(f"Abonnement activé pour le compte {compte.id}.")
            return JsonResponse({"status": "Abonnement activé"}, status=200)

        elif event_type in ["BILLING.SUBSCRIPTION.CANCELLED", "BILLING.SUBSCRIPTION.EXPIRED"]:
            if compte.abonnement_active:
                compte.abonnement_active = False
                compte.save()
                logger.info(f"Abonnement annulé ou expiré pour le compte {compte.id}.")
            return JsonResponse({"status": "Abonnement annulé"}, status=200)

        elif event_type == "BILLING.SUBSCRIPTION.SUSPENDED":
            if compte.abonnement_active:
                compte.abonnement_active = False
                compte.save()
                logger.warning(f"Abonnement suspendu pour le compte {compte.id}.")
            return JsonResponse({"status": "Abonnement suspendu"}, status=200)

        elif event_type == "PAYMENT.SALE.REFUNDED":
            if compte.dernier_paiement is not None:
                compte.dernier_paiement = None  # Réinitialisation en cas de remboursement
                compte.save()
                logger.warning(f"Paiement remboursé pour le compte {compte.id}, dernier paiement réinitialisé.")
            return JsonResponse({"status": "Paiement remboursé"}, status=200)

        logger.info(f"Webhook PayPal: Événement ignoré ({event_type}) pour le compte {compte.id}.")
        return JsonResponse({"status": "Aucune action nécessaire"}, status=200)

    except Exception as e:
        logger.error(f"Erreur lors du traitement du webhook PayPal pour le compte {compte.id}: {str(e)}")
        return JsonResponse({"error": "Erreur interne"}, status=500)



from django.http import JsonResponse
from django.utils.timezone import now
from utilisateurs.models import Compte

from django.http import JsonResponse
from django.utils.timezone import now

def verifier_abonnement(request):
    if request.user.is_authenticated and hasattr(request.user, 'profil') and hasattr(request.user.profil, 'compte'):
        compte = request.user.profil.compte

        # Vérification si l'utilisateur a un abonnement après la période d'essai
        if compte.dernier_paiement:
            abonnement_expire = compte.abonnement_est_expire()

            if abonnement_expire:
                # Si l'abonnement est expiré
                return JsonResponse({
                    "abonnement_expire": True,
                    "jours_restants": 0
                })

            # Si l'abonnement est actif, calculer les jours restants
            jours_restants = max(0, 30 - (now() - compte.dernier_paiement).days)

            return JsonResponse({
                "abonnement_expire": False,
                "jours_restants": jours_restants
            })
        else:
            # Pas d'abonnement souscrit (en période d'essai ou n'a pas souscrit)
            return JsonResponse({
                "abonnement_expire": False,
                "message": "Aucun abonnement souscrit."
            })

    return JsonResponse({"error": "Utilisateur non connecté"}, status=401)

def verifier_essai_gratuit(request):
    if request.user.is_authenticated and hasattr(request.user, 'profil') and hasattr(request.user.profil, 'compte'):
        compte = request.user.profil.compte
        date_creation = compte.date_creation  # Supposons que ce champ existe
        essai_duree = timedelta(days=7)  # Durée de l'essai gratuit

        jours_restants = max(0, (date_creation + essai_duree - now()).days)

        return JsonResponse({
            "essai_expire": jours_restants == 0,
            "jours_restants": jours_restants
        })
    
    return JsonResponse({"error": "Utilisateur non connecté"}, status=401)
