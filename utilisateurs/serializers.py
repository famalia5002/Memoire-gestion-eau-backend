from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Utilisateur

class UtilisateurSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    nom_complet = serializers.SerializerMethodField()

    class Meta:
        model = Utilisateur
        fields = [
            'id', 'username', 'email', 'first_name',
            'last_name', 'nom_complet', 'role', 'zone',
            'telephone', 'adresse', 'latitude', 'longitude',
            'photo', 'photo_url'
        ]
        extra_kwargs = {
            'photo': {'write_only': True}
        }

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None

    def get_nom_complet(self, obj):
        return obj.nom_complet

class CreerUtilisateurSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    class Meta:
        model = Utilisateur
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'role', 'zone', 'telephone',
            'adresse', 'latitude', 'longitude', 'photo'
        ]

    def create(self, validated_data):
        utilisateur = Utilisateur.objects.create_user(**validated_data)
        return utilisateur

class ModifierUtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = [
            'email', 'first_name', 'last_name',
            'telephone', 'adresse', 'zone',
            'latitude', 'longitude', 'photo'
        ]

class ModifierMotDePasseSerializer(serializers.Serializer):
    ancien_password = serializers.CharField(required=True)
    nouveau_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )