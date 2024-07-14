"""
Custom views for the `pilling_station` Django app.
"""

from recall_server.polling_station.serializers import PollingStationSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class PollingStationView(APIView):
    """
    Endpoint to add polling station.
    """

    def post(self, request):
        serializer = PollingStationSerializer(data=request.data)
        if serializer.is_valid():
            polling_station = serializer.save()
            return Response(
                PollingStationSerializer(polling_station).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
