from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Utilisateur
from .serializers import (
    UtilisateurSerializer,
    CreerUtilisateurSerializer,
    ModifierMotDePasseSerializer
)

class ConnexionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        utilisateur = authenticate(
            username=username,
            password=password
        )

        if utilisateur:
            refresh = RefreshToken.for_user(utilisateur)
            return Response({
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'role': utilisateur.role,
                'id': utilisateur.id,
                'nom': utilisateur.nom_complet,
                'zone': utilisateur.zone,
            })
        
        return Response(
            {'erreur': 'Identifiants incorrects'},
            status=status.HTTP_401_UNAUTHORIZED
        )

class DeconnexionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'message': 'Déconnexion réussie'},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {'erreur': 'Token invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )

class ListeClientsView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UtilisateurSerializer

    def get_queryset(self):
        user = self.request.user
        # Super admin voit tous les clients
        if user.role == 'super_admin':
            return Utilisateur.objects.filter(role='client')
        # Admin zone voit seulement les clients de sa zone
        return Utilisateur.objects.filter(
            role='client',
            zone=user.zone
        )

    def create(self, request, *args, **kwargs):
        serializer = CreerUtilisateurSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(role='client')
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class DetailClientView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UtilisateurSerializer
    queryset = Utilisateur.objects.filter(role='client')

class ListeAdminsView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UtilisateurSerializer

    def get_queryset(self):
        # Seul le super admin peut voir les admins zones
        if self.request.user.role == 'super_admin':
            return Utilisateur.objects.filter(role='admin_zone')
        return Utilisateur.objects.none()

    def create(self, request, *args, **kwargs):
        if request.user.role != 'super_admin':
            return Response(
                {'erreur': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = CreerUtilisateurSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(role='admin_zone')
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class ProfilView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UtilisateurSerializer

    def get_object(self):
        return self.request.user