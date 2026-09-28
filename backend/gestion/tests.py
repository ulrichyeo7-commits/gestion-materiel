import json

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Materiel


class OpenAPIDocumentationTests(APITestCase):

    def _obtenir_schema(self):

        reponse = self.client.get(
            reverse("api-schema"),
            {
                "format": "json"
            },
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_200_OK,
        )

        return json.loads(
            reponse.content.decode("utf-8")
        )

    def test_le_schema_json_est_public_et_identifie_api(self):

        schema = self._obtenir_schema()

        self.assertTrue(
            str(schema.get("openapi", "")).startswith("3.")
        )
        self.assertIsInstance(
            schema.get("info"),
            dict,
        )
        self.assertTrue(
            schema["info"].get("title")
        )
        self.assertTrue(
            schema["info"].get("version")
        )

    def test_le_schema_documente_les_routes_et_methodes_api(self):

        schema = self._obtenir_schema()
        chemins = schema.get("paths", {})

        operations_attendues = {
            "/api/auth/me/": {
                "get"
            },
            "/api/auth/login/": {
                "post"
            },
            "/api/auth/refresh/": {
                "post"
            },
            "/api/materiels/": {
                "get"
            },
            "/api/demandes/": {
                "get",
                "post",
            },
            "/api/admin/demandes/": {
                "get"
            },
            "/api/admin/demandes/{id_demande}/": {
                "patch"
            },
            "/api/admin/materiels/": {
                "get",
                "post",
            },
            "/api/admin/materiels/{id_materiel}/": {
                "put",
                "patch",
            },
        }

        for chemin, methodes in operations_attendues.items():

            with self.subTest(chemin=chemin):

                self.assertIn(
                    chemin,
                    chemins,
                )
                self.assertTrue(
                    methodes.issubset(
                        chemins[chemin]
                    ),
                    msg=(
                        f"Méthodes manquantes pour {chemin}: "
                        f"{methodes.difference(chemins[chemin])}"
                    ),
                )

    def test_le_schema_declare_et_utilise_jwt_bearer(self):

        schema = self._obtenir_schema()

        mecanismes = (
            schema.get("components", {})
            .get("securitySchemes", {})
        )

        jwt_bearer = {
            nom
            for nom, configuration in mecanismes.items()
            if (
                configuration.get("type") == "http"
                and configuration.get(
                    "scheme",
                    "",
                ).lower() == "bearer"
                and configuration.get(
                    "bearerFormat",
                    "",
                ).upper() == "JWT"
            )
        }

        self.assertTrue(
            jwt_bearer,
            msg=(
                "Le schéma doit déclarer une "
                "authentification HTTP Bearer JWT."
            ),
        )

        operations_protegees = [
            (
                "/api/auth/me/",
                "get",
            ),
            (
                "/api/materiels/",
                "get",
            ),
            (
                "/api/demandes/",
                "post",
            ),
            (
                "/api/admin/materiels/",
                "post",
            ),
        ]

        for chemin, methode in operations_protegees:

            exigences = (
                schema["paths"][chemin][methode]
                .get("security", [])
            )

            with self.subTest(
                chemin=chemin,
                methode=methode,
            ):

                self.assertTrue(
                    any(
                        jwt_bearer.intersection(
                            exigence
                        )
                        for exigence in exigences
                    ),
                    msg=(
                        f"{methode.upper()} {chemin} doit "
                        "référencer le mécanisme JWT."
                    ),
                )

    def test_les_routes_de_documentation_sont_exclues_du_schema(self):

        schema = self._obtenir_schema()
        chemins = schema.get("paths", {})

        self.assertNotIn(
            reverse("api-schema"),
            chemins,
        )
        self.assertNotIn(
            reverse("api-swagger-ui"),
            chemins,
        )

    def test_swagger_est_public_et_charge_le_schema(self):

        reponse = self.client.get(
            reverse("api-swagger-ui")
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_200_OK,
        )
        self.assertTrue(
            reponse["Content-Type"].startswith(
                "text/html"
            )
        )
        self.assertContains(
            reponse,
            reverse("api-schema"),
        )


