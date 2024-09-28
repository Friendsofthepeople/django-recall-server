from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recall_server.issues.views import IssueViewSet


router = DefaultRouter()
router.register(r'', IssueViewSet)

urlpatterns = [
        path('', include(router.urls)),
        ]
