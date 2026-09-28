from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Demande, LigneDemande, Materiel
from .services.demande_service import (
    creer_demande,
    traiter_demande,
)


class DonneesDemandeMixin:

    @classmethod
    def setUpTestData(cls):
        utilisateur = get_user_model()

        cls.demandeur = utilisateur.objects.create_user(
            username="demandeur",
            password="mot-de-passe-test",
        )
        cls.autre_demandeur = utilisateur.objects.create_user(
            username="autre_demandeur",
            password="mot-de-passe-test",
        )
        cls.admin = utilisateur.objects.create_user(
            username="admin_demandes",
            password="mot-de-passe-test",
            is_staff=True,
        )

        cls.ordinateur = Materiel.objects.create(
            nom="Ordinateur",
            categorie="Informatique",
            quantite_disponible=10,
        )
        cls.ecran = Materiel.objects.create(
            nom="Écran",
            categorie="Informatique",
            quantite_disponible=5,
        )

    def creer_demande(self, utilisateur=None, lignes=None):
        return creer_demande(
            utilisateur=utilisateur or self.demandeur,
            lignes=lignes or [
                {
                    "materiel": self.ordinateur,
                    "quantite": 1,
                }
            ],
        )

    def url_traitement(self, demande):
        return reverse(
            "admin-demande-traitement",
            kwargs={
                "id_demande": demande.id,
            },
        )


