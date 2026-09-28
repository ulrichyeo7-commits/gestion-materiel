from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Materiel
from .serializers import (
    DemandeCreationSerializer,
    DemandeSerializer,
    DemandeTraitementSerializer,
    ErreurSerializer,
    MaterielSerializer,
    UtilisateurConnecteSerializer,
)
from .services.demande_service import (
    ErreurDemande,
    creer_demande,
    lister_demandes_utilisateur,
    lister_toutes_demandes,
    traiter_demande,
)


class UtilisateurConnecteView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Consulter l'utilisateur connecté",
        description=(
            "Retourne l'identifiant, le nom d'utilisateur "
            "et le statut administrateur du compte authentifié."
        ),
        tags=["Authentification"],
        responses={
            status.HTTP_200_OK: (
                UtilisateurConnecteSerializer
            ),
        },
    )
    def get(self, request):

        utilisateur = request.user

        return Response(
            {
                "id": utilisateur.id,
                "username": utilisateur.username,
                "is_staff": utilisateur.is_staff,
            },
            status=status.HTTP_200_OK
        )


class MaterielListView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Lister les matériels disponibles",
        description=(
            "Retourne les matériels dont le stock est "
            "strictement supérieur à zéro."
        ),
        tags=["Matériels"],
        responses={
            status.HTTP_200_OK: (
                MaterielSerializer(many=True)
            ),
        },
    )
    def get(self, request):

        materiels = Materiel.objects.filter(
            quantite_disponible__gt=0
        )

        serializer = MaterielSerializer(
            materiels,
            many=True,
            context={
                "request": request
            }
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class DemandeListCreateView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        summary="Lister mes demandes",
        description=(
            "Retourne l'historique des demandes de "
            "l'utilisateur authentifié."
        ),
        tags=["Demandes"],
        responses={
            status.HTTP_200_OK: (
                DemandeSerializer(many=True)
            ),
        },
    )
    def get(self, request):

        demandes = (
            lister_demandes_utilisateur(
                request.user
            )
        )

        serializer = DemandeSerializer(
            demandes,
            many=True,
            context={
                "request": request
            }
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Créer une demande",
        description=(
            "Crée une demande contenant un ou plusieurs "
            "matériels et les quantités souhaitées."
        ),
        tags=["Demandes"],
        request=DemandeCreationSerializer,
        responses={
            status.HTTP_201_CREATED: DemandeSerializer,
            status.HTTP_400_BAD_REQUEST: ErreurSerializer,
        },
    )
    def post(self, request):

        serializer_entree = (
            DemandeCreationSerializer(
                data=request.data
            )
        )

        serializer_entree.is_valid(
            raise_exception=True
        )

        try:

            demande = creer_demande(
                utilisateur=request.user,
                lignes=(
                    serializer_entree
                    .validated_data["materiels"]
                )
            )

        except ErreurDemande as erreur:

            return Response(
                {
                    "erreur": str(erreur)
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                )
            )

        serializer_sortie = (
            DemandeSerializer(
                demande,
                context={
                    "request": request
                }
            )
        )

        return Response(
            serializer_sortie.data,
            status=status.HTTP_201_CREATED
        )


class AdminDemandeListView(APIView):

    permission_classes = [
        IsAdminUser
    ]

    @extend_schema(
        summary="Lister toutes les demandes",
        description=(
            "Retourne l'ensemble des demandes pour leur "
            "suivi par un administrateur."
        ),
        tags=["Administration"],
        responses={
            status.HTTP_200_OK: (
                DemandeSerializer(many=True)
            ),
        },
    )
    def get(self, request):

        demandes = lister_toutes_demandes()

        serializer = DemandeSerializer(
            demandes,
            many=True,
            context={
                "request": request
            }
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class AdminDemandeTraitementView(
    APIView
):

    permission_classes = [
        IsAdminUser
    ]

    @extend_schema(
        summary="Traiter une demande",
        description=(
            "Accepte ou refuse une demande en attente. "
            "L'acceptation met automatiquement le stock à jour."
        ),
        tags=["Administration"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": [
                            "ACCEPTER",
                            "REFUSER",
                        ],
                        "description": (
                            "Décision appliquée à la demande."
                        ),
                    },
                },
                "required": [
                    "action"
                ],
            },
        },
        responses={
            status.HTTP_200_OK: DemandeSerializer,
            status.HTTP_400_BAD_REQUEST: ErreurSerializer,
            status.HTTP_404_NOT_FOUND: ErreurSerializer,
        },
    )
    def patch(
        self,
        request,
        id_demande
    ):

        serializer = (
            DemandeTraitementSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        action = (
            serializer.validated_data[
                "action"
            ]
        )

        try:

            demande = traiter_demande(
                id_demande=id_demande,
                action=action
            )

        except LookupError as erreur:

            return Response(
                {
                    "erreur": str(erreur)
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                )
            )

        except ErreurDemande as erreur:

            return Response(
                {
                    "erreur": str(erreur)
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                )
            )

        serializer_sortie = (
            DemandeSerializer(
                demande,
                context={
                    "request": request
                }
            )
        )

        return Response(
            serializer_sortie.data,
            status=status.HTTP_200_OK
        )


class AdminMaterielListCreateView(
    APIView
):

    permission_classes = [
        IsAdminUser
    ]

    @extend_schema(
        summary="Lister tous les matériels",
        description=(
            "Retourne le catalogue complet, y compris les "
            "matériels dont le stock est épuisé."
        ),
        tags=["Administration"],
        responses={
            status.HTTP_200_OK: (
                MaterielSerializer(many=True)
            ),
        },
    )
    def get(self, request):

        materiels = (
            Materiel.objects
            .all()
            .order_by("nom")
        )

        serializer = MaterielSerializer(
            materiels,
            many=True,
            context={
                "request": request
            }
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Ajouter un matériel",
        description=(
            "Ajoute un matériel au catalogue. Utilisez une "
            "requête multipart/form-data pour envoyer une photo."
        ),
        tags=["Administration"],
        request=MaterielSerializer,
        responses={
            status.HTTP_201_CREATED: MaterielSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Données de matériel invalides."
            ),
        },
    )
    def post(self, request):

        serializer = MaterielSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        materiel = serializer.save()

        serializer_sortie = (
            MaterielSerializer(
                materiel,
                context={
                    "request": request
                }
            )
        )

        return Response(
            serializer_sortie.data,
            status=status.HTTP_201_CREATED
        )


@extend_schema_view(
    put=extend_schema(
        summary="Remplacer les caractéristiques d'un matériel",
        description=(
            "Remplace toutes les caractéristiques modifiables "
            "du matériel sélectionné."
        ),
        tags=["Administration"],
    ),
    patch=extend_schema(
        summary="Modifier les caractéristiques d'un matériel",
        description=(
            "Met à jour uniquement les caractéristiques fournies "
            "pour le matériel sélectionné."
        ),
        tags=["Administration"],
    ),
)
class AdminMaterielUpdateView(
    UpdateAPIView
):

    permission_classes = [
        IsAdminUser
    ]

    queryset = Materiel.objects.all()

    serializer_class = MaterielSerializer

    lookup_url_kwarg = "id_materiel"
