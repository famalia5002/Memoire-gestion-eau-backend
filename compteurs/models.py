from django.db import models

# Create your models here.

class Compteur(models.Model):
    STATUTS = [
        ('disponible', 'Disponible'),
        ('attribue', 'Attribué'),
        ('en_panne', 'En panne'),
    ]

    ETAT_VANNE = [
        ('ouverte', 'Ouverte'),
        ('fermee', 'Fermée'),
    ]

    numero_compteur = models.CharField(max_length=50, unique=True)
    serie = models.CharField(max_length=100)
    statut = models.CharField(
        max_length=20,
        choices=STATUTS,
        default='disponible'
    )
    etat_vanne = models.CharField(
        max_length=10,
        choices=ETAT_VANNE,
        default='ouverte'
    )
    client = models.ForeignKey(
        'utilisateurs.Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'client'},
        related_name='compteurs'
    )
    date_installation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Compteur {self.numero_compteur}"

    class Meta:
        verbose_name = "Compteur"
        verbose_name_plural = "Compteurs"
