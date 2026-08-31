from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListeFacturesView.as_view(), name='liste_factures'),
    path('<int:pk>/', views.DetailFactureView.as_view(), name='detail_facture'),
    path('<int:facture_id>/payer/', views.PayerFactureView.as_view(), name='payer_facture'),
    path('tarifs/', views.TarifView.as_view(), name='tarifs'),
    path('generer/', views.GenererFactureView.as_view(), name='generer_facture'),
    path('generer-toutes/', views.GenererToutesFacturesView.as_view(), name='generer_toutes'),
    path('<int:facture_id>/detail/', views.FacturePDFView.as_view(), name='facture_detail'),
    path('<int:facture_id>/envoyer-pdf/', views.EnvoyerPDFView.as_view(), name='envoyer_pdf'),


]