import os
from pathlib import PurePosixPath
from uuid import uuid4

import cloudinary
import cloudinary.uploader
from django.core.files.storage import Storage


class CloudinaryMediaStorage(Storage):
    """Stockage Django minimal pour les images envoyées vers Cloudinary."""

    def __init__(self, base_folder=None):
        self.base_folder = (
            base_folder
            or os.getenv(
                "CLOUDINARY_MEDIA_FOLDER",
                "gestion-materiel",
            )
        ).strip("/")

    def _save(self, name, content):
        chemin = PurePosixPath(name)
        dossier_relatif = str(chemin.parent)

        morceaux_dossier = [
            morceau
            for morceau in (
                self.base_folder,
                "" if dossier_relatif == "." else dossier_relatif,
            )
            if morceau
        ]

        dossier = "/".join(morceaux_dossier)

        public_id = (
            f"{chemin.stem}-{uuid4().hex}"
        )

        if hasattr(content, "seek"):
            content.seek(0)

        resultat = cloudinary.uploader.upload(
            content,
            folder=dossier or None,
            public_id=public_id,
            resource_type="image",
            overwrite=False,
        )

        return resultat["public_id"]

    def delete(self, name):
        if not name:
            return

        cloudinary.uploader.destroy(
            name,
            resource_type="image",
            invalidate=True,
        )

    def exists(self, name):
        # Les noms envoyés sur Cloudinary sont rendus uniques dans _save().
        # Éviter un appel réseau ici garde Storage.save() rapide.
        return False

    def url(self, name):
        if not name:
            return ""

        return cloudinary.CloudinaryImage(
            name
        ).build_url(
            secure=True
        )
