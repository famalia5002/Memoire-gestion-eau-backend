from rest_framework import serializers
from .models import Facture, Tarif
from utilisateurs.serializers import UtilisateurSerializer
from consommation.serializers import IndexSerializer

class TarifSerializer(serializers.ModelSerializer):
    type_zone_label = serializers.CharField(
        source='get_type_zone_display',
        read_only=True
    )
    type_abonne_label = serializers.CharField(
        source='get_type_abonne_display',
        read_only=True
    )

    class Meta:
        model = Tarif
        fields = [
            'id', 'type_zone', 'type_zone_label',
            'type_abonne', 'type_abonne_label',
            'prix_ts', 'prix_tp', 'prix_td',
            'date_debut', 'date_fin', 'actif'
        ]

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
    periode_label = serializers.SerializerMethodField()

    class Meta:
        model = Facture
        fields = [
            'id', 'client', 'client_detail',
            'tarif', 'tarif_detail',
            'volume_total', 'montant',
            'statut', 'mode_paiement',
            'date_generation', 'date_limite',
            'periode_debut', 'periode_fin',
            'periode_label', 'index_list'
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
        mois_fr = [
            'Janvier', 'Février', 'Mars', 'Avril',
            'Mai', 'Juin', 'Juillet', 'Août',
            'Septembre', 'Octobre', 'Novembre', 'Décembre'
        ]
        if obj.periode_debut and obj.periode_fin:
            mois_debut = mois_fr[obj.periode_debut.month - 1]
            mois_fin = mois_fr[obj.periode_fin.month - 1]
            annee = obj.periode_fin.year
            return f"{mois_debut} - {mois_fin} {annee}"
        else:
            mois = mois_fr[obj.date_generation.month - 1]
            annee = obj.date_generation.year
            return f"{mois} {annee}"