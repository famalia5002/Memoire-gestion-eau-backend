from django.shortcuts import render

# Create your views here.

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Compteur
from .serializers import CompteurSerializer
from django.db.models import Q

class ListeCompteursView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompteurSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Compteur.objects.all()
        
        # Admin zone voit :
        # - Les compteurs de sa zone (avec client)
        # - Les compteurs disponibles (sans client)
        return Compteur.objects.filter(
            Q(client__zone=user.zone) |  # compteurs avec client de sa zone
            Q(client__isnull=True)        # compteurs sans client
        ).distinct()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class DetailCompteurView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompteurSerializer
    queryset = Compteur.objects.all()

class AssocierCompteurClientView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, compteur_id):
        try:
            compteur = Compteur.objects.get(id=compteur_id)
            client_id = request.data.get('client_id')
            
            from utilisateurs.models import Utilisateur
            client = Utilisateur.objects.get(
                id=client_id,
                role='client'
            )
            
            compteur.client = client
            compteur.statut = 'attribue'
            compteur.save()
            
            return Response({
                'message': f'Compteur {compteur.numero_compteur} associé à {client.nom_complet}'
            })
        except Compteur.DoesNotExist:
            return Response(
                {'erreur': 'Compteur non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )

class ControlerVanneView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, compteur_id):
        try:
            compteur = Compteur.objects.get(id=compteur_id)
            action = request.data.get('action')

            if action not in ['ouvrir', 'fermer']:
                return Response(
                    {'erreur': 'Action invalide'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Enregistrer la commande
            from alertes.models import Commande
            Commande.objects.create(
                compteur=compteur,
                action=action,
                effectuee_par=request.user,
                statut='envoyee'
            )

            # Mettre à jour l'état de la vanne
            compteur.etat_vanne = 'ouverte' if action == 'ouvrir' else 'fermee'
            compteur.save()

            return Response({
                'message': f'Vanne {action}e avec succès',
                'etat_vanne': compteur.etat_vanne
            })

        except Compteur.DoesNotExist:
            return Response(
                {'erreur': 'Compteur non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )

class DesassocierCompteurView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, compteur_id):
        try:
            compteur = Compteur.objects.get(id=compteur_id)
            compteur.client = None
            compteur.statut = 'disponible'
            compteur.save()

            return Response({
                'message': f'Compteur {compteur.numero_compteur} désassocié avec succès'
            })
        except Compteur.DoesNotExist:
            return Response(
                {'erreur': 'Compteur non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
