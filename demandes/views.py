from django.shortcuts import render

# Create your views here.

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone
from .models import DemandeAbonnement
from .serializers import DemandeSerializer
from .email_utils import envoyer_email_bienvenue

class ListeDemandesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DemandeSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return DemandeAbonnement.objects.all()
        # Admin zone voit les demandes de sa zone
        return DemandeAbonnement.objects.filter(zone=user.zone)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class CreerDemandeView(APIView):
    # AllowAny car le client n'est pas encore inscrit
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = DemandeSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Demande soumise avec succès ! Vous serez contacté sous 48h.',
                'demande': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class TraiterDemandeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, demande_id):
        try:
            demande = DemandeAbonnement.objects.get(id=demande_id)
            action = request.data.get('action')
            motif = request.data.get('motif_refus', '')

            # Vérifier action valide
            if action not in ['accepter', 'refuser', 'accepter_manuel']:
                return Response(
                    {'erreur': 'Action invalide'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ===== REFUSER =====
            if action == 'refuser':
                if not motif:
                    return Response(
                        {'erreur': 'Le motif du refus est obligatoire'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                demande.statut = 'refusee'
                demande.motif_refus = motif
                demande.date_traitement = timezone.now()
                demande.traite_par = request.user
                demande.save()

                return Response({
                    'message': 'Demande refusée avec succès'
                })

            # ===== ACCEPTER MANUEL =====
            if action == 'accepter_manuel':
                from utilisateurs.models import Utilisateur

                # Récupérer le mot de passe temporaire
                password_temp = request.data.get('password_temporaire', '')

                try:
                    # Chercher le client créé avec cet email
                    client = Utilisateur.objects.filter(
                        email=demande.email,
                        role='client'
                    ).last()  # ← prendre le plus récent

                    # Envoyer email si client trouvé et mot de passe fourni
                    if client and password_temp:
                        envoyer_email_bienvenue(client, password_temp)
                        print(f"Email envoyé à {client.email}")
                    else:
                        print(f"Client non trouvé ou mot de passe manquant")

                except Exception as e:
                   print(f"Erreur email: {e}")

                # Marquer demande comme acceptée
                demande.statut = 'acceptee'
                demande.date_traitement = timezone.now()
                demande.traite_par = request.user
                demande.save()

                return Response({
                    'message': 'Demande marquée comme acceptée'
                })
                    # ===== ACCEPTER AUTOMATIQUE =====
            # (création automatique du compte)
            if action == 'accepter':
                from utilisateurs.models import Utilisateur
                import random
                import string

                # Vérifier si email déjà utilisé
                if Utilisateur.objects.filter(email=demande.email).exists():
                    return Response(
                        {'erreur': 'Un compte avec cet email existe déjà'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Générer username unique
                base_username = f"{demande.prenom.lower()}.{demande.nom.lower()}"
                base_username = base_username.replace(' ', '').replace('-', '')
                username = base_username
                compteur = 1
                while Utilisateur.objects.filter(username=username).exists():
                    username = f"{base_username}{compteur}"
                    compteur += 1

                # Générer mot de passe temporaire
                chars = 'ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789'
                password = ''.join(random.choices(chars, k=8))

                # Créer le compte client
                client = Utilisateur.objects.create_user(
                    username=username,
                    email=demande.email,
                    password=password,
                    first_name=demande.prenom,
                    last_name=demande.nom,
                    role='client',
                    telephone=demande.telephone,
                    adresse=demande.adresse,
                    zone=demande.zone,
                    latitude=demande.latitude,
                    longitude=demande.longitude,
                    type_client=demande.type_client,
                    statut_abonnement='en_traitement',
                    doc_cin=bool(demande.photo_cin),
                    doc_attestation=bool(demande.photo_attestation),
                    doc_contrat_location=bool(demande.photo_contrat),
                    doc_convention=bool(demande.photo_convention),
                )

                # Mettre à jour la demande
                demande.statut = 'acceptee'
                demande.date_traitement = timezone.now()
                demande.traite_par = request.user
                demande.save()

                # Envoyer email de bienvenue
                email_envoye = envoyer_email_bienvenue(client, password)

                return Response({
                    'message': f'Demande acceptée ! Compte créé avec succès.',
                    'email_envoye': email_envoye,
                    'client': {
                        'id': client.id,
                        'username': username,
                        'password_temporaire': password,
                        'email': demande.email,
                    }
                }, status=status.HTTP_201_CREATED)

        except DemandeAbonnement.DoesNotExist:
            return Response(
                {'erreur': 'Demande non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'erreur': f'Erreur serveur : {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            