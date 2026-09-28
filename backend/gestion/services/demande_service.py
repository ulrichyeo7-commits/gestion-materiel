from django.db import transaction
from django.utils import timezone

from ..models import (
    Demande,
    LigneDemande,
    Materiel,
)


class ErreurDemande(Exception):
    pass


def lister_demandes_utilisateur(utilisateur):

    return (
        Demande.objects
        .filter(utilisateur=utilisateur)
        .prefetch_related("lignes__materiel")
        .order_by("-date_demande")
    )


def lister_toutes_demandes():

    return (
        Demande.objects
        .select_related("utilisateur")
        .prefetch_related("lignes__materiel")
        .order_by("-date_demande")
    )


@transaction.atomic
def creer_demande(utilisateur, lignes):

    materiels_deja_ajoutes = set()

    for ligne in lignes:

        materiel = ligne["materiel"]
        quantite = ligne["quantite"]

        if materiel.id in materiels_deja_ajoutes:
            raise ErreurDemande(
                f"Le matériel « {materiel.nom} » "
                "apparaît plusieurs fois dans la demande."
            )

        materiels_deja_ajoutes.add(materiel.id)

        if quantite > materiel.quantite_disponible:
            raise ErreurDemande(
                f"Quantité insuffisante pour "
                f"« {materiel.nom} ». "
                f"Disponible : "
                f"{materiel.quantite_disponible}."
            )

    demande = Demande.objects.create(
        utilisateur=utilisateur
    )

    lignes_a_creer = []

    for ligne in lignes:

        lignes_a_creer.append(
            LigneDemande(
                demande=demande,
                materiel=ligne["materiel"],
                quantite=ligne["quantite"]
            )
        )

    LigneDemande.objects.bulk_create(
        lignes_a_creer
    )

    return (
        Demande.objects
        .select_related("utilisateur")
        .prefetch_related("lignes__materiel")
        .get(id=demande.id)
    )


@transaction.atomic
def traiter_demande(id_demande, action):

    try:
        demande = (
            Demande.objects
            .select_for_update()
            .get(id=id_demande)
        )

    except Demande.DoesNotExist:
        raise LookupError(
            "Demande introuvable."
        )

    if demande.statut != Demande.Statut.EN_ATTENTE:
        raise ErreurDemande(
            "Cette demande a déjà été traitée."
        )

    lignes = list(
        demande.lignes.select_related(
            "materiel"
        )
    )

    if action == "ACCEPTER":

        ids_materiels = [
            ligne.materiel_id
            for ligne in lignes
        ]

        materiels = {
            materiel.id: materiel
            for materiel in (
                Materiel.objects
                .select_for_update()
                .filter(
                    id__in=ids_materiels
                )
            )
        }

        for ligne in lignes:

            materiel = materiels[
                ligne.materiel_id
            ]

            if (
                materiel.quantite_disponible
                < ligne.quantite
            ):
                raise ErreurDemande(
                    f"Stock insuffisant pour "
                    f"« {materiel.nom} ». "
                    f"Disponible : "
                    f"{materiel.quantite_disponible}."
                )

        for ligne in lignes:

            materiel = materiels[
                ligne.materiel_id
            ]

            materiel.quantite_disponible -= (
                ligne.quantite
            )

            materiel.save(
                update_fields=[
                    "quantite_disponible"
                ]
            )

        demande.statut = (
            Demande.Statut.ACCEPTEE
        )

    elif action == "REFUSER":

        demande.statut = (
            Demande.Statut.REFUSEE
        )

    else:

        raise ErreurDemande(
            "Action invalide."
        )

    demande.date_traitement = timezone.now()

    demande.save(
        update_fields=[
            "statut",
            "date_traitement",
        ]
    )

    return (
        Demande.objects
        .select_related("utilisateur")
        .prefetch_related("lignes__materiel")
        .get(id=demande.id)
    )