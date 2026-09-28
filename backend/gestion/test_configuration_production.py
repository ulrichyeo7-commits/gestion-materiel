import os
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config.environment import (
    database_config,
    env_bool,
    env_int,
    env_list,
)


class EnvironmentHelpersTests(SimpleTestCase):

    def test_env_bool_reconnait_les_valeurs_valides(self):

        valeurs = {
            "true": True,
            "TRUE": True,
            "1": True,
            "yes": True,
            "on": True,
            "false": False,
            "FALSE": False,
            "0": False,
            "no": False,
            "off": False,
        }

        for valeur, resultat_attendu in valeurs.items():
            with self.subTest(valeur=valeur):
                with patch.dict(
                    os.environ,
                    {"TEST_BOOL": valeur},
                    clear=True,
                ):
                    self.assertIs(
                        env_bool("TEST_BOOL"),
                        resultat_attendu,
                    )

    def test_env_bool_utilise_la_valeur_par_defaut(self):

        with patch.dict(os.environ, {}, clear=True):
            self.assertIs(
                env_bool("TEST_BOOL", default=True),
                True,
            )

    def test_env_bool_refuse_une_valeur_invalide(self):

        with patch.dict(
            os.environ,
            {"TEST_BOOL": "peut-etre"},
            clear=True,
        ):
            with self.assertRaises(ImproperlyConfigured):
                env_bool("TEST_BOOL")

    def test_env_int_reconnait_un_entier_valide(self):

        with patch.dict(
            os.environ,
            {"TEST_INT": "120"},
            clear=True,
        ):
            self.assertEqual(
                env_int(
                    "TEST_INT",
                    default=0,
                    minimum=0,
                ),
                120,
            )

    def test_env_int_utilise_la_valeur_par_defaut(self):

        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(
                env_int("TEST_INT", default=30),
                30,
            )

    def test_env_int_refuse_une_valeur_non_entiere(self):

        with patch.dict(
            os.environ,
            {"TEST_INT": "douze"},
            clear=True,
        ):
            with self.assertRaises(ImproperlyConfigured):
                env_int("TEST_INT")

    def test_env_int_respecte_la_valeur_minimale(self):

        with patch.dict(
            os.environ,
            {"TEST_INT": "-1"},
            clear=True,
        ):
            with self.assertRaises(ImproperlyConfigured):
                env_int("TEST_INT", minimum=0)

    def test_env_list_nettoie_et_ignore_les_elements_vides(self):

        with patch.dict(
            os.environ,
            {
                "TEST_LIST": (
                    " api.example.test, ,localhost,"
                    " https://frontend.example.test "
                )
            },
            clear=True,
        ):
            self.assertEqual(
                env_list("TEST_LIST"),
                [
                    "api.example.test",
                    "localhost",
                    "https://frontend.example.test",
                ],
            )

    def test_env_list_utilise_et_parse_la_valeur_par_defaut(self):

        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(
                env_list(
                    "TEST_LIST",
                    default="127.0.0.1, localhost",
                ),
                [
                    "127.0.0.1",
                    "localhost",
                ],
            )

    def test_database_config_utilise_sqlite_sans_database_url(self):

        base_dir = Path("application") / "backend"

        with patch.dict(os.environ, {}, clear=True):
            configuration = database_config(base_dir)

        self.assertEqual(
            configuration,
            {
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": base_dir / "db.sqlite3",
                }
            },
        )

    def test_database_config_parse_postgresql_et_configure_les_connexions(
        self
    ):

        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": (
                    "postgresql://test_user:test_password@"
                    "db.example.test:5432/test_database"
                    "?sslmode=require"
                ),
                "DB_CONN_MAX_AGE": "120",
            },
            clear=True,
        ):
            configuration = database_config(
                Path("application") / "backend"
            )

        base_de_donnees = configuration["default"]

        self.assertEqual(
            base_de_donnees["ENGINE"],
            "django.db.backends.postgresql",
        )
        self.assertEqual(
            base_de_donnees["NAME"],
            "test_database",
        )
        self.assertEqual(
            base_de_donnees["HOST"],
            "db.example.test",
        )
        self.assertEqual(
            base_de_donnees["PORT"],
            5432,
        )
        self.assertEqual(
            base_de_donnees["CONN_MAX_AGE"],
            120,
        )
        self.assertIs(
            base_de_donnees["CONN_HEALTH_CHECKS"],
            True,
        )
        self.assertEqual(
            base_de_donnees["OPTIONS"]["sslmode"],
            "require",
        )

    def test_database_config_refuse_un_moteur_non_postgresql(self):

        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "sqlite:///base-interdite.sqlite3",
            },
            clear=True,
        ):
            with self.assertRaises(ImproperlyConfigured):
                database_config(
                    Path("application") / "backend"
                )

    def test_database_config_refuse_une_url_postgresql_incomplete(self):

        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": (
                    "postgresql://test_user:test_password@"
                    "db.example.test:5432"
                ),
            },
            clear=True,
        ):
            with self.assertRaises(ImproperlyConfigured):
                database_config(
                    Path("application") / "backend"
                )


class ProductionSettingsTests(SimpleTestCase):

    def test_static_root_est_configure(self):

        self.assertEqual(
            settings.STATIC_ROOT,
            settings.BASE_DIR / "staticfiles",
        )

    def test_whitenoise_suit_immediatement_security_middleware(self):

        security_middleware = (
            "django.middleware.security.SecurityMiddleware"
        )
        whitenoise_middleware = (
            "whitenoise.middleware.WhiteNoiseMiddleware"
        )

        position_security = settings.MIDDLEWARE.index(
            security_middleware
        )

        self.assertEqual(
            settings.MIDDLEWARE[position_security + 1],
            whitenoise_middleware,
        )

    def test_stockage_media_correspond_a_la_configuration(self):

        backend_attendu = (
            "config.media_storage.CloudinaryMediaStorage"
            if settings.USE_CLOUDINARY_MEDIA
            else "django.core.files.storage.FileSystemStorage"
        )

        self.assertEqual(
            settings.STORAGES["default"]["BACKEND"],
            backend_attendu,
        )

    def test_statiques_utilisent_whitenoise(self):

        self.assertEqual(
            settings.STORAGES["staticfiles"]["BACKEND"],
            (
                "whitenoise.storage."
                "CompressedManifestStaticFilesStorage"
            ),
        )
