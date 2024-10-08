from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recall_server.laws.views import BillViewSet, CommentViewSet


router = DefaultRouter()
router.register(r'', BillViewSet, basename='laws')
router.register(r'', CommentViewSet, basename='comments')

urlpatterns = [
        path('', include(router.urls)),
        ]
