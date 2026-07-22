from rest_framework import serializers
from .models import Consommation, Index
from compteurs.serializers import CompteurSerializer

class ConsommationSerializer(serializers.ModelSerializer):
    compteur_detail = CompteurSerializer(
        source='compteur',
        read_only=True
    )

    class Meta:
        model = Consommation
        fields = [
            'id', 'compteur', 'compteur_detail',
            'volume', 'date_heure'
        ]

class IndexSerializer(serializers.ModelSerializer):
    compteur_detail = CompteurSerializer(
        source='compteur',
        read_only=True
    )

    class Meta:
        model = Index
        fields = [
            'id', 'compteur', 'compteur_detail',
            'valeur_index', 'date_releve'
        ]