from django import forms
from .models import UtilisateurProfil

class PhotoProfilForm(forms.ModelForm):
    class Meta:
        model = UtilisateurProfil
        fields = ['photo_profil']
