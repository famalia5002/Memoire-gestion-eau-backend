from django.contrib import admin
from django.contrib import admin
from .models import Avis

# Register your models here.

@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = [
        'client', 'note', 'commentaire',
        'date_avis', 'statut'
    ]
    list_filter = ['note', 'statut']
    search_fields = ['client__username']
    ordering = ['-date_avis']
