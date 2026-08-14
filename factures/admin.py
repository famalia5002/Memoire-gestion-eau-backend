from django.contrib import admin
from .models import Facture, Tarif

@admin.register(Tarif)
class TarifAdmin(admin.ModelAdmin):
    list_display = [
        'type_zone', 'type_abonne',
        'prix_ts', 'prix_tp', 'prix_td',
        'date_debut', 'actif'
    ]
    list_filter = ['type_zone', 'type_abonne', 'actif']
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