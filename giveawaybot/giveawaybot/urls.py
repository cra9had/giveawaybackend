from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

app_name = "giveaway"

urlpatterns = [
    path('api/', include('webapp.urls')),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
         "api/swagger/",
         SpectacularSwaggerView.as_view(url_name="schema"),
         name="swagger",
     ),
    path(
         "api/redoc/",
         SpectacularRedocView.as_view(url_name="schema"),
         name="redoc",
     ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
