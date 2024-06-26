from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="Member of Parliament Recall System",
        default_version="v1.0",
        description="""A Django server for managing the verification of constituents
        ,publishing of representative information, and signing to recall them.""",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT license"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/voter/", include("recall_server.voter.urls")),
    path("api/mps/", include("recall_server.mps.urls")),
    path("api/recall/", include("recall_server.recall.urls")),
    path(
        "docs/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "docs/redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path("auth/", include("djoser.urls.base")),
    path("auth/", include("djoser.urls.authtoken")),
    path("auth/", include("djoser.social.urls")),
]
