from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .models import Avis
from .serializers import AvisSerializer
from rest_framework.views import APIView

from rest_framework import generics, status
from rest_framework.response import Response

class ListeAvisView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvisSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'client':
            return Avis.objects.filter(client=user)
        return Avis.objects.all()

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

class DetailAvisView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvisSerializer
    queryset = Avis.objects.all()

from django.utils import timezone

class RepondreAvisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, avis_id):
        try:
            avis = Avis.objects.get(id=avis_id)
            reponse = request.data.get('reponse')

            if not reponse:
                return Response(
                    {'erreur': 'La réponse est vide'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            avis.reponse_admin = reponse
            avis.date_reponse = timezone.now()
            avis.statut = 'traite'  # ← marquer comme traité automatiquement
            avis.save()

            return Response({
                'message': 'Réponse envoyée avec succès',
                'avis_id': avis_id
            })

        except Avis.DoesNotExist:
            return Response(
                {'erreur': 'Avis non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )

class MarquerTraiteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, avis_id):
        try:
            avis = Avis.objects.get(id=avis_id)
            avis.statut = 'traite'
            avis.save()

            return Response({
                'message': 'Avis marqué comme traité'
            })

        except Avis.DoesNotExist:
            return Response(
                {'erreur': 'Avis non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
