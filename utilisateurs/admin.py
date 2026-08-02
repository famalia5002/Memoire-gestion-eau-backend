from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur

# Register your models here.

@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = [
        'username', 'email', 'first_name', 
        'last_name', 'role', 'zone', 'telephone'
    ]
    list_filter = ['role', 'zone']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': (
                'role', 'zone', 'telephone',
                'adresse', 'latitude', 'longitude','photo'
            )
        }),
    )
