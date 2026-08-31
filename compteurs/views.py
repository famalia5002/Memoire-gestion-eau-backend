from django.shortcuts import render
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
        return Compteur.objects.filter(
            Q(client__zone=user.zone) |
            Q(client__isnull=True)
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

            if client.statut_abonnement == 'en_traitement':
                client.statut_abonnement = 'actif'
                client.save()

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

            # ← Si fermée par admin, seul l'admin peut rouvrir
            if (action == 'ouvrir' and
                    getattr(compteur, 'ferme_par', None) == 'admin' and
                    request.user.role == 'client'):
                return Response(
                    {'erreur': 'Seul l\'administrateur peut rouvrir cette vanne.'},
                    status=status.HTTP_403_FORBIDDEN
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

            # Qui a fermé ?
            if action == 'fermer':
                if request.user.role == 'client':
                    compteur.ferme_par = 'client'
                else:
                    compteur.ferme_par = 'admin'
            else:
                compteur.ferme_par = None  # ← réinitialiser à l'ouverture

            compteur.save()

            return Response({
                'message': f'Vanne {action}e avec succès',
                'etat_vanne': compteur.etat_vanne,
                'ferme_par': compteur.ferme_par
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


#  Client peut fermer sa vanne d'urgence
class FermerVanneClientView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, compteur_id):
        try:
            # Vérifier que c'est bien le compteur du client connecté
            compteur = Compteur.objects.get(
                id=compteur_id,
                client=request.user
            )

            if compteur.etat_vanne == 'fermee':
                return Response(
                    {'erreur': 'La vanne est déjà fermée'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Fermer la vanne
            compteur.etat_vanne = 'fermee'
            compteur.ferme_par = 'client'
            compteur.save()

            # Créer une alerte automatiquement
            from alertes.models import Alerte
            Alerte.objects.create(
                compteur=compteur,
                type_alerte='vanne_fermee',
                statut='en_cours',
            )

            # Enregistrer la commande
            from alertes.models import Commande
            Commande.objects.create(
                compteur=compteur,
                action='fermer',
                effectuee_par=request.user,
                statut='envoyee'
            )

            return Response({
                'message': 'Vanne fermée avec succès. L\'administrateur a été notifié.',
                'etat_vanne': 'fermee',
                'ferme_par': 'client'
            })

        except Compteur.DoesNotExist:
            return Response(
                {'erreur': 'Compteur non trouvé ou non autorisé'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'erreur': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RouvrirVanneClientView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, compteur_id):
        try:
            compteur = Compteur.objects.get(
                id=compteur_id,
                client=request.user
            )

            # ← Client ne peut rouvrir que si c'est lui qui a fermé
            if compteur.ferme_par == 'admin':
                return Response(
                    {'erreur': 'Seul l\'administrateur peut rouvrir cette vanne.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if compteur.etat_vanne == 'ouverte':
                return Response(
                    {'erreur': 'La vanne est déjà ouverte'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            compteur.etat_vanne = 'ouverte'
            compteur.ferme_par = None
            compteur.save()

            return Response({
                'message': 'Vanne rouverte avec succès.',
                'etat_vanne': 'ouverte',
            })

        except Compteur.DoesNotExist:
            return Response(
                {'erreur': 'Compteur non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )