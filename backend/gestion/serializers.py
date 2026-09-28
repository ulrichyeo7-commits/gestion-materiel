from rest_framework import serializers

from .models import (
    Demande,
    LigneDemande,
    Materiel,
)


class UtilisateurConnecteSerializer(
    serializers.Serializer
):

    id = serializers.IntegerField(
        read_only=True
    )

    username = serializers.CharField(
        read_only=True
    )

    is_staff = serializers.BooleanField(
        read_only=True
    )


class ErreurSerializer(
    serializers.Serializer
):

    erreur = serializers.CharField(
        read_only=True
    )


class MaterielSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Materiel

        fields = [
            "id",
            "nom",
            "description",
            "categorie",
            "photo",
            "quantite_disponible",
            "date_creation",
        ]

        read_only_fields = [
            "id",
            "date_creation",
        ]


class LigneDemandeSerializer(
    serializers.ModelSerializer
):

    materiel = MaterielSerializer(
        read_only=True
    )

    class Meta:
        model = LigneDemande

        fields = [
            "id",
            "materiel",
            "quantite",
        ]


class DemandeSerializer(
    serializers.ModelSerializer
):

    utilisateur = (
        serializers.StringRelatedField()
    )

    lignes = LigneDemandeSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Demande

        fields = [
            "id",
            "utilisateur",
            "statut",
            "date_demande",
            "date_traitement",
            "lignes",
        ]


class LigneDemandeCreationSerializer(
    serializers.Serializer
):

    materiel_id = (
        serializers.PrimaryKeyRelatedField(
            queryset=Materiel.objects.all(),
            source="materiel"
        )
    )

    quantite = serializers.IntegerField(
        min_value=1
    )


class DemandeCreationSerializer(
    serializers.Serializer
):

    materiels = LigneDemandeCreationSerializer(
        many=True,
        allow_empty=False
    )


class DemandeTraitementSerializer(
    serializers.Serializer
):

    action = serializers.ChoiceField(
        choices=[
            "ACCEPTER",
            "REFUSER",
        ]
    )
