from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
   
    #path('',home,name='home'),
    path('dashboardAdmin/', admin_account_dashboard, name='admin_dashboard'),
    path('contact/', views.contact_view, name='contact'),
    path('acc/', Acc, name='acc'),
    path('acceuil/', Acceuil, name='acceuil'),
    path('ajouter-categorie/', CategoryCreateView.as_view(), name='ajouter_categorie'),
    path('categories/<int:pk>/modifier/', CategoryEditView.as_view(), name='category_edit'),
    path('categories/<int:pk>/supprimer/', CategoryDeleteView.as_view(), name='category_delete'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('parametre/', foncParametre.as_view(), name='parametre'),
    path( 'produit/', affichage.as_view(), name='home'),
    path( 'produits/', ProductList.as_view(), name='produits'),
    path( 'Achat/', affichageAchat.as_view(), name='Achat'),
    path( 'AchatProduits/<int:id>/', AchatProduits, name='AchatProduits'),
    path( 'ajout/', AjoutProduits.as_view(), name='ajout'),
    #path('modification/<int:id>/', modifier,name='modifier'),
    path('modification/<uuid:uuid>/<slug:slug>/', Update_donnees.as_view(), name='modifier'),
    #path('supprimer/<int:id>/', supprimer, name="supprimer"),
    path('detail/<uuid:uuid>/<slug:slug>/', edit.as_view(),name='detail'),
    path('detailstock/<uuid:uuid>/<slug:slug>/', editstock.as_view(),name='detailstock'),
    path('delete/<uuid:uuid>/<slug:slug>/', delete.as_view(),name='delete'),
    #path('ajout/',ajout_donnees,name='ajout'),

    path('recherche/', recherche, name='recherche'),
    path('ajoutvente/', VenteProduits, name='ajoutvente'),
    path('enregistrement-recu/<int:id>/', Saverecu, name='saverecu'),
    path('facture/<int:facture_id>/', afficher_facture, name='facture'),
    path('historique-ventes/', views.historique_ventes, name='historique_ventes'),
    path('details-facture/<int:facture_id>/', views.details_facture, name='details_facture'),
    
    path('rechercher-facture/', views.rechercher_facture, name='rechercher_facture'),
    path('rechercher-factureAchat/', views.rechercher_factureAchat, name='rechercher_factureAchat'),
    path('product-details/<int:produit_id>/', get_product_details, name='get_product_details'),
    
    path('creer-achat/', creer_achat, name='creer_achat'),
    path('historique-achats/', historique_achats, name='historique_achats'),
    path('historique/achats/supprimer/<int:facture_pk>/', views.supprimer_facture_achat, name='supprimer_facture_achat'),
    path('historique/vente/supprimer/<int:facture_pk>/', views.supprimer_facture_vente, name='supprimer_facture_vente'),
    path('historique/devis/supprimer/<int:devis_pk>/', views.supprimer_facture_devis, name='supprimer_facture_devis'),
    path('historique/commande/supprimer/<int:bon_pk>/', views.supprimer_facture_commande, name='supprimer_facture_commande'),
    path('details-achat/<int:facture_pk>/', details_facture_achat, name='details_achat'),
    path('modifier-lots/<uuid:uuid>/<slug:slug>/', views.modifier_lots_produit, name='modifier_lots_produit'),
    path('supprimer_lot/<int:lot_id>/', views.supprimer_lot, name='supprimer_lot'),
    path('annuler-modification/', views.annuler_modification, name='annuler_modification'),
    path('recherche-stock/', views.rechercher_stock, name='recherche_stock'),
    path('recherche-rechercher_bon_commande/', views.rechercher_bon_commande, name='rechercher_bon_commande'),
    path('recherche-devis/', views.recherche_devis, name='recherche_devis'),
    path('rapports/', views.rapports_statistiques, name='rapports_statistiques'),
    path('notifications/', views.verifier_notifications, name='notifications'),
    path('notifications/marquer-comme-lues/', views.marquer_notifications_lues, name='marquer_notifications_lues'),
    path('creer-commande/', creer_bon_de_commande, name='creer_commande'),
    path('historique-commande/', historique_commande, name='historique_commande'),
   
    path('historique-devis/', historique_devis, name='historique_devis'),
    path('bon-commande/<int:commandefac_id>/', views.afficher_bon_commande, name='afficher_bon_commande'),
    path('devis/<int:devisfac_id>/', views.afficher_deviss, name='afficher_devis'),
   
    path('details_bon_commande/<int:bon_id>/', views.afficher_details_bon_commande, name='details_bon_commande'),
    path('create-devis/', views.creer_devis, name='create_devis'),
    path('devis/<int:devis_id>/', views.devis_detail, name='devis_detail'),
   
    
    path("payment/checkout/", paypal_checkout, name="paypal_checkout"),
    path("payment/success/", payment_success, name="payment_success"),
    path("payment/cancel/", payment_cancel, name="payment_cancel"),
    # path('capture-paypal-order/<str:order_id>/', capture_paypal_order, name="capture_paypal_order"),
     path('webhook/paypal/', paypal_webhook, name='paypal_webhook'),
    path("api/verifier-abonnement/", verifier_abonnement, name="verifier_abonnement"),
    path("api/verifier-essai/", verifier_essai_gratuit, name="verifier_essai_gratuit"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

