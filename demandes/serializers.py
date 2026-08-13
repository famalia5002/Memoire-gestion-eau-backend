from rest_framework import serializers
from .models import DemandeAbonnement
from utilisateurs.serializers import UtilisateurSerializer

class DemandeSerializer(serializers.ModelSerializer):
    traite_par_detail = UtilisateurSerializer(
        source='traite_par',
        read_only=True
    )
    photo_cin_url = serializers.SerializerMethodField()
    photo_attestation_url = serializers.SerializerMethodField()
    photo_contrat_url = serializers.SerializerMethodField()
    photo_convention_url = serializers.SerializerMethodField()

    class Meta:
        model = DemandeAbonnement
        fields = [
            'id', 'nom', 'prenom', 'email',
            'telephone', 'adresse', 'zone',
            'latitude', 'longitude', 'type_client',
            'photo_cin', 'photo_cin_url',
            'photo_attestation', 'photo_attestation_url',
            'photo_contrat', 'photo_contrat_url',
            'photo_convention', 'photo_convention_url',
            'statut', 'motif_refus',
            'date_demande', 'date_traitement',
            'traite_par', 'traite_par_detail'
        ]
        extra_kwargs = {
            'photo_cin': {'write_only': True},
            'photo_attestation': {'write_only': True},
            'photo_contrat': {'write_only': True},
            'photo_convention': {'write_only': True},
        }

    def get_photo_cin_url(self, obj):
        if obj.photo_cin:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo_cin.url)
        return None

    def get_photo_attestation_url(self, obj):
        if obj.photo_attestation:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo_attestation.url)
        return None

    def get_photo_contrat_url(self, obj):
        if obj.photo_contrat:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo_contrat.url)
        return None

    def get_photo_convention_url(self, obj):
        if obj.photo_convention:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo_convention.url)
        return None