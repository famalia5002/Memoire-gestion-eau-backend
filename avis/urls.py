from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListeAvisView.as_view(), name='liste_avis'),
    path('<int:pk>/', views.DetailAvisView.as_view(), name='detail_avis'),
]