from django.contrib import admin
from django.contrib import admin
from .models import Consommation, Index
# Register your models here.


@admin.register(Consommation)
class ConsommationAdmin(admin.ModelAdmin):
    list_display = [
        'compteur', 'volume', 'date_heure'
    ]
    list_filter = ['date_heure']
    search_fields = ['compteur__numero_compteur']
    ordering = ['-date_heure']

@admin.register(Index)
class IndexAdmin(admin.ModelAdmin):
    list_display = [
        'compteur', 'valeur_index', 'date_releve'
    ]
    list_filter = ['date_releve']
    search_fields = ['compteur__numero_compteur']
    ordering = ['-date_releve']
