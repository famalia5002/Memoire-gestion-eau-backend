from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListeCompteursView.as_view(), name='liste_compteurs'),
    path('<int:pk>/', views.DetailCompteurView.as_view(), name='detail_compteur'),
    path('<int:compteur_id>/associer/', views.AssocierCompteurClientView.as_view(), name='associer_compteur'),
    path('<int:compteur_id>/desassocier/', views.DesassocierCompteurView.as_view(), name='desassocier_compteur'),
    path('<int:compteur_id>/vanne/', views.ControlerVanneView.as_view(), name='controler_vanne'),
    path('<int:compteur_id>/fermer-vanne-client/', views.FermerVanneClientView.as_view(), name='fermer_vanne_client'),
    path('<int:compteur_id>/rouvrir-vanne-client/', views.RouvrirVanneClientView.as_view(), name='rouvrir_vanne_client'),
]