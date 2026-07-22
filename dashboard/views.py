from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from utilisateurs.models import Utilisateur
        from compteurs.models import Compteur
        from consommation.models import Consommation
        from alertes.models import Alerte
        from factures.models import Facture

        user = request.user

        # Filtrer selon la zone de l'admin
        if user.role == 'super_admin':
            clients = Utilisateur.objects.filter(role='client')
            compteurs = Compteur.objects.all()
            alertes = Alerte.objects.filter(statut='en_cours')
            factures = Facture.objects.all()
            consommations = Consommation.objects.all()
        else:
            clients = Utilisateur.objects.filter(
                role='client',
                zone=user.zone
            )
            compteurs = Compteur.objects.filter(
                client__zone=user.zone
            )
            alertes = Alerte.objects.filter(
                compteur__client__zone=user.zone,
                statut='en_cours'
            )
            factures = Facture.objects.filter(
                client__zone=user.zone
            )
            consommations = Consommation.objects.filter(
                compteur__client__zone=user.zone
            )

        # Consommation du jour
        debut_jour = timezone.now() - timedelta(days=1)
        conso_jour = consommations.filter(
            date_heure__gte=debut_jour
        )
        total_conso_jour = sum(
            c.volume for c in conso_jour
        )

        # Consommation du mois
        debut_mois = timezone.now() - timedelta(days=30)
        conso_mois = consommations.filter(
            date_heure__gte=debut_mois
        )
        total_conso_mois = sum(
            c.volume for c in conso_mois
        )

        # Factures en retard
        factures_retard = factures.filter(
            statut='en_retard'
        ).count()

        return Response({
            'statistiques': {
                'total_clients': clients.count(),
                'total_compteurs': compteurs.count(),
                'compteurs_actifs': compteurs.filter(
                    statut='attribue'
                ).count(),
                'compteurs_en_panne': compteurs.filter(
                    statut='en_panne'
                ).count(),
                'alertes_en_cours': alertes.count(),
                'factures_en_retard': factures_retard,
                'consommation_jour': round(total_conso_jour, 2),
                'consommation_mois': round(total_conso_mois, 2),
            }
        })