class AdminMaterielUpdateTests(APITestCase):

    def setUp(self):

        utilisateur = get_user_model()

        self.admin = utilisateur.objects.create_user(
            username="admin_materiel",
            password="mot-de-passe-test",
            is_staff=True,
        )

        self.utilisateur = (
            utilisateur.objects.create_user(
                username="utilisateur_standard",
                password="mot-de-passe-test",
            )
        )

        self.materiel = Materiel.objects.create(
            nom="Ordinateur portable",
            description="Modèle initial",
            categorie="Informatique",
            quantite_disponible=4,
        )

        self.url = reverse(
            "admin-materiel-update",
            kwargs={
                "id_materiel": self.materiel.id
            },
        )

    def test_un_admin_peut_modifier_un_materiel(self):

        self.client.force_authenticate(
            user=self.admin
        )

        reponse = self.client.put(
            self.url,
            {
                "nom": "Ordinateur graphique",
                "description": "Station mobile",
                "categorie": "Création numérique",
                "quantite_disponible": 7,
            },
            format="multipart",
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_200_OK,
        )

        self.materiel.refresh_from_db()

        self.assertEqual(
            self.materiel.nom,
            "Ordinateur graphique",
        )
        self.assertEqual(
            self.materiel.description,
            "Station mobile",
        )
        self.assertEqual(
            self.materiel.categorie,
            "Création numérique",
        )
        self.assertEqual(
            self.materiel.quantite_disponible,
            7,
        )

    def test_un_non_admin_ne_peut_pas_modifier_un_materiel(
        self
    ):

        self.client.force_authenticate(
            user=self.utilisateur
        )

        reponse = self.client.patch(
            self.url,
            {
                "nom": "Nom interdit"
            },
            format="json",
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.materiel.refresh_from_db()

        self.assertEqual(
            self.materiel.nom,
            "Ordinateur portable",
        )

    def test_un_admin_peut_modifier_partiellement_les_caracteristiques(
        self
    ):

        self.client.force_authenticate(
            user=self.admin
        )

        reponse = self.client.patch(
            self.url,
            {
                "description": "Mémoire 32 Go et SSD 1 To",
                "categorie": "Postes de travail",
                "quantite_disponible": 9,
            },
            format="json",
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_200_OK,
        )

        self.materiel.refresh_from_db()

        self.assertEqual(
            self.materiel.nom,
            "Ordinateur portable",
        )
        self.assertEqual(
            self.materiel.description,
            "Mémoire 32 Go et SSD 1 To",
        )
        self.assertEqual(
            self.materiel.categorie,
            "Postes de travail",
        )
        self.assertEqual(
            self.materiel.quantite_disponible,
            9,
        )

    def test_un_admin_recoit_404_pour_un_materiel_inexistant(
        self
    ):

        self.client.force_authenticate(
            user=self.admin
        )

        url_inexistante = reverse(
            "admin-materiel-update",
            kwargs={
                "id_materiel": self.materiel.id + 999
            },
        )

        reponse = self.client.patch(
            url_inexistante,
            {
                "nom": "Matériel inexistant"
            },
            format="json",
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_une_quantite_negative_est_refusee_sans_modification(
        self
    ):

        self.client.force_authenticate(
            user=self.admin
        )

        valeurs_initiales = {
            "nom": self.materiel.nom,
            "description": self.materiel.description,
            "categorie": self.materiel.categorie,
            "quantite_disponible": (
                self.materiel.quantite_disponible
            ),
        }

        reponse = self.client.patch(
            self.url,
            {
                "description": "Ne doit pas être enregistrée",
                "quantite_disponible": -1,
            },
            format="json",
        )

        self.assertEqual(
            reponse.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.materiel.refresh_from_db()

        self.assertEqual(
            {
                "nom": self.materiel.nom,
                "description": self.materiel.description,
                "categorie": self.materiel.categorie,
                "quantite_disponible": (
                    self.materiel.quantite_disponible
                ),
            },
            valeurs_initiales,
        )
