from rest_framework import viewsets, filters
from django.db.models import Count, Q
# from rest_framework import action
from rest_framework.response import Response

from recall_server.voting.serializers import(
        PublicVoteSerializer,
        OfficialVoteSerializer,
        VoteStatsSerializer
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


class VoteStatsViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        bill_id = self.kwargs.get('bill_id')
        stats = PublicVote.objects.filter(bill_id=bill_id).values\
                ('county__name').annotate(
                        yes_votes=Count('id', filter=Q(vote='yes')),
                        no_votes=Count('id', filter=Q(vote='no')),
                        abstain_votes=Count('id', filter=Q(vote='abstain')),
                        total_votes=Count('id')
                        ).order_by('-total_votes')
        serializer = VoteStatsSerializer(stats, many=True)
        return Response(serializer.data)
