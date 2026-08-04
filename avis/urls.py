from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListeAvisView.as_view(), name='liste_avis'),
    path('<int:pk>/', views.DetailAvisView.as_view(), name='detail_avis'),
    path('<int:avis_id>/repondre/', views.RepondreAvisView.as_view(), name='repondre_avis'),      
    path('<int:avis_id>/traiter/', views.MarquerTraiteView.as_view(), name='traiter_avis'), 
]