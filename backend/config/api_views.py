from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


@extend_schema_view(
    post=extend_schema(
        summary="Se connecter et obtenir des jetons JWT",
        description=(
            "Vérifie les identifiants et retourne un jeton "
            "d'accès ainsi qu'un jeton de rafraîchissement."
        ),
        tags=["Authentification"],
    )
)
class ConnexionJWTView(TokenObtainPairView):
    pass


@extend_schema_view(
    post=extend_schema(
        summary="Rafraîchir le jeton d'accès",
        description=(
            "Échange un jeton de rafraîchissement valide "
            "contre un nouveau jeton d'accès."
        ),
        tags=["Authentification"],
    )
)
class RafraichissementJWTView(TokenRefreshView):
    pass
