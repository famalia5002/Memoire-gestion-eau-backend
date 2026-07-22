from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListeAlertesView.as_view(), name='liste_alertes'),
    path('<int:alerte_id>/resoudre/', views.ResoudreAlerteView.as_view(), name='resoudre_alerte'),
    path('commandes/', views.ListeCommandesView.as_view(), name='liste_commandes'),
]