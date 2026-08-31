from django.shortcuts import render

# Create your views here.

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Alerte, Commande
from .serializers import AlerteSerializer, CommandeSerializer

class ListeAlertesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AlerteSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'client':
            return Alerte.objects.filter(
                compteur__client=user
            )
        elif user.role == 'admin_zone':
            return Alerte.objects.filter(
                compteur__client__zone=user.zone
            )
        return Alerte.objects.all()

class ResoudreAlerteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, alerte_id):
        try:
            alerte = Alerte.objects.get(id=alerte_id)

            if alerte.statut == 'resolue':
                return Response(
                    {'erreur': 'Cette alerte est déjà résolue'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Juste marquer comme résolue
            # L'admin gère la vanne manuellement depuis la page Compteurs
            alerte.statut = 'resolue'
            alerte.date_resolution = timezone.now()
            alerte.save()

            return Response({
                'message': 'Alerte résolue avec succès',
            })

        except Alerte.DoesNotExist:
            return Response(
                {'erreur': 'Alerte non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'erreur': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class ListeCommandesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommandeSerializer
    queryset = Commande.objects.all()
