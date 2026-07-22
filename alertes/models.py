from django.db import models
from compteurs.models import Compteur
# Create your models here.


class Alerte(models.Model):
    TYPES = [
        ('fuite', 'Fuite probable'),
        ('surconsommation', 'Surconsommation'),
        ('deconnecte', 'Compteur déconnecté'),
    ]

    STATUTS = [
        ('en_cours', 'En cours'),
        ('resolue', 'Résolue'),
    ]

    compteur = models.ForeignKey(
        Compteur,
        on_delete=models.CASCADE,
        related_name='alertes'
    )
    type_alerte = models.CharField(max_length=20, choices=TYPES)
    statut = models.CharField(
        max_length=20,
        choices=STATUTS,
        default='en_cours'
    )
    date = models.DateTimeField(auto_now_add=True)
    date_resolution = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Alerte {self.type_alerte} - {self.compteur}"

    class Meta:
        ordering = ['-date']

class Commande(models.Model):
    ACTIONS = [
        ('ouvrir', 'Ouvrir vanne'),
        ('fermer', 'Fermer vanne'),
    ]

    STATUTS = [
        ('envoyee', 'Envoyée'),
        ('executee', 'Exécutée'),
        ('echouee', 'Échouée'),
    ]

    compteur = models.ForeignKey(
        Compteur,
        on_delete=models.CASCADE,
        related_name='commandes'
    )
    action = models.CharField(max_length=10, choices=ACTIONS)
    statut = models.CharField(
        max_length=10,
        choices=STATUTS,
        default='envoyee'
    )
    effectuee_par = models.ForeignKey(
        'utilisateurs.Utilisateur',
        on_delete=models.SET_NULL,
        null=True
    )
    date_commande = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande {self.action} - {self.compteur}"
