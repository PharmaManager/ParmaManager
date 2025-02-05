from django.forms import ModelForm
from django import forms
from .models import Produits, Vente, ProduitsAchat,parametre,Achat,Customer,Categories, FactureAchat,StockLot,commandefact,Devis, DevisFact
from django.forms import modelformset_factory
from django.core.exceptions import ValidationError
from datetime import date
from decimal import Decimal
from .models import ContactMessage
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ['name']  # Inclure uniquement le champ 'name'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Extraire l'utilisateur de kwargs
        super().__init__(*args, **kwargs)

        if self.user:
            compte = self.user.profil.compte
            # Vérifier si l'utilisateur est admin du compte
            if not compte.utilisateurs.filter(utilisateur=self.user).first().is_compte_admin:
                raise forms.ValidationError("Vous n'êtes pas l'administrateur de ce compte.")
        
        
#####support
class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['sujet', 'message', 'image']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Entrez votre message ici...'}),
        }
        labels = {
            'sujet': 'Sujet',
            'message': 'Message',
            'image': 'Joindre une image (facultatif)',
        }
        
class   formParametre(ModelForm):
    
    class Meta:
        model = parametre
        fields = [
            'name','adresse','devise','numero','email','logo','fiscal','remarque'
        ]
        
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'placeholder':'Entrez le nom de la pharmaçie',
                    'class' :'form-control'
                }),
            # 'pays': forms.TextInput(
            #     attrs={
            #         'placeholder':'Entrez le pays de votre pharmaçie (Rouyaume du maroc)',
            #         'class' :'form-control'
            #     }
            #),
            'fiscal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Régime fiscal'}),
            'remarque': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Les produits vendus ne sont ni échangés ni remboursés. Pour tout soucis, voir le vendeur. '}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de téléphone'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adresse email'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            
            'adresse': forms.TextInput(
                attrs={
                    'placeholder':'Entrez adresse de la pharmaçie',
                    'class' :'form-control'
                }
            ),
            
            'devise' : forms.TextInput(
                attrs={
                    'placeholder': 'Entrez la devise (DH)',
                    'class':'form-control'
                }
            )
        }
        
        def __init__(self, *args, **kwargs):
            
            super(formParametre, self).__init__(*args,**kwargs)
            
            self.fields['name'].error_messages = {
                'required': 'Le nom est obligatoire',
                'invalid': 'Veuillez renseigner un nom valide'
            }
            self.fields['adresse'].error_messages = {
                'required': 'Adresse de la pharmaçie est obligatoire',
                'invalid': 'Veuillez renseigner uen adresse  valide'
            }
            self.fields['devise'].error_messages = {
                'required': 'la devise est obligatoire est obligatoire',
                'invalid': 'Veuillez entrer une devise valide'
            }
            self.fields['remarque'].required = False

class AjoutProduit(forms.ModelForm):
    class Meta:
        model = Produits
        exclude = ['quantite', 'date_expiration',]
        fields = [
            'name', 'category', 'price',  'description',  'image'
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'placeholder': 'Entrez le nom du produit',
                    'class': 'form-control'
                }
            ),
            'category': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'price': forms.NumberInput(
                attrs={
                    'placeholder': 'Entrez le prix du produit',
                    'class': 'form-control'
                }
            ),
           
            'description': forms.Textarea(
                attrs={
                    'placeholder': 'Description du produit',
                    'class': 'form-control',
                    'rows': 4
                }
            ),
            
            'image': forms.FileInput(
                attrs={
                    'class': 'form-control-file'
                }
            )
        }

    def __init__(self, *args, **kwargs):
        compte = kwargs.pop('compte', None)  # Récupération du compte passé au formulaire
        super().__init__(*args, **kwargs)
        if compte:
            # Filtrer les catégories en fonction du compte
            self.fields['category'].queryset = Categories.objects.filter(compte=compte)

        # Messages d'erreur
        self.fields['name'].error_messages = {
            'required': 'Le nom du produit est obligatoire',
            'invalid': 'Veuillez renseigner un nom valide'
        }
        self.fields['category'].error_messages = {
            'required': 'La catégorie du produit est obligatoire',
            'invalid': 'Veuillez sélectionner une catégorie valide'
        }
        self.fields['price'].error_messages = {
            'required': 'Le prix du produit est obligatoire',
            'invalid': 'Veuillez entrer un prix valide'
        }
       
        self.fields['description'].error_messages = {
            'required': 'La description du produit est obligatoire',
            'invalid': 'Veuillez entrer une description valide'
        }
        

            


