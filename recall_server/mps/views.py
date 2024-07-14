"""
Custom views for the `mps` Django app.
"""

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MemberOfParliament
from .serializers import MemberOfParliamentSerializer


class MpRegisterView(APIView):
    """
    Custom, class-based API dispatcher for the `voter.Voter` model.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MemberOfParliamentSerializer(data=request.data)
        if serializer.is_valid():
            mp = serializer.save()
            return Response(
                MemberOfParliamentSerializer(mp).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MpListView(generics.ListAPIView):
    """
    Custom, class-based API list view for the `voter.Voter` model.
    """

    queryset = MemberOfParliament.objects.all()
    serializer_class = MemberOfParliamentSerializer
