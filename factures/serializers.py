from rest_framework import serializers
from .models import Facture, Tarif
from utilisateurs.serializers import UtilisateurSerializer

class TarifSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarif
        fields = '__all__'

class FactureSerializer(serializers.ModelSerializer):
    client_detail = UtilisateurSerializer(
        source='client',
        read_only=True
    )
    tarif_detail = TarifSerializer(
        source='tarif',
        read_only=True
    )

    class Meta:
        model = Facture
        fields = [
            'id', 'client', 'client_detail',
            'tarif', 'tarif_detail', 'volume_total',
            'montant', 'statut', 'mode_paiement',
            'date_generation', 'date_limite'
        ]