# class AjoutVentemultiple(forms.Form):
#     # Informations client
#     customer = forms.CharField(
#         max_length=100,
#         label="Nom du client",
#         widget=forms.TextInput(attrs={'class': 'form-control'}),
#         required=True
#     )

#     # Liste des produits (dynamique, à adapter selon le modèle de produit)
#     produits = Produits.objects.all()  # Récupère tous les produits depuis la base de données
    
#     # Champ pour chaque produit (dynamique)
#     for produit in produits:
#         # Champ pour choisir le produit
#         locals()[f'produit_{produit.id}'] = forms.ModelChoiceField(
#             queryset=Produits.objects.filter(id=produit.id),
#             initial=produit,
#             label=produit.name,
#             widget=forms.Select(attrs={'class': 'form-control'}),
#             required=True
#         )
        
#         # Champ pour la quantité
#         locals()[f'quantite_{produit.id}'] = forms.IntegerField(
#             label=f"Quantité de {produit.name}",
#             min_value=1,
#             initial=1,
#             widget=forms.NumberInput(attrs={'class': 'form-control'}),
#         )

#         # Champ pour le prix
#         locals()[f'price_{produit.id}'] = forms.DecimalField(
#             max_digits=10,
#             decimal_places=2,
#             label=f"Prix unitaire de {produit.name}",
#             initial=produit.price,
#             widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
#             required=True
#         )

#         # Champ pour la remise sur chaque produit
#         locals()[f'remise_{produit.id}'] = forms.FloatField(
#             min_value=0,
#             max_value=100,
#             label=f"Remise pour {produit.name} (%)",
#             initial=0,
#             widget=forms.NumberInput(attrs={'class': 'form-control'}),
#         )

#     # Champ pour la remise globale sur la facture (facultatif, si applicable à tous les produits)
#     remise_globale = forms.FloatField(
#         min_value=0,
#         max_value=100,
#         label="Remise globale (%)",
#         initial=0,
#         widget=forms.NumberInput(attrs={'class': 'form-control'})
#     )

#     # Champ caché pour gérer les produits (sera géré dynamiquement dans la vue)
#     articles = forms.CharField(
#         widget=forms.HiddenInput(),  # Masqué, sera géré dynamiquement
#     )

#     def __init__(self, *args, **kwargs):
#         super(AjoutVentemultiple, self).__init__(*args, **kwargs)
        
#         # Dynamique : pour chaque produit, ajouter un champ pour la quantité et la remise
#         for produit in self.produits:
#             self.fields[f'produit_{produit.id}'] = forms.ModelChoiceField(
#                 queryset=Produits.objects.filter(id=produit.id),
#                 initial=produit,
#                 label=produit.name,
#                 widget=forms.Select(attrs={'class': 'form-control'}),
#                 required=True
#             )
            
#             self.fields[f'quantite_{produit.id}'] = forms.IntegerField(
#                 label=f"Quantité de {produit.name}",
#                 min_value=1,
#                 initial=1,
#                 widget=forms.NumberInput(attrs={'class': 'form-control'}),
#             )
            
#             self.fields[f'price_{produit.id}'] = forms.DecimalField(
#                 max_digits=10,
#                 decimal_places=2,
#                 label=f"Prix unitaire de {produit.name}",
#                 initial=produit.price,
#                 widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
#                 required=True
#             )
            
#             self.fields[f'remise_{produit.id}'] = forms.FloatField(
#                 min_value=0,
#                 max_value=100,
#                 label=f"Remise pour {produit.name} (%)",
#                 initial=0,
#                 widget=forms.NumberInput(attrs={'class': 'form-control'})
#             )

