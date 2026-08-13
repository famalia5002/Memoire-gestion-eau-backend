from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListeDemandesView.as_view(), name='liste_demandes'),
    path('creer/', views.CreerDemandeView.as_view(), name='creer_demande'),
    path('<int:demande_id>/traiter/', views.TraiterDemandeView.as_view(), name='traiter_demande'),
]