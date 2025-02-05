from django.urls import path
from .views import *



urlpatterns = [
    
    
    
    path ("connecter/", connecter_compte, name='login'),
    path ("creation/", creation_compte, name='creation'),
    path ("verification/", verification_Mail, name='verification'),
    path ("confirmation/", confirmation_code, name='confirmation_code'),
    path('modification-code/<int:uid>/', Changement_Code, name="modifierCode"),
    path('creation-utilisateur-secondaire/',creation_utilisateur_secondaire, name='creation_utilisateur_secondaire'),
    path('liste-utilisateurs/', liste_utilisateurs, name='liste_utilisateurs'),
    path('modifier-utilisateur/<int:utilisateur_id>/', modifier_utilisateur, name='modifier_utilisateur'),
    path('supprimer-utilisateur/<int:utilisateur_id>/', supprimer_utilisateur, name='supprimer_utilisateur'),
    path('deconnection/', Deconnection, name="deconnection"),
    

]