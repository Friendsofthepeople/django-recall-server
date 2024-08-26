from django.urls import path, include

from rest_framework.routers import DefaultRouter

from recall_server.laws.views import BillViewSet


router = DefaultRouter()
router.register(r'', BillViewSet, basename='laws')

urlpatterns = [
        path('', include(router.urls)),
        ]
