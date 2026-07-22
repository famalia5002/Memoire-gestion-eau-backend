from django.urls import path
from . import views

urlpatterns = [
    # ESP32 envoie les données ici
    path('enregistrer/', views.EnregistrerConsommationView.as_view(), name='enregistrer_consommation'),
    
    # Client consulte sa consommation
    path('', views.ConsommationClientView.as_view(), name='consommation_client'),
    
    # Index du compteur
    path('index/<int:compteur_id>/', views.IndexCompteurView.as_view(), name='index_compteur'),
]