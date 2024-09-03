"""
URL config for the 'voting' Django app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recall_server.voting.views import(
        PublicVoteViewSet,
        OfficialVoteViewSet,
        VoteStatsViewSet
        )


router = DefaultRouter()
router.register(r'', PublicVoteViewSet)
router.register(r'', OfficialVoteViewSet)
router.register(r'votestats', VoteStatsViewSet, basename='votestats')

urlpatterns = [
        path('', include(router.urls)),
        ]
