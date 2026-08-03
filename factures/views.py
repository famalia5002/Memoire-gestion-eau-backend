from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
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


class GenererFactureView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from utilisateurs.models import Utilisateur
        from consommation.models import Consommation
        from compteurs.models import Compteur

        client_id = request.data.get('client_id')
        debut_periode = request.data.get('debut_periode')
        fin_periode = request.data.get('fin_periode')

        try:
            client = Utilisateur.objects.get(
                id=client_id,
                role='client'
            )
        except Utilisateur.DoesNotExist:
            return Response(
                {'erreur': 'Client non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Récupérer tarif actif
        tarif = Tarif.objects.filter(
            date_fin__isnull=True
        ).first()

        if not tarif:
            return Response(
                {'erreur': 'Aucun tarif défini. Créez un tarif d\'abord.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Période par défaut = 30 derniers jours
        if debut_periode and fin_periode:
            from datetime import datetime
            debut = datetime.fromisoformat(debut_periode)
            fin = datetime.fromisoformat(fin_periode)
        else:
            fin = timezone.now()
            debut = fin - timedelta(days=30)

        # Compteurs du client
        compteurs = Compteur.objects.filter(client=client)

        # Consommation sur la période
        consommations = Consommation.objects.filter(
            compteur__in=compteurs,
            date_heure__gte=debut,
            date_heure__lte=fin
        )

        volume_total = sum(c.volume for c in consommations)

        if volume_total == 0:
            return Response(
                {'erreur': 'Aucune consommation sur cette période'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier si facture déjà générée sur cette période
        facture_existante = Facture.objects.filter(
            client=client,
            date_generation__gte=debut,
            date_generation__lte=fin
        ).first()

        if facture_existante:
            return Response(
                {'erreur': f'Facture #{facture_existante.id} déjà générée pour ce client sur cette période'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculer montant
        montant = round(volume_total * tarif.prix_litre, 2)

        # Créer la facture
        facture = Facture.objects.create(
            client=client,
            tarif=tarif,
            volume_total=round(volume_total, 2),
            montant=montant,
            statut='en_attente',
            date_limite=(timezone.now() + timedelta(days=30)).date()
        )

        serializer = FactureSerializer(
            facture,
            context={'request': request}
        )
        return Response({
            'message': f'Facture générée pour {client.nom_complet}',
            'facture': serializer.data
        }, status=status.HTTP_201_CREATED)


class GenererToutesFacturesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from utilisateurs.models import Utilisateur
        from consommation.models import Consommation
        from compteurs.models import Compteur

        # Tarif actif
        tarif = Tarif.objects.filter(
            date_fin__isnull=True
        ).first()

        if not tarif:
            return Response(
                {'erreur': 'Aucun tarif défini'},
                status=status.HTTP_400_BAD_REQUEST
            )

        fin = timezone.now()
        debut = fin - timedelta(days=30)

        # Clients selon rôle
        if request.user.role == 'super_admin':
            clients = Utilisateur.objects.filter(role='client')
        else:
            clients = Utilisateur.objects.filter(
                role='client',
                zone=request.user.zone
            )

        factures_creees = []
        erreurs = []

        for client in clients:
            compteurs = Compteur.objects.filter(client=client)
            consommations = Consommation.objects.filter(
                compteur__in=compteurs,
                date_heure__gte=debut,
                date_heure__lte=fin
            )

            volume_total = sum(c.volume for c in consommations)

            if volume_total == 0:
                erreurs.append(
                    f'{client.nom_complet} : aucune consommation'
                )
                continue

            # Vérifier si facture déjà générée
            facture_existante = Facture.objects.filter(
                client=client,
                date_generation__gte=debut
            ).first()

            if facture_existante:
                erreurs.append(
                    f'{client.nom_complet} : facture déjà générée'
                )
                continue

            montant = round(volume_total * tarif.prix_litre, 2)

            facture = Facture.objects.create(
                client=client,
                tarif=tarif,
                volume_total=round(volume_total, 2),
                montant=montant,
                statut='en_attente',
                date_limite=(timezone.now() + timedelta(days=30)).date()
            )
            factures_creees.append(f'{client.nom_complet} : {montant} FCFA')

        return Response({
            'message': f'{len(factures_creees)} facture(s) générée(s)',
            'factures_creees': factures_creees,
            'erreurs': erreurs
        })