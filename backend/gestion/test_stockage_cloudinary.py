from io import BytesIO
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from config.media_storage import CloudinaryMediaStorage


class CloudinaryMediaStorageTests(SimpleTestCase):

    @patch("config.media_storage.cloudinary.uploader.upload")
    def test_save_envoie_image_dans_dossier_cloudinary(
        self,
        upload_mock,
    ):
        upload_mock.return_value = {
            "public_id": (
                "gestion-materiel/materiels/"
                "ordinateur-identifiant"
            )
        }

        stockage = CloudinaryMediaStorage(
            base_folder="gestion-materiel"
        )

        contenu = BytesIO(b"image-fictive")

        nom = stockage._save(
            "materiels/ordinateur.jpg",
            contenu,
        )

        self.assertEqual(
            nom,
            (
                "gestion-materiel/materiels/"
                "ordinateur-identifiant"
            ),
        )

        arguments = upload_mock.call_args.kwargs

        self.assertEqual(
            arguments["folder"],
            "gestion-materiel/materiels",
        )
        self.assertEqual(
            arguments["resource_type"],
            "image",
        )
        self.assertFalse(
            arguments["overwrite"]
        )

    @patch("config.media_storage.cloudinary.CloudinaryImage")
    def test_url_retourne_une_url_https_cloudinary(
        self,
        image_mock,
    ):
        instance = Mock()
        instance.build_url.return_value = (
            "https://res.cloudinary.com/demo/image/upload/photo"
        )
        image_mock.return_value = instance

        stockage = CloudinaryMediaStorage()

        url = stockage.url(
            "gestion-materiel/materiels/photo"
        )

        self.assertEqual(
            url,
            (
                "https://res.cloudinary.com/demo/"
                "image/upload/photo"
            ),
        )

        instance.build_url.assert_called_once_with(
            secure=True
        )

    @patch("config.media_storage.cloudinary.uploader.destroy")
    def test_delete_supprime_image_cloudinary(
        self,
        destroy_mock,
    ):
        stockage = CloudinaryMediaStorage()

        stockage.delete(
            "gestion-materiel/materiels/photo"
        )

        destroy_mock.assert_called_once_with(
            "gestion-materiel/materiels/photo",
            resource_type="image",
            invalidate=True,
        )
