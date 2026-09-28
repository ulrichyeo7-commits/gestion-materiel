from django.contrib import admin

from .models import (
    Materiel,
    Demande,
    LigneDemande
)


@admin.register(Materiel)
class MaterielAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "nom",
        "categorie",
        "quantite_disponible",
    )


class LigneDemandeInline(admin.TabularInline):
    model = LigneDemande
    extra = 0


@admin.register(Demande)
class DemandeAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "utilisateur",
        "statut",
        "date_demande",
        "date_traitement",
    )

    inlines = [
        LigneDemandeInline
    ]


@admin.register(LigneDemande)
class LigneDemandeAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "demande",
        "materiel",
        "quantite",
    )