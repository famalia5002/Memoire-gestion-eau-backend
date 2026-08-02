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

        # Filtrer selon rôle
        if user.role == 'super_admin':
            clients = Utilisateur.objects.filter(role='client')
            compteurs = Compteur.objects.all()
            alertes = Alerte.objects.filter(statut='en_cours')
            factures = Facture.objects.all()
            consommations = Consommation.objects.all()
        else:
            clients = Utilisateur.objects.filter(
                role='client', zone=user.zone
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

        # Consommation aujourd'hui
        debut_jour = timezone.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        total_conso_jour = sum(
            c.volume for c in consommations.filter(
                date_heure__gte=debut_jour
            )
        )

        # Consommation du mois
        debut_mois = timezone.now() - timedelta(days=30)
        total_conso_mois = sum(
            c.volume for c in consommations.filter(
                date_heure__gte=debut_mois
            )
        )

        # ===== GRAPHIQUE 1 : 7 derniers jours =====
        jours = []
        jours_fr = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
        for i in range(6, -1, -1):
            jour = timezone.now() - timedelta(days=i)
            debut = jour.replace(hour=0, minute=0, second=0, microsecond=0)
            fin = jour.replace(hour=23, minute=59, second=59, microsecond=999999)

            volume = sum(
                c.volume for c in consommations.filter(
                    date_heure__gte=debut,
                    date_heure__lte=fin
                )
            )

            jours.append({
                'jour': jours_fr[jour.weekday()],
                'date': jour.strftime('%d/%m'),
                'volume': round(volume, 2)
            })

        # ===== GRAPHIQUE 2 : 6 derniers mois =====
        mois = []
        mois_fr = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                   'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        for i in range(5, -1, -1):
            date_mois = timezone.now() - timedelta(days=30 * i)
            debut_m = date_mois.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            if date_mois.month == 12:
                fin_m = date_mois.replace(
                    year=date_mois.year + 1,
                    month=1, day=1
                ) - timedelta(seconds=1)
            else:
                fin_m = date_mois.replace(
                    month=date_mois.month + 1, day=1
                ) - timedelta(seconds=1)

            volume_mois = sum(
                c.volume for c in consommations.filter(
                    date_heure__gte=debut_m,
                    date_heure__lte=fin_m
                )
            )

            mois.append({
                'mois': mois_fr[date_mois.month - 1],
                'volume': round(volume_mois, 2)
            })

        # ===== STATS PAR ZONE =====
        zones = [
            'Dakar 1', 'Dakar 2', 'Thiès', 'Rufisque',
            'Mbour', 'Diourbel', 'Louga', 'Saint-Louis',
            'Tambacounda', 'Ziguinchor'
        ]
        stats_par_zone = []
        for zone in zones:
            clients_zone = Utilisateur.objects.filter(
                role='client', zone=zone
            ).count()
            compteurs_zone = Compteur.objects.filter(
                client__zone=zone
            ).count()
            conso_zone = sum(
                c.volume for c in Consommation.objects.filter(
                    compteur__client__zone=zone
                )
            )
            if clients_zone > 0 or compteurs_zone > 0:
                stats_par_zone.append({
                    'zone': zone,
                    'clients': clients_zone,
                    'compteurs': compteurs_zone,
                    'consommation': round(conso_zone, 2),
                })

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
                'factures_en_retard': factures.filter(
                    statut='en_retard'
                ).count(),
                'consommation_jour': round(total_conso_jour, 2),
                'consommation_mois': round(total_conso_mois, 2),
                'consommation_7jours': jours,
                'consommation_6mois': mois,
                'stats_par_zone': stats_par_zone,
            }
        })