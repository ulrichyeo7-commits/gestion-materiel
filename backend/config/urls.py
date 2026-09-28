from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from .api_views import (
    ConnexionJWTView,
    RafraichissementJWTView,
)


urlpatterns = [
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="api-schema"
    ),

    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="api-schema"
        ),
        name="api-swagger-ui"
    ),

    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "api/",
        include("gestion.urls")
    ),

    path(
        "api/auth/login/",
        ConnexionJWTView.as_view(),
        name="token-obtain-pair"
    ),

    path(
        "api/auth/refresh/",
        RafraichissementJWTView.as_view(),
        name="token-refresh"
    ),

    path(
        "api-auth/",
        include("rest_framework.urls")
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
