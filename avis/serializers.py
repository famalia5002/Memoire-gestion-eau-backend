from rest_framework import serializers
from .models import Avis
from utilisateurs.serializers import UtilisateurSerializer

class AvisSerializer(serializers.ModelSerializer):
    client_detail = UtilisateurSerializer(
        source='client',
        read_only=True
    )

    class Meta:
        model = Avis
        fields = [
            'id', 'client', 'client_detail',
            'note', 'commentaire',
            'date_avis', 'statut'
        ]