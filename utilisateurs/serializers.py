from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Utilisateur

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = [
            'id', 'username', 'email', 'first_name', 
            'last_name', 'role', 'zone', 'telephone',
            'adresse', 'latitude', 'longitude'
        ]

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
            'adresse', 'latitude', 'longitude'
        ]

    def create(self, validated_data):
        utilisateur = Utilisateur.objects.create_user(
            **validated_data
        )
        return utilisateur

class ModifierMotDePasseSerializer(serializers.Serializer):
    ancien_password = serializers.CharField(required=True)
    nouveau_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )