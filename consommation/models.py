from django.db import models

from compteurs.models import Compteur
# Create your models here.


class Consommation(models.Model):
    compteur = models.ForeignKey(
        Compteur,
        on_delete=models.CASCADE,
        related_name='consommations'
    )
    volume = models.FloatField()
    date_heure = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.compteur} - {self.volume}L"

    class Meta:
        ordering = ['-date_heure']

class Index(models.Model):
    compteur = models.ForeignKey(
        Compteur,
        on_delete=models.CASCADE,
        related_name='index'
    )
    valeur_index = models.FloatField()
    date_releve = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Index {self.compteur} - {self.valeur_index}m³"

    class Meta:
        ordering = ['-date_releve']
