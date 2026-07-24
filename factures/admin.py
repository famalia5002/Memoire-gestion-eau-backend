from django.contrib import admin
from django.contrib import admin
from .models import Facture, Tarif

# Register your models here.

@admin.register(Tarif)
class TarifAdmin(admin.ModelAdmin):
    list_display = [
        'type_eau', 'prix_litre',
        'date_debut', 'date_fin'
    ]
    ordering = ['-date_debut']

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'client', 'volume_total',
        'montant', 'statut',
        'mode_paiement', 'date_generation',
        'date_limite'
    ]
    list_filter = ['statut', 'mode_paiement']
    search_fields = ['client__username', 'client__email']
    ordering = ['-date_generation']
