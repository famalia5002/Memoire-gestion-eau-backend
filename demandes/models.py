from django.db import models

# Create your models here.
class DemandeAbonnement(models.Model):
    STATUTS = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
    ]

    TYPE_CLIENT = [
        ('proprietaire', 'Propriétaire'),
        ('locataire', 'Locataire'),
    ]

    # Infos personnelles
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    adresse = models.TextField()
    zone = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    type_client = models.CharField(
        max_length=20,
        choices=TYPE_CLIENT,
        default='proprietaire'
    )

    # Documents uploadés
    photo_cin = models.FileField(
        upload_to='demandes/cin/',
        null=True, blank=True
    )
    photo_attestation = models.FileField(
        upload_to='demandes/attestations/',
        null=True, blank=True
    )
    photo_contrat = models.FileField(
        upload_to='demandes/contrats/',
        null=True, blank=True
    )
    photo_convention = models.FileField(
        upload_to='demandes/conventions/',
        null=True, blank=True
    )

    # Statut et traitement
    statut = models.CharField(
        max_length=20,
        choices=STATUTS,
        default='en_attente'
    )
    motif_refus = models.TextField(null=True, blank=True)
    date_demande = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(
        'utilisateurs.Utilisateur',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='demandes_traitees'
    )

    def __str__(self):
        return f"Demande {self.nom} {self.prenom} - {self.statut}"

    class Meta:
        ordering = ['-date_demande']
        verbose_name = "Demande d'abonnement"
        verbose_name_plural = "Demandes d'abonnement"
