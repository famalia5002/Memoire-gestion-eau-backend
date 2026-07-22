from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from datetime import timedelta
from .models import Consommation, Index
from .serializers import ConsommationSerializer, IndexSerializer

class EnregistrerConsommationView(APIView):
    # AllowAny car c'est l'ESP32 qui envoie (pas d'authentification)
    permission_classes = [AllowAny]

    def post(self, request):
        from compteurs.models import Compteur
        
        numero_compteur = request.data.get('numero_compteur')
        volume = request.data.get('volume')

        try:
            compteur = Compteur.objects.get(
                numero_compteur=numero_compteur
            )
            
            # Enregistrer la consommation
            consommation = Consommation.objects.create(
                compteur=compteur,
                volume=volume
            )

            # Mettre à jour l'index
            dernier_index = Index.objects.filter(
                compteur=compteur
            ).first()
            
            nouvelle_valeur = (dernier_index.valeur_index if dernier_index else 0) + (volume / 1000)
            
            Index.objects.create(
                compteur=compteur,
                valeur_index=nouvelle_valeur
            )

            # Vérifier anomalie
            self.verifier_anomalie(compteur, volume)

            return Response({
                'message': 'Consommation enregistrée',
                'volume': volume,
                'compteur': numero_compteur
            }, status=status.HTTP_201_CREATED)

        except Compteur.DoesNotExist:
            return Response(
                {'erreur': 'Compteur non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )

    def verifier_anomalie(self, compteur, volume):
        from alertes.models import Alerte
        # Seuil de surconsommation : 100 litres en une mesure
        if volume > 100:
            Alerte.objects.create(
                compteur=compteur,
                type_alerte='surconsommation'
            )

class ConsommationClientView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        periode = request.query_params.get('periode', 'journalier')
        
        # Récupérer les compteurs du client
        from compteurs.models import Compteur
        compteurs = Compteur.objects.filter(client=user)

        if periode == 'journalier':
            debut = timezone.now() - timedelta(days=1)
        elif periode == 'mensuel':
            debut = timezone.now() - timedelta(days=30)
        else:
            debut = timezone.now() - timedelta(days=365)

        consommations = Consommation.objects.filter(
            compteur__in=compteurs,
            date_heure__gte=debut
        )

        serializer = ConsommationSerializer(
            consommations, many=True
        )
        return Response(serializer.data)

class IndexCompteurView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = IndexSerializer

    def get_queryset(self):
        compteur_id = self.kwargs.get('compteur_id')
        return Index.objects.filter(compteur_id=compteur_id)