from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListeFacturesView.as_view(), name='liste_factures'),
    path('<int:pk>/', views.DetailFactureView.as_view(), name='detail_facture'),
    path('<int:facture_id>/payer/', views.PayerFactureView.as_view(), name='payer_facture'),
    path('tarifs/', views.TarifView.as_view(), name='tarifs'),
]