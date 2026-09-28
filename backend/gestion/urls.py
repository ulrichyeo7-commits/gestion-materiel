from django.urls import path

from .views import (
    AdminDemandeListView,
    AdminDemandeTraitementView,
    AdminMaterielListCreateView,
    AdminMaterielUpdateView,
    DemandeListCreateView,
    MaterielListView,
    UtilisateurConnecteView,
)


urlpatterns = [
    path(
        "auth/me/",
        UtilisateurConnecteView.as_view(),
        name="utilisateur-connecte"
    ),

    path(
        "materiels/",
        MaterielListView.as_view(),
        name="materiel-list"
    ),

    path(
        "demandes/",
        DemandeListCreateView.as_view(),
        name="demande-list-create"
    ),

    path(
        "admin/demandes/",
        AdminDemandeListView.as_view(),
        name="admin-demande-list"
    ),

    path(
        "admin/demandes/<int:id_demande>/",
        AdminDemandeTraitementView.as_view(),
        name="admin-demande-traitement"
    ),

    path(
        "admin/materiels/",
        AdminMaterielListCreateView.as_view(),
        name="admin-materiel-list-create"
    ),

    path(
        "admin/materiels/<int:id_materiel>/",
        AdminMaterielUpdateView.as_view(),
        name="admin-materiel-update"
    ),
]
