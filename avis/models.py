from django.db import models

# Create your models here.
class Avis(models.Model):
    STATUTS = [
        ('en_attente', 'En attente'),
        ('traite', 'Traité'),
    ]

    client = models.ForeignKey(
        'utilisateurs.Utilisateur',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'client'},
        related_name='avis'
    )
    note = models.IntegerField()
    commentaire = models.TextField()
    date_avis = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=20,
        choices=STATUTS,
        default='en_attente'
    )
   
    reponse_admin = models.TextField(
        blank=True,
        null=True
    )
    date_reponse = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Avis {self.client} - {self.note} étoiles"

    class Meta:
        ordering = ['-date_avis']