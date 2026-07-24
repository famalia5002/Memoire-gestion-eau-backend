from django.contrib import admin
from django.contrib import admin
from .models import Compteur
# Register your models here.

@admin.register(Compteur)
class CompteurAdmin(admin.ModelAdmin):
    list_display = [
        'numero_compteur', 'serie', 
        'statut', 'etat_vanne', 
        'client', 'date_installation'
    ]
    list_filter = ['statut', 'etat_vanne']
    search_fields = ['numero_compteur', 'serie']
    ordering = ['numero_compteur']