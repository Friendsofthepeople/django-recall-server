from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recall_server.laws.views import (
    BillViewSet,
    CommentViewSet,
    BillRevisionViewSet,
    BillAmendmentViewSet,
    PublishedLawViewSet
)


router = DefaultRouter()
router.register(r'bills', BillViewSet, basename='bills')
router.register(r'comments', CommentViewSet, basename='comments')
router.register(r'revisions', BillRevisionViewSet, basename='revisions')
router.register(r'amendments', BillAmendmentViewSet, basename='amendments')
router.register(r'published-laws', PublishedLawViewSet, basename='published-laws')

urlpatterns = [
    path('', include(router.urls)),
]
