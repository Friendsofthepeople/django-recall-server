"""
Custom views for the `voter` Django app.
"""

from recall_server.voter.serializers import VoterSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class VoterRegisterView(APIView):
    """
    Custom, class-based API dispatcher for the `voter.Voter` model.
    """

    def post(self, request):
        serializer = VoterSerializer(data=request.data)
        if serializer.is_valid():
            voter = serializer.save()
            return Response(VoterSerializer(voter).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
