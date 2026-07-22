from django.db import models

# Create your models here.
class Tarif(models.Model):
    TYPES = [
        ('eau_potable', 'Eau potable'),
        ('industrielle', 'Industrielle'),
    ]

    type_eau = models.CharField(max_length=20, choices=TYPES)
    prix_litre = models.FloatField()
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Tarif {self.type_eau} - {self.prix_litre} FCFA/L"

class Facture(models.Model):
    STATUTS = [
        ('en_attente', 'En attente'),
        ('payee', 'Payée'),
        ('en_retard', 'En retard'),
    ]

    MODES_PAIEMENT = [
        ('agence', 'Agence'),
        ('wave', 'Wave'),
        ('orange_money', 'Orange Money'),
    ]

    client = models.ForeignKey(
        'utilisateurs.Utilisateur',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'client'},
        related_name='factures'
    )
    tarif = models.ForeignKey(
        Tarif,
        on_delete=models.SET_NULL,
        null=True
    )
    volume_total = models.FloatField()
    montant = models.FloatField()
    statut = models.CharField(
        max_length=20,
        choices=STATUTS,
        default='en_attente'
    )
    mode_paiement = models.CharField(
        max_length=20,
        choices=MODES_PAIEMENT,
        null=True,
        blank=True
    )
    date_generation = models.DateTimeField(auto_now_add=True)
    date_limite = models.DateField()

    def __str__(self):
        return f"Facture {self.id} - {self.client} - {self.statut}"

    class Meta:
        ordering = ['-date_generation']