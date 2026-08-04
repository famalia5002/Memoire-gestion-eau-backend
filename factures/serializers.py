from rest_framework import serializers
from .models import Facture, Tarif
from utilisateurs.serializers import UtilisateurSerializer

class TarifSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarif
        fields = '__all__'

from consommation.serializers import IndexSerializer
from compteurs.models import Compteur
from consommation.models import Index

class FactureSerializer(serializers.ModelSerializer):
    client_detail = UtilisateurSerializer(
        source='client',
        read_only=True
    )
    tarif_detail = TarifSerializer(
        source='tarif',
        read_only=True
    )
    index_list = serializers.SerializerMethodField()
    periode_label = serializers.SerializerMethodField()  # ← nouveau

    class Meta:
        model = Facture
        fields = [
            'id', 'client', 'client_detail',
            'tarif', 'tarif_detail',
            'volume_total', 'montant',
            'statut', 'mode_paiement',
            'date_generation', 'date_limite',
            'periode_debut', 'periode_fin',
            'periode_label',  # ← nouveau
            'index_list'
        ]

    def get_index_list(self, obj):
        from compteurs.models import Compteur
        from consommation.models import Index
        compteurs = Compteur.objects.filter(client=obj.client)
        index = Index.objects.filter(
            compteur__in=compteurs
        ).order_by('-date_releve')[:2]
        return IndexSerializer(index, many=True).data

    def get_periode_label(self, obj):
        # Générer le label de la période
        if obj.periode_debut and obj.periode_fin:
            mois_fr = [
                'Janvier', 'Février', 'Mars', 'Avril',
                'Mai', 'Juin', 'Juillet', 'Août',
                'Septembre', 'Octobre', 'Novembre', 'Décembre'
            ]
            mois = mois_fr[obj.periode_fin.month - 1]
            annee = obj.periode_fin.year
            return f"{mois} {annee}"
        else:
            # Si pas de période définie, utiliser la date de génération
            mois_fr = [
                'Janvier', 'Février', 'Mars', 'Avril',
                'Mai', 'Juin', 'Juillet', 'Août',
                'Septembre', 'Octobre', 'Novembre', 'Décembre'
            ]
            mois = mois_fr[obj.date_generation.month - 1]
            annee = obj.date_generation.year
            return f"{mois} {annee}"