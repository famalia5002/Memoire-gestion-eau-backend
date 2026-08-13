from django.contrib import admin

# Register your models here.
from .models import DemandeAbonnement

@admin.register(DemandeAbonnement)
class DemandeAdmin(admin.ModelAdmin):
    list_display = [
        'nom', 'prenom', 'email', 'zone',
        'type_client', 'statut', 'date_demande'
    ]
    list_filter = ['statut', 'zone', 'type_client']
    search_fields = ['nom', 'prenom', 'email']
    ordering = ['-date_demande']