class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        fields = ['produit', 'quantite', 'remise']

    quantite = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    remise = forms.FloatField(min_value=0, max_value=100, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    

class AjoutVentemultiple(forms.Form):
    customer = forms.CharField(max_length=100, label="Nom du client", widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)

    # Formset dynamique pour gérer plusieurs produits
    VenteFormSet = modelformset_factory(Vente, form=VenteForm, extra=1)  # `extra=1` ajoute une ligne vide pour ajouter un produit
    vente_formset = VenteFormSet(queryset=Vente.objects.none())  # On commence avec un formset vide

    # Remise globale
    remise_globale = forms.FloatField(min_value=0, max_value=100, label="Remise globale (%)", initial=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(AjoutVentemultiple, self).__init__(*args, **kwargs)

        # Ajouter les champs de produits dynamiquement dans le formset
        for form in self.vente_formset:
            form.fields['produit'] = forms.ModelChoiceField(queryset=Produits.objects.all(), label="Produit", widget=forms.Select(attrs={'class': 'form-control'}), required=True)
            form.fields['quantite'] = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
            form.fields['remise'] = forms.FloatField(min_value=0, max_value=100, label="Remise (%)", initial=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    # Option de gérer la remise globale (facultatif)
    def calculate_total(self):
        total = 0
        for form in self.vente_formset:
            if form.cleaned_data:
                produit = form.cleaned_data['produit']
                quantite = form.cleaned_data['quantite']
                remise = form.cleaned_data['remise']
                price = produit.price
                total += (price * quantite) * (1 - remise / 100)
        # Appliquer la remise globale si elle est présente
        remise_globale = self.cleaned_data.get('remise_globale', 0)
        total *= (1 - remise_globale / 100)
        return total



#POUR ACHAT 
class AchatForm(forms.ModelForm):
    class Meta:
        model = Achat
        fields = ['produit', 'quantite', 'prix_unitaire', 'remise', 'date_expiration']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control produit-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control quantite-input', 'min': '1', 'value': '1'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control prix_unitaire-input'}),
            'remise': forms.NumberInput(attrs={'class': 'form-control remise-input', 'min': '0', 'max': '100', 'value': '0'}),
            'date_expiration': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        # Validation des champs obligatoires
        produit = cleaned_data.get('produit')
        quantite = cleaned_data.get('quantite')
        prix_unitaire = cleaned_data.get('prix_unitaire')
        date_expiration = cleaned_data.get('date_expiration')

        if not produit:
            raise forms.ValidationError("Le champ produit est obligatoire.")
        if quantite is None or quantite <= 0:
            raise forms.ValidationError("La quantité doit être supérieure à zéro.")
        if prix_unitaire is None or prix_unitaire <= 0:
            raise forms.ValidationError("Le prix unitaire doit être supérieur à zéro.")
        if quantite > 0 and not date_expiration:
            raise forms.ValidationError("La date d'expiration est requise lorsque la quantité est supérieure à zéro.")

        return cleaned_data


class FactureAchatForm(forms.ModelForm):
    class Meta:
        model = FactureAchat
        fields = ['fournisseur', 'remise_globale']
        widgets = {
            'fournisseur': forms.TextInput(attrs={'class': 'form-control'}),
            'remise_globale': forms.NumberInput(attrs={'class': 'form-control remise-globale-input', 'min': '0', 'max': '100'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        # Validation du champ fournisseur
        fournisseur = cleaned_data.get('fournisseur')
        if not fournisseur:
            raise forms.ValidationError("Le champ fournisseur est obligatoire.")

        return cleaned_data




# modification dans le stock

class StockLotExpirationForm(forms.ModelForm):
    class Meta:
        model = StockLot
        fields = ['date_expiration']
        widgets = {
            'date_expiration': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_date_expiration(self):
        date_expiration = self.cleaned_data['date_expiration']
        if date_expiration <= date.today():
            raise ValidationError("La date d'expiration doit être une date future.")
        return date_expiration
    
    
from django import forms
from .models import BonDeCommande, Fournisseur, Produits

class BonDeCommandeForm(forms.ModelForm):
    class Meta:
        model = commandefact
        fields = ['fournisseur', 'produit', 'quantite', 'prix_unitaire']

    fournisseur = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le nom du fournisseur'})
    )
    produit = forms.ModelChoiceField(
        queryset=Produits.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control produit-select'})
    )
    quantite = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control quantite-input', 'min': 1, 'value': 1})
    )
    prix_unitaire = forms.DecimalField(
        min_value=0.01,
        widget=forms.NumberInput(attrs={'class': 'form-control price-input', 'min': 0.01, 'step': 0.01})
    )


# class AjoutVentemultiple(forms.Form):
    
    
#     customer = forms.CharField(
#         max_length=100,
#         label="Nom du client",
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
    
#     # Liste des produits (dynamique, à adapter selon le modèle de produit)
#     articles = forms.Field(
#         widget=forms.HiddenInput(),  # Masqué, sera géré dynamiquement dans la vue
#     )

#     # Champ pour la remise globale sur la facture (facultatif, si applicable à tous les produits)
#     remise = forms.FloatField(
#         min_value=0,
#         max_value=100,
#         label="Remise globale (%)",
#         initial=0,
#         widget=forms.NumberInput(attrs={'class': 'form-control'})
#     )

#     # Pour chaque produit, on crée un champ dynamique pour gérer quantité, prix et remise
#     def __init__(self, *args, **kwargs):
#         super(AjoutVentemultiple, self).__init__(*args, **kwargs)
        
#         # On récupère tous les produits disponibles dans la base de données
#         produits = Produits.objects.all()

#         # Dynamique: pour chaque produit, ajouter un champ pour la quantité et la remise
#         for produit in produits:
#             self.fields[f'produit_{produit.id}'] = forms.ModelChoiceField(
#                 queryset=Produits.objects.filter(id=produit.id),
#                 initial=produit,
#                 label=produit.name,
#                 widget=forms.Select(attrs={'class': 'form-control'}),
#                 required=True
#             )
            
#             self.fields[f'quantite_{produit.id}'] = forms.IntegerField(
#                 label=f"Quantité de {produit.name}",
#                 min_value=1,
#                 initial=1,
#                 widget=forms.NumberInput(attrs={'class': 'form-control'}),
               
#             )
            
#             self.fields[f'price_{produit.id}'] = forms.DecimalField(
#                 max_digits=10,
#                 decimal_places=2,
#                 label=f"Prix unitaire de {produit.name}",
#                 initial=produit.price,
#                 widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
#                 required=True
#             )
            
#             self.fields[f'remise_{produit.id}'] = forms.FloatField(
#                 min_value=0,
#                 max_value=100,
#                 label=f"Remise pour {produit.name} (%)",
#                 initial=0,
#                 widget=forms.NumberInput(attrs={'class': 'form-control'})
               
#             )
    
    # Vous pouvez ajouter une méthode pour valider ou traiter les champs, si nécessaire.

# class AjoutVentemultiple(forms.Form):
#     customer = forms.CharField(
#         max_length=100,
#         label="Nom du client",
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     remise = forms.FloatField(
#         min_value=0,
#         max_value=100,
#         label="Remise (%)",
#         initial=0,
#         widget=forms.NumberInput(attrs={'class': 'form-control'})
#     )

#     # Liste des produits (dynamique, à adapter selon le modèle de produit)
#     products = forms.ModelMultipleChoiceField(
#         queryset=Produits.objects.all(),
#         label="Produits à vendre",
#         widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control'})
#     )

#     quantite = forms.IntegerField(
#         min_value=1,
#         label="Quantité par produit",
#         widget=forms.NumberInput(attrs={'class': 'form-control'})
#     )

#     # Champ pour le prix unitaire (DecimalField pour les prix)
#     price = forms.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         label="Prix unitaire",
#         widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
#     )



class   AjoutA(ModelForm):
    
    class Meta:
        model = ProduitsAchat
        fields = [
            'priceA','quantite','fournisseur', 'date_expirationM','date_achat'
        ]
        
        widgets = {
            'fournisseur': forms.TextInput(
                attrs={
                    'placeholder':'Entrez et adresse du fournisseur',
                    'class' :'form-control'
                }
            ),
            
            'priceA' : forms.NumberInput(
                attrs={
                    'placeholder': 'Entrez le prix du produit',
                    'class':'form-control'
                }
            ),
            
            'quantite': forms.NumberInput(
                attrs= {
                    'placeholder': 'Entrez la quantité du produit',
                    'class':'form-control'
                }
            ),
            
            'date_achat': forms.DateInput(
                attrs={
                    'placeholder': 'La date achat',
                    'class':'form-control',
                     'type':'date'}
            ), 
            
            'date_expirationM': forms.DateInput(
                attrs ={
                    'placeholder': 'Date d\'expiration',
                    'class':'form-control',
                    'type':'date'
                }
                
            )
            
            
        }

        def __init__(self, *args, **kwargs):
            
            super(AjoutA, self).__init__(*args,**kwargs)
            
            self.fields['fournisseur'].error_messages = {
                'required': 'Le nom du fournisseur est obligatoire',
                'invalid': 'Veuillez renseigner un nom valide'
            }
            
            self.fields['priceA'].error_messages = {
                'required': 'le prix du produit est obligatoire',
                'invalid': 'Veuillez entrer un prix valide'
            }
            self.fields['quantite'].error_messages = {
                'required': 'la quantité du produit est obligatoire',
                'invalid': 'Veuillez entrer une quantité valide'
            }
            self.fields['date_achat'].error_messages = {
                'required': 'la date achat est obligatoire',
                'invalid': 'Veuillez entrer une date valide'
            }
            self.fields['date_expirationM'].error_messages = {
                'required': 'la date expiraion du produit est obligatoire',
                'invalid': 'Veuillez entrer une date valide '
            }


#DEVIS
from django import forms
from .models import Devis, DevisFact, Produits, Customer, StockLot
class DevisFactForm(forms.ModelForm):
    class Meta:
        model = DevisFact
        fields = ['client', 'date_expiration', 'statut', 'remarque', 'remise_globale']

    client = forms.CharField(
        required=True,
        label="Nom du Client",
        widget=forms.TextInput(attrs={'class': 'form-control  client-input'})
    )
    date_expiration = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control date_expiration-input'}),
        label="Date d'expiration"
    )
    statut = forms.ChoiceField(
        choices=DevisFact.STATUT_CHOICES,
        required=True,
        label="Statut du devis",
        widget=forms.Select(attrs={'class': 'form-control  statut-select'})
    )
    remarque = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control remarque-input'}),
        required=False,
        label="Remarque"
    )
    remise_globale = forms.DecimalField(
        max_digits=5, decimal_places=2, required=False, initial=0,
        label="Remise Globale",
        widget=forms.NumberInput(attrs={'class': 'form-control  remise_globale-input' ,'min': '0', 'max': '100'})
    )


class DevisForm(forms.ModelForm):
    class Meta:
        model = Devis
        fields = ['produit', 'quantite', 'prix_unitaire', 'remise_specifique',  'total']

    produit = forms.ModelChoiceField(
        queryset=Produits.objects.filter(lots__quantite__gt=0),
        required=True,
        label="Produit",
        widget=forms.Select(attrs={'class': 'form-control quantite-select'})
    )
    quantite = forms.IntegerField(
        min_value=1, required=True, label="Quantité",
        widget=forms.NumberInput(attrs={'class': 'form-control quantite-input '})
    )
    prix_unitaire = forms.DecimalField(
        max_digits=10, decimal_places=2, required=True,
        label="Prix unitaire",
        widget=forms.NumberInput(attrs={'class': 'form-control prix_unitaire-input'})
    )
    remise_specifique = forms.DecimalField(
        max_digits=5, decimal_places=2, required=False, initial=0,
        label="Remise spécifique",
        widget=forms.NumberInput(attrs={'class': 'form-control remise_specifique-input ' , 'min': '0', 'max': '100'})
    )
    

    def clean(self):
            cleaned_data = super().clean()
            produit = cleaned_data.get('produit')
            quantite = cleaned_data.get('quantite') or 0
            prix_unitaire = cleaned_data.get('prix_unitaire') or Decimal(0)
            remise_specifique = cleaned_data.get('remise_specifique') or Decimal(0)

            # Vérifications sécurisées
            if produit:
                stock_lot = StockLot.objects.filter(produit=produit).first()
                if stock_lot and stock_lot.quantite < quantite:
                    raise forms.ValidationError(f"Il n'y a pas assez de stock pour le produit {produit.name}.")

            if quantite <= 0:
                raise forms.ValidationError("La quantité doit être positive.")
            if prix_unitaire <= 0:
                raise forms.ValidationError("Le prix unitaire doit être positif.")
            if remise_specifique < 0 or remise_specifique > 100:
                raise forms.ValidationError("La remise spécifique doit être comprise entre 0 et 100.")

            return cleaned_data

            
# formulaire de vente
# class Ajoutvente(forms.ModelForm):
    
   
#     customer = forms.CharField(max_length=100)
#     quantite = forms.IntegerField(min_value=1)
#     remise = forms.IntegerField(min_value=0, max_value=100, required=False, initial=0)  # Remise en pourcentage

    
    
#     class Meta:
    
#         model = Vente
#         fields = ['quantite', 'customer','remise']
        
#         widgets = {
#             'customer': forms.TextInput(
#                 attrs={
#                     'placeholder':"Le nom du client",
#                 'class': 'forms-control'
#                  }
#             ),
#             'quantite': forms.TextInput(
#                 attrs={
#                     'placeholder':"La quantité",
#                 'class': 'forms-control'
#                  }
#             ),
            
#         }
        
#     def clean_remise(self):
#         remise = self.cleaned_data.get('remise', 0)
#         if remise < 0 or remise > 100:
#             raise forms.ValidationError("La remise doit être entre 0 et 100.")
#         return remise
        
        


# class FactureClientForm(forms.ModelForm):
#     class Meta:
#         model = Facture_client
#         fields = ['customer']
        
# class LigneFactureForm(forms.ModelForm):
#     class Meta:
#         model = LigneFacture
#         fields = ['produit', 'quantite', 'remise']

#     prix_unitaire = forms.DecimalField(widget=forms.NumberInput(attrs={'readonly': 'readonly'}))

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Initialiser le prix unitaire selon le produit sélectionné
#         if 'produit' in self.data:
#             try:
#                 produit_id = int(self.data.get('produit'))
#                 produit = Produits.objects.get(id=produit_id)
#                 self.fields['prix_unitaire'].initial = produit.price
#             except (ValueError, Produits.DoesNotExist):
#                 pass

# class AjoutA(forms.ModelForm):
    
#     quantite = forms.IntegerField(
#         help_text='Veillez entrez la quantité du produit',
#         required=True
#     )
#     date_achat = forms.DateField(
#         help_text='Veillez entrez la date achat',
#         input_formats=['%Y-%m-%d'],
#         required=True,
#          widget = forms.DateInput(
#                 attrs={ 
#                 'class': 'forms-control',
#                 'type': 'date'})
#     )
#     date_expiration = forms.DateField(
#         help_text='Veillez entrez la date expiration',
#         required=True,
#         widget = forms.DateInput(
#                 attrs={ 
#                 'class': 'forms-control',
#                 'type': 'date'})
        
       
#     )
#     fournisseur = forms.CharField(
#         help_text='Veillez entrez le nom du fournisseur',
#         required=True,
#         max_length=5000
#     )
#     price = forms.IntegerField(
#         help_text='Veillez entrez le prix du produit',
#         required=True,
      
#     )
    
#     class Meta:
    
#         model = ProduitsAchat
#         fields = ['quantite', 'fournisseur','date_achat']
        
#         widgets = {
#             'quantite': forms.NumberInput(
#                 attrs={
#                     'placeholder':"Le quantite achete",
#                 'class': 'forms-control'
#                  }
#             ),
#             'fournisseur': forms.TextInput(
#                 attrs={
#                     'placeholder':"Le nom et adresse du fournisseur",
#                 'class': 'forms-control'
#                  }
#             ),
#             'date_achat': forms.DateInput(
#                 attrs={
#                     'placeholder':"Le nom et adresse du fournisseur",
#                 'class': 'forms-control',
#                 'type':'date'
#                  }
#             ),
            
#         }
        
#formulaire d'achat


# class   AjoutA(ModelForm):
    
#     class Meta:
#         model = ProduitsAchat
#         fields = [
#             'name','category','price','quantite','description', 'date_expiration','date_achat','fournisseur'
#         ]
        
#         widgets = {
#             'name': forms.Select(
#                 attrs={
#                     'placeholder':'Selectionné un produit',
#                     'class' :'form-control'
#                 }
#             ),
            
#             'category': forms.Select(
#                 attrs={
#                     'class':'form-control'
#                 }
#             ),
            
#             'price' : forms.NumberInput(
#                 attrs={
#                     'placeholder': 'Entrez le prix du produit',
#                     'class':'form-control'
#                 }
#             ),
            
#             'quantite': forms.NumberInput(
#                 attrs= {
#                     'placeholder': 'Entrez la quantité du produit',
#                     'class':'form-control'
#                 }
#             ),
            
#             'description': forms.Textarea(
#                 attrs={
#                     'placeholder': 'Description  du produit',
#                     'class':'form-control',
#                     'rows': 4}
#             ), 
            
#             'date_expiration': forms.DateInput(
#                 attrs ={
#                     'placeholder': 'Date d\'expiration',
#                     'class':'form-control',
#                     'type':'date'
#                 }
                
#             ),
#             'date_achat': forms.DateInput(
#                 attrs ={
#                     'placeholder': 'Date d\'achat',
#                     'class':'form-control',
#                     'type':'date'
#                 }
#             ),
#             'fournisseur': forms.Textarea(
#                 attrs={
#                     'placeholder':'le nom et adresse du fournisseur',
#                     'class' :'form-control',
#                     'rows': 2}
#             )
            
#         }

#         def __init__(self, *args, **kwargs):
            
#             super(ProduitsAchat, self).__init__(*args,**kwargs)
            
#             self.fields['name'].error_messages = {
#                 'required': 'Le nom du produit est obligatoire',
#                 'invalid': 'Veuillez renseigner un nom valide'
#             }
#             self.fields['category'].error_messages = {
#                 'required': 'La categorie du produit est obligatoire',
#                 'invalid': 'Veuillez selectionner une categorie  valide'
#             }
#             self.fields['price'].error_messages = {
#                 'required': 'le prix du produit est obligatoire',
#                 'invalid': 'Veuillez entrer un prix valide'
#             }
#             self.fields['quantite'].error_messages = {
#                 'required': 'la quantité du produit est obligatoire',
#                 'invalid': 'Veuillez entrer une quantité valide'
#             }
#             self.fields['description'].error_messages = {
#                 'required': 'la description du produit est obligatoire',
#                 'invalid': 'Veuillez entrer une description valide'
#             }
#             self.fields['fournisseur'].error_messages = {
#                 'required': 'Nom et adresse du  fournisseur est obligatoire',
#                 'invalid': 'Veuillez entrer un non valide'
#             }
#             self.fields['date_expiration'].error_messages = {
#                 'required': 'la date expiraion du produit est obligatoire',
#                 'invalid': 'Veuillez entrer une date valide '
#             }
#             self.fields['date_achat'].error_messages = {
#                 'required': 'la date achat du produit est obligatoire',
#                 'invalid': 'Veuillez entrer une date valide '
#             }
                  
        
        