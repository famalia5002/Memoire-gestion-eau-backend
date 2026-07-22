from rest_framework import serializers
from .models import Alerte, Commande
from compteurs.serializers import CompteurSerializer
from utilisateurs.serializers import UtilisateurSerializer

class AlerteSerializer(serializers.ModelSerializer):
    compteur_detail = CompteurSerializer(
        source='compteur',
        read_only=True
    )

    class Meta:
        model = Alerte
        fields = [
            'id', 'compteur', 'compteur_detail',
            'type_alerte', 'statut',
            'date', 'date_resolution'
        ]

class CommandeSerializer(serializers.ModelSerializer):
    compteur_detail = CompteurSerializer(
        source='compteur',
        read_only=True
    )
    admin_detail = UtilisateurSerializer(
        source='effectuee_par',
        read_only=True
    )

    class Meta:
        model = Commande
        fields = [
            'id', 'compteur', 'compteur_detail',
            'action', 'statut', 'effectuee_par',
            'admin_detail', 'date_commande'
        ]