from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Facture, Tarif
from .serializers import FactureSerializer, TarifSerializer

class ListeFacturesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FactureSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'client':
            return Facture.objects.filter(client=user)
        elif user.role == 'admin_zone':
            return Facture.objects.filter(
                client__zone=user.zone
            )
        return Facture.objects.all()

class DetailFactureView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FactureSerializer
    queryset = Facture.objects.all()

class PayerFactureView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, facture_id):
        try:
            facture = Facture.objects.get(id=facture_id)
            mode_paiement = request.data.get('mode_paiement')

            if mode_paiement not in ['agence', 'wave', 'orange_money']:
                return Response(
                    {'erreur': 'Mode de paiement invalide'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            facture.statut = 'payee'
            facture.mode_paiement = mode_paiement
            facture.save()

            # Rouvrir la vanne si elle était fermée
            compteurs = facture.client.compteurs.all()
            for compteur in compteurs:
                if compteur.etat_vanne == 'fermee':
                    compteur.etat_vanne = 'ouverte'
                    compteur.save()

            return Response({
                'message': 'Paiement effectué avec succès',
                'mode': mode_paiement,
                'statut': 'payee'
            })

        except Facture.DoesNotExist:
            return Response(
                {'erreur': 'Facture non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )

class TarifView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TarifSerializer
    queryset = Tarif.objects.all()
