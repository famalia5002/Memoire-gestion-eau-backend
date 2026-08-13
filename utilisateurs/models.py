from django.contrib.auth.models import AbstractUser
from django.db import models

def chemin_photo(instance, filename):
    return f'photos/utilisateurs/{instance.username}/{filename}'

class Utilisateur(AbstractUser):
    ROLES = [
        ('super_admin', 'Super Administrateur'),
        ('admin_zone', 'Administrateur Zone'),
        ('client', 'Client'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLES,
        default='client'
    )
    zone = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    telephone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    adresse = models.TextField(
        blank=True,
        null=True
    )
    latitude = models.FloatField(
        blank=True,
        null=True
    )
    longitude = models.FloatField(
        blank=True,
        null=True
    )
    
    photo = models.ImageField(
        upload_to=chemin_photo,
        blank=True,
        null=True
    )

    TYPE_CLIENT = [
        ('proprietaire', 'Propriétaire'),
        ('locataire', 'Locataire'),
    ]

    STATUT_ABONNEMENT = [
        ('actif', 'Actif'),
        ('en_traitement', 'En cours de traitement'),
        ('suspendu', 'Suspendu'),
        ('resilie', 'Résilié'),
    ]

    type_client = models.CharField(
        max_length=20,
        choices=TYPE_CLIENT,
        blank=True, null=True
    )
    statut_abonnement = models.CharField(
        max_length=20,
        choices=STATUT_ABONNEMENT,
        default='actif'
    )
    # Documents fournis
    doc_cin = models.BooleanField(default=False)
    doc_attestation = models.BooleanField(default=False)
    doc_contrat_location = models.BooleanField(default=False)
    doc_convention = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def est_super_admin(self):
        return self.role == 'super_admin'

    @property
    def est_admin_zone(self):
        return self.role == 'admin_zone'

    @property
    def est_client(self):
        return self.role == 'client'

    @property
    def nom_complet(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"