from django.contrib import admin
from django.contrib import admin
from .models import Alerte, Commande
# Register your models here.


@admin.register(Alerte)
class AlerteAdmin(admin.ModelAdmin):
    list_display = [
        'compteur', 'type_alerte',
        'statut', 'date', 'date_resolution'
    ]
    list_filter = ['type_alerte', 'statut']
    search_fields = ['compteur__numero_compteur']
    ordering = ['-date']

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = [
        'compteur', 'action', 'statut',
        'effectuee_par', 'date_commande'
    ]
    list_filter = ['action', 'statut']
    search_fields = ['compteur__numero_compteur']
    ordering = ['-date_commande']
