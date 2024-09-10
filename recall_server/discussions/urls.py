from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recall_server.discussions.views import (
        PostViewSet,
        ResponseViewSet
        )


router = DefaultRouter()
router.register(r'', PostViewSet)
router.register(r'', ResponseViewSet)

urlpatterns = [
        path('', include(router.urls)),
        ]
