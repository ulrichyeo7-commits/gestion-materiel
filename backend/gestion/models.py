from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Materiel(models.Model):

    nom = models.CharField(max_length=150)

    description = models.TextField(
        blank=True
    )

    categorie = models.CharField(
        max_length=100,
        blank=True
    )

    photo = models.ImageField(
        upload_to="materiels/",
        blank=True,
        null=True
    )

    quantite_disponible = models.PositiveIntegerField(
        default=0
    )

    date_creation = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.nom


class Demande(models.Model):

    class Statut(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        ACCEPTEE = "ACCEPTEE", "Acceptée"
        REFUSEE = "REFUSEE", "Refusée"

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="demandes"
    )

    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.EN_ATTENTE
    )

    date_demande = models.DateTimeField(
        auto_now_add=True
    )

    date_traitement = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Demande #{self.id} - {self.utilisateur}"


class LigneDemande(models.Model):

    demande = models.ForeignKey(
        Demande,
        on_delete=models.CASCADE,
        related_name="lignes"
    )

    materiel = models.ForeignKey(
        Materiel,
        on_delete=models.CASCADE,
        related_name="lignes_demandes"
    )

    quantite = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["demande", "materiel"],
                name="unique_materiel_par_demande"
            )
        ]

    def __str__(self):
        return (
            f"{self.materiel.nom} "
            f"x {self.quantite}"
        )