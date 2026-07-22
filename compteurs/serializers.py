from rest_framework import serializers
from .models import Compteur
from utilisateurs.serializers import UtilisateurSerializer

class CompteurSerializer(serializers.ModelSerializer):
    client_detail = UtilisateurSerializer(
        source='client', 
        read_only=True
    )

    class Meta:
        model = Compteur
        fields = [
            'id', 'numero_compteur', 'serie', 
            'statut', 'etat_vanne', 'client',
            'client_detail', 'date_installation'
        ]