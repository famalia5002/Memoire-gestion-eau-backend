from django.db import models

class Tarif(models.Model):
    TYPES_ZONE = [
        ('assainie', 'Zone assainie'),
        ('non_assainie', 'Zone non assainie'),
    ]

    TYPES_ABONNE = [
        ('domestique_15mm', 'Domestique diamètre 15mm'),
        ('domestique_20mm', 'Domestique diamètre >= 20mm'),
        ('non_domestique', 'Non domestique'),
        ('maraicher', 'Maraîcher'),
    ]

    type_zone = models.CharField(
        max_length=20,
        choices=TYPES_ZONE,
        default='assainie'
    )
    type_abonne = models.CharField(
        max_length=20,
        choices=TYPES_ABONNE,
        default='domestique_15mm'
    )
    # Prix en FCFA/m³ TTC
    prix_ts = models.FloatField(
        default=202,
        help_text="Tranche sociale 0-20 m³ (FCFA/m³ TTC)"
    )
    prix_tp = models.FloatField(
        default=697.97,
        help_text="Tranche progressive 21-40 m³ (FCFA/m³ TTC)"
    )
    prix_td = models.FloatField(
        default=878.35,
        help_text="Tranche dissuasive >40 m³ (FCFA/m³ TTC)"
    )
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"Tarif {self.get_type_zone_display()} - {self.get_type_abonne_display()}"

    class Meta:
        verbose_name = "Tarif"
        verbose_name_plural = "Tarifs"


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
    volume_total = models.FloatField()  # en litres
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
    periode_debut = models.DateField(null=True, blank=True)
    periode_fin = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Facture {self.id} - {self.client} - {self.statut}"

    class Meta:
        ordering = ['-date_generation']