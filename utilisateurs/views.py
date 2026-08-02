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
      ModifierUtilisateurSerializer,
    ModifierMotDePasseSerializer
)
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser

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

            # Construire l'URL de la photo
            photo_url = None
            if utilisateur.photo:
                photo_url = request.build_absolute_uri(
                    utilisateur.photo.url
                )

            return Response({
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'role': utilisateur.role,
                'id': utilisateur.id,
                'nom': utilisateur.nom_complet,
                'username': utilisateur.username,
                'zone': utilisateur.zone,
                'email': utilisateur.email,
                'telephone': utilisateur.telephone,
                'photo_url': photo_url,  # ← photo incluse
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
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Utilisateur.objects.filter(role='client')
        return Utilisateur.objects.filter(
            role='client',
            zone=user.zone
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        serializer = CreerUtilisateurSerializer(
            data=request.data,
            context={'request': request}
        )
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
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ModifierProfilView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def put(self, request):
        serializer = ModifierUtilisateurSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            # Retourner les données mises à jour
            user_serializer = UtilisateurSerializer(
                request.user,
                context={'request': request}
            )
            return Response({
                'message': 'Profil mis à jour avec succès',
                'user': user_serializer.data
            })
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
class ModifierPhotoView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        photo = request.FILES.get('photo')
        if not photo:
            return Response(
                {'erreur': 'Aucune photo fournie'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Supprimer ancienne photo
        if request.user.photo:
            import os
            if os.path.exists(request.user.photo.path):
                os.remove(request.user.photo.path)

        request.user.photo = photo
        request.user.save()

        photo_url = request.build_absolute_uri(request.user.photo.url)

        return Response({
            'message': 'Photo mise à jour avec succès',
            'photo_url': photo_url
        })

class ChangerMotDePasseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ancien = request.data.get('ancien_password')
        nouveau = request.data.get('nouveau_password')
        confirmer = request.data.get('confirmer_password')

        # Vérifier ancien mot de passe
        if not request.user.check_password(ancien):
            return Response(
                {'erreur': 'Ancien mot de passe incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier confirmation
        if nouveau != confirmer:
            return Response(
                {'erreur': 'Les mots de passe ne correspondent pas'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier longueur
        if len(nouveau) < 8:
            return Response(
                {'erreur': 'Le mot de passe doit contenir au moins 8 caractères'},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.set_password(nouveau)
        request.user.save()

        return Response({
            'message': 'Mot de passe changé avec succès !'
        })

class DetailAdminView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UtilisateurSerializer
    queryset = Utilisateur.objects.filter(role='admin_zone')
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'super_admin':
            return Response(
                {'erreur': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)