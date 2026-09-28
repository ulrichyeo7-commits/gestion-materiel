from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Materiel


class AuthentificationPermissionsTests(APITestCase):

    @classmethod
    def setUpTestData(cls):

        modele_utilisateur = get_user_model()

        cls.mot_de_passe = "mot-de-passe-test"

        cls.utilisateur = modele_utilisateur.objects.create_user(
            username="utilisateur_auth",
            password=cls.mot_de_passe,
        )

        cls.admin = modele_utilisateur.objects.create_user(
            username="administrateur_auth",
            password=cls.mot_de_passe,
            is_staff=True,
        )

    def test_un_utilisateur_obtient_un_jwt_et_l_utilise(self):

        reponse_connexion = self.client.post(
            reverse("token-obtain-pair"),
            {
                "username": self.utilisateur.username,
                "password": self.mot_de_passe,
            },
            format="json",
        )

        self.assertEqual(
            reponse_connexion.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access", reponse_connexion.data)
        self.assertIn("refresh", reponse_connexion.data)

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {reponse_connexion.data['access']}"
            )
        )

        reponse_utilisateur = self.client.get(
            reverse("utilisateur-connecte")
        )

        self.assertEqual(
            reponse_utilisateur.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            reponse_utilisateur.data,
            {
                "id": self.utilisateur.id,
                "username": self.utilisateur.username,
                "is_staff": False,
            },
        )

    def test_une_route_protegee_refuse_un_utilisateur_anonyme(self):

        reponse = self.client.get(
            reverse("materiel-list")
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_un_utilisateur_normal_ne_peut_pas_acceder_a_l_administration(
        self
    ):

        self.client.force_authenticate(
            user=self.utilisateur
        )

        reponse = self.client.get(
            reverse("admin-materiel-list-create")
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_un_administrateur_peut_acceder_a_l_administration(self):

        self.client.force_authenticate(
            user=self.admin
        )

        reponse = self.client.get(
            reverse("admin-materiel-list-create")
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_200_OK,
        )


class MaterielAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):

        modele_utilisateur = get_user_model()

        cls.utilisateur = modele_utilisateur.objects.create_user(
            username="utilisateur_materiel",
            password="mot-de-passe-test",
        )

        cls.admin = modele_utilisateur.objects.create_user(
            username="administrateur_materiel",
            password="mot-de-passe-test",
            is_staff=True,
        )

        cls.materiel_disponible = Materiel.objects.create(
            nom="Ordinateur disponible",
            description="Matériel présent en stock",
            categorie="Informatique",
            quantite_disponible=3,
        )

        cls.materiel_epuise = Materiel.objects.create(
            nom="Écran épuisé",
            description="Matériel sans stock",
            categorie="Informatique",
            quantite_disponible=0,
        )

    def test_un_utilisateur_voit_uniquement_les_materiels_disponibles(self):

        self.client.force_authenticate(
            user=self.utilisateur
        )

        reponse = self.client.get(
            reverse("materiel-list")
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_200_OK,
        )

        identifiants = {
            materiel["id"]
            for materiel in reponse.data
        }

        self.assertIn(
            self.materiel_disponible.id,
            identifiants,
        )
        self.assertNotIn(
            self.materiel_epuise.id,
            identifiants,
        )

    def test_un_admin_ajoute_un_materiel_sans_photo(self):

        self.client.force_authenticate(
            user=self.admin
        )

        reponse = self.client.post(
            reverse("admin-materiel-list-create"),
            {
                "nom": "Clavier mécanique",
                "description": "Clavier filaire",
                "categorie": "Périphériques",
                "quantite_disponible": 8,
            },
            format="json",
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertIsNone(reponse.data["photo"])

        materiel = Materiel.objects.get(
            id=reponse.data["id"]
        )

        self.assertEqual(
            materiel.nom,
            "Clavier mécanique",
        )
        self.assertEqual(
            materiel.quantite_disponible,
            8,
        )
        self.assertFalse(materiel.photo)
