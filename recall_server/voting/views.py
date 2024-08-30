from rest_framework import viewsets, filters
# from rest_framework import action
# from rest_framework.response import Response

from recall_server.voting.serializers import(
        PublicVoteSerializer,
        OfficialVoteSerializer
        )
from recall_server.voting.models import PublicVote, OfficialVote


class PublicVoteViewSet(viewsets.ModelViewSet):
    """
    Keeps track of users votes and comments on proposed bills
    """
    queryset = PublicVote.objects.all()
    serializer_class = PublicVoteSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OfficialVoteViewSet(viewsets.ModelViewSet):
    """
    Keeps trak of how legislators voted for various bills
    """
    queryset = OfficialVote.objects.all()
    serializer_class = OfficialVoteSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
