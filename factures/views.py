from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import Facture, Tarif
from .serializers import FactureSerializer, TarifSerializer

# Zones assainies
ZONES_ASSAINIES = ['Dakar 1', 'Dakar 2', 'Thiès', 'Rufisque', 'Mbour']

def calculer_montant(volume_m3, tarif):
    """
    Calcule le montant selon les tranches SEN'EAU
    Facturation bimestrielle
    """
    montant = 0

    if volume_m3 <= 20:
        montant = volume_m3 * tarif.prix_ts
    elif volume_m3 <= 40:
        montant = (20 * tarif.prix_ts) + \
                  ((volume_m3 - 20) * tarif.prix_tp)
    else:
        montant = (20 * tarif.prix_ts) + \
                  (20 * tarif.prix_tp) + \
                  ((volume_m3 - 40) * tarif.prix_td)

    return round(montant, 2)


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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class DetailFactureView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FactureSerializer
    queryset = Facture.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


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

            # Rouvrir la vanne si fermée
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

        try:
            client = Utilisateur.objects.get(
                id=client_id, role='client'
            )
        except Utilisateur.DoesNotExist:
            return Response(
                {'erreur': 'Client non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Déterminer type de zone
        type_zone = 'assainie' if client.zone in ZONES_ASSAINIES \
            else 'non_assainie'

        # Récupérer tarif selon zone
        tarif = Tarif.objects.filter(
            type_zone=type_zone,
            type_abonne='domestique_15mm',
            actif=True,
            date_fin__isnull=True
        ).first()

        if not tarif:
            tarif = Tarif.objects.filter(actif=True).first()

        if not tarif:
            return Response(
                {'erreur': 'Aucun tarif défini. Créez un tarif d\'abord.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Période bimestrielle (2 mois)
        fin = timezone.now()
        debut = fin - timedelta(days=60)

        compteurs = Compteur.objects.filter(client=client)
        consommations = Consommation.objects.filter(
            compteur__in=compteurs,
            date_heure__gte=debut,
            date_heure__lte=fin
        )

        volume_litres = sum(c.volume for c in consommations)
        volume_m3 = volume_litres / 1000

        if volume_m3 == 0:
            return Response(
                {'erreur': 'Aucune consommation sur cette période'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier facture déjà générée
        facture_existante = Facture.objects.filter(
            client=client,
            date_generation__gte=debut
        ).first()

        if facture_existante:
            return Response(
                {'erreur': 'Facture déjà générée ce bimestre'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculer montant avec tranches
        montant = calculer_montant(volume_m3, tarif)

        # Créer facture
        facture = Facture.objects.create(
            client=client,
            tarif=tarif,
            volume_total=round(volume_litres, 2),
            montant=montant,
            statut='en_attente',
            date_limite=(timezone.now() + timedelta(days=60)).date(),
            periode_debut=debut.date(),
            periode_fin=fin.date()
        )

        serializer = FactureSerializer(
            facture,
            context={'request': request}
        )
        return Response({
            'message': f'Facture générée pour {client.nom_complet}',
            'facture': serializer.data,
            'detail_calcul': {
                'volume_litres': round(volume_litres, 2),
                'volume_m3': round(volume_m3, 3),
                'zone': type_zone,
                'tarifs_appliques': {
                    'TS (0-20 m³)': f"{tarif.prix_ts} FCFA/m³",
                    'TP (21-40 m³)': f"{tarif.prix_tp} FCFA/m³",
                    'TD (>40 m³)': f"{tarif.prix_td} FCFA/m³",
                }
            }
        }, status=status.HTTP_201_CREATED)


class GenererToutesFacturesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from utilisateurs.models import Utilisateur
        from consommation.models import Consommation
        from compteurs.models import Compteur

        fin = timezone.now()
        debut = fin - timedelta(days=60)

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
            # Tarif selon zone
            type_zone = 'assainie' if client.zone in ZONES_ASSAINIES \
                else 'non_assainie'

            tarif = Tarif.objects.filter(
                type_zone=type_zone,
                type_abonne='domestique_15mm',
                actif=True,
                date_fin__isnull=True
            ).first()

            if not tarif:
                tarif = Tarif.objects.filter(actif=True).first()

            if not tarif:
                erreurs.append(f'{client.nom_complet} : aucun tarif')
                continue

            compteurs = Compteur.objects.filter(client=client)
            consommations = Consommation.objects.filter(
                compteur__in=compteurs,
                date_heure__gte=debut,
                date_heure__lte=fin
            )

            volume_litres = sum(c.volume for c in consommations)
            volume_m3 = volume_litres / 1000

            if volume_m3 == 0:
                erreurs.append(
                    f'{client.nom_complet} : aucune consommation'
                )
                continue

            facture_existante = Facture.objects.filter(
                client=client,
                date_generation__gte=debut
            ).first()

            if facture_existante:
                erreurs.append(
                    f'{client.nom_complet} : facture déjà générée'
                )
                continue

            montant = calculer_montant(volume_m3, tarif)

            facture = Facture.objects.create(
                client=client,
                tarif=tarif,
                volume_total=round(volume_litres, 2),
                montant=montant,
                statut='en_attente',
                date_limite=(timezone.now() + timedelta(days=60)).date(),
                periode_debut=debut.date(),
                periode_fin=fin.date()
            )
            factures_creees.append(
                f'{client.nom_complet} : {montant} FCFA'
            )

        return Response({
            'message': f'{len(factures_creees)} facture(s) générée(s)',
            'factures_creees': factures_creees,
            'erreurs': erreurs
        })