class DemandeAPITests(
    DonneesDemandeMixin,
    APITestCase,
):

    def test_creation_multi_materiels_cree_les_lignes_en_attente(self):
        self.client.force_authenticate(
            user=self.demandeur
        )

        reponse = self.client.post(
            reverse("demande-list-create"),
            {
                "materiels": [
                    {
                        "materiel_id": self.ordinateur.id,
                        "quantite": 2,
                    },
                    {
                        "materiel_id": self.ecran.id,
                        "quantite": 3,
                    },
                ]
            },
            format="json",
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_201_CREATED,
        )

        demande = Demande.objects.get(
            id=reponse.data["id"]
        )
        lignes = {
            ligne.materiel_id: ligne.quantite
            for ligne in demande.lignes.all()
        }

        self.assertEqual(
            demande.utilisateur,
            self.demandeur,
        )
        self.assertEqual(
            demande.statut,
            Demande.Statut.EN_ATTENTE,
        )
        self.assertIsNone(
            demande.date_traitement
        )
        self.assertEqual(
            lignes,
            {
                self.ordinateur.id: 2,
                self.ecran.id: 3,
            },
        )

        self.ordinateur.refresh_from_db()
        self.ecran.refresh_from_db()

        self.assertEqual(
            self.ordinateur.quantite_disponible,
            10,
        )
        self.assertEqual(
            self.ecran.quantite_disponible,
            5,
        )

    def test_quantite_nulle_ou_negative_est_refusee(self):
        self.client.force_authenticate(
            user=self.demandeur
        )

        for quantite in (0, -1):
            with self.subTest(quantite=quantite):
                reponse = self.client.post(
                    reverse("demande-list-create"),
                    {
                        "materiels": [
                            {
                                "materiel_id": self.ordinateur.id,
                                "quantite": quantite,
                            }
                        ]
                    },
                    format="json",
                )

                self.assertEqual(
                    reponse.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )

        self.assertEqual(
            Demande.objects.count(),
            0,
        )
        self.assertEqual(
            LigneDemande.objects.count(),
            0,
        )

    def test_quantite_superieure_au_stock_est_refusee(self):
        self.client.force_authenticate(
            user=self.demandeur
        )

        reponse = self.client.post(
            reverse("demande-list-create"),
            {
                "materiels": [
                    {
                        "materiel_id": self.ecran.id,
                        "quantite": 6,
                    }
                ]
            },
            format="json",
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "Quantité insuffisante",
            reponse.data["erreur"],
        )
        self.assertFalse(
            Demande.objects.exists()
        )
        self.assertFalse(
            LigneDemande.objects.exists()
        )

    def test_un_materiel_duplique_est_refuse(self):
        self.client.force_authenticate(
            user=self.demandeur
        )

        reponse = self.client.post(
            reverse("demande-list-create"),
            {
                "materiels": [
                    {
                        "materiel_id": self.ordinateur.id,
                        "quantite": 1,
                    },
                    {
                        "materiel_id": self.ordinateur.id,
                        "quantite": 2,
                    },
                ]
            },
            format="json",
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "apparaît plusieurs fois",
            reponse.data["erreur"],
        )
        self.assertFalse(
            Demande.objects.exists()
        )
        self.assertFalse(
            LigneDemande.objects.exists()
        )

    def test_un_utilisateur_ne_voit_que_ses_demandes(self):
        demande_visible = self.creer_demande()
        self.creer_demande(
            utilisateur=self.autre_demandeur
        )

        self.client.force_authenticate(
            user=self.demandeur
        )

        reponse = self.client.get(
            reverse("demande-list-create")
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            {
                element["id"]
                for element in reponse.data
            },
            {
                demande_visible.id
            },
        )

    def test_un_admin_voit_les_demandes_de_tous_les_utilisateurs(self):
        premiere = self.creer_demande()
        seconde = self.creer_demande(
            utilisateur=self.autre_demandeur
        )

        self.client.force_authenticate(
            user=self.admin
        )

        reponse = self.client.get(
            reverse("admin-demande-list")
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            {
                element["id"]
                for element in reponse.data
            },
            {
                premiere.id,
                seconde.id,
            },
        )

    def test_accepter_met_a_jour_statut_date_et_tous_les_stocks(self):
        demande = self.creer_demande(
            lignes=[
                {
                    "materiel": self.ordinateur,
                    "quantite": 3,
                },
                {
                    "materiel": self.ecran,
                    "quantite": 2,
                },
            ]
        )

        self.client.force_authenticate(
            user=self.admin
        )

        reponse = self.client.patch(
            self.url_traitement(demande),
            {
                "action": "ACCEPTER"
            },
            format="json",
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_200_OK,
        )

        demande.refresh_from_db()
        self.ordinateur.refresh_from_db()
        self.ecran.refresh_from_db()

        self.assertEqual(
            demande.statut,
            Demande.Statut.ACCEPTEE,
        )
        self.assertIsNotNone(
            demande.date_traitement
        )
        self.assertEqual(
            self.ordinateur.quantite_disponible,
            7,
        )
        self.assertEqual(
            self.ecran.quantite_disponible,
            3,
        )

    def test_refuser_change_le_statut_sans_diminuer_les_stocks(self):
        demande = self.creer_demande(
            lignes=[
                {
                    "materiel": self.ordinateur,
                    "quantite": 3,
                },
                {
                    "materiel": self.ecran,
                    "quantite": 2,
                },
            ]
        )

        self.client.force_authenticate(
            user=self.admin
        )

        reponse = self.client.patch(
            self.url_traitement(demande),
            {
                "action": "REFUSER"
            },
            format="json",
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_200_OK,
        )

        demande.refresh_from_db()
        self.ordinateur.refresh_from_db()
        self.ecran.refresh_from_db()

        self.assertEqual(
            demande.statut,
            Demande.Statut.REFUSEE,
        )
        self.assertIsNotNone(
            demande.date_traitement
        )
        self.assertEqual(
            self.ordinateur.quantite_disponible,
            10,
        )
        self.assertEqual(
            self.ecran.quantite_disponible,
            5,
        )

    def test_une_demande_deja_traitee_ne_peut_pas_etre_retraitee(self):
        demande = self.creer_demande()

        self.client.force_authenticate(
            user=self.admin
        )

        premiere_reponse = self.client.patch(
            self.url_traitement(demande),
            {
                "action": "ACCEPTER"
            },
            format="json",
        )

        demande.refresh_from_db()
        date_premier_traitement = demande.date_traitement

        seconde_reponse = self.client.patch(
            self.url_traitement(demande),
            {
                "action": "REFUSER"
            },
            format="json",
        )

        self.assertEqual(
            premiere_reponse.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            seconde_reponse.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "déjà été traitée",
            seconde_reponse.data["erreur"],
        )

        demande.refresh_from_db()
        self.ordinateur.refresh_from_db()

        self.assertEqual(
            demande.statut,
            Demande.Statut.ACCEPTEE,
        )
        self.assertEqual(
            demande.date_traitement,
            date_premier_traitement,
        )
        self.assertEqual(
            self.ordinateur.quantite_disponible,
            9,
        )

    def test_stock_reverifie_et_aucune_modification_partielle(self):
        demande = self.creer_demande(
            lignes=[
                {
                    "materiel": self.ordinateur,
                    "quantite": 4,
                },
                {
                    "materiel": self.ecran,
                    "quantite": 4,
                },
            ]
        )

        self.ecran.quantite_disponible = 3
        self.ecran.save(
            update_fields=[
                "quantite_disponible"
            ]
        )

        self.client.force_authenticate(
            user=self.admin
        )

        reponse = self.client.patch(
            self.url_traitement(demande),
            {
                "action": "ACCEPTER"
            },
            format="json",
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "Stock insuffisant",
            reponse.data["erreur"],
        )

        demande.refresh_from_db()
        self.ordinateur.refresh_from_db()
        self.ecran.refresh_from_db()

        self.assertEqual(
            demande.statut,
            Demande.Statut.EN_ATTENTE,
        )
        self.assertIsNone(
            demande.date_traitement
        )
        self.assertEqual(
            self.ordinateur.quantite_disponible,
            10,
        )
        self.assertEqual(
            self.ecran.quantite_disponible,
            3,
        )

    def test_action_de_traitement_invalide_ne_modifie_rien(self):
        demande = self.creer_demande()

        self.client.force_authenticate(
            user=self.admin
        )

        reponse = self.client.patch(
            self.url_traitement(demande),
            {
                "action": "ARCHIVER"
            },
            format="json",
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        demande.refresh_from_db()
        self.ordinateur.refresh_from_db()

        self.assertEqual(
            demande.statut,
            Demande.Statut.EN_ATTENTE,
        )
        self.assertIsNone(
            demande.date_traitement
        )
        self.assertEqual(
            self.ordinateur.quantite_disponible,
            10,
        )

    def test_traiter_une_demande_inexistante_retourne_404(self):
        self.client.force_authenticate(
            user=self.admin
        )

        reponse = self.client.patch(
            reverse(
                "admin-demande-traitement",
                kwargs={
                    "id_demande": 999999,
                },
            ),
            {
                "action": "ACCEPTER"
            },
            format="json",
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            reponse.data["erreur"],
            "Demande introuvable.",
        )


class AtomiciteTraitementTests(
    DonneesDemandeMixin,
    TestCase,
):

    def test_une_exception_annule_les_decrements_deja_effectues(self):
        demande = self.creer_demande(
            lignes=[
                {
                    "materiel": self.ordinateur,
                    "quantite": 2,
                },
                {
                    "materiel": self.ecran,
                    "quantite": 2,
                },
            ]
        )

        sauvegarde_reelle = Materiel.save
        sauvegardes_tentees = []

        def sauvegarder_puis_echouer(instance, *args, **kwargs):
            sauvegardes_tentees.append(instance.id)

            if len(sauvegardes_tentees) == 2:
                raise RuntimeError(
                    "Échec simulé pendant la seconde sauvegarde."
                )

            return sauvegarde_reelle(
                instance,
                *args,
                **kwargs,
            )

        with patch.object(
            Materiel,
            "save",
            new=sauvegarder_puis_echouer,
        ):
            with self.assertRaises(RuntimeError):
                traiter_demande(
                    id_demande=demande.id,
                    action="ACCEPTER",
                )

        self.assertEqual(
            len(sauvegardes_tentees),
            2,
        )

        demande.refresh_from_db()
        self.ordinateur.refresh_from_db()
        self.ecran.refresh_from_db()

        self.assertEqual(
            demande.statut,
            Demande.Statut.EN_ATTENTE,
        )
        self.assertIsNone(
            demande.date_traitement
        )
        self.assertEqual(
            self.ordinateur.quantite_disponible,
            10,
        )
        self.assertEqual(
            self.ecran.quantite_disponible,
            5,
        )
