from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recall_server.laws.views import BillViewSet, DiscussionViewSet


router = DefaultRouter()
router.register(r'', BillViewSet, basename='laws')
router.register(r'', DiscussionViewSet, basename='discussions')

urlpatterns = [
        path('', include(router.urls)),
        ]
