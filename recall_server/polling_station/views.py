from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from recall_server.polling_station.models import PollingStation
from recall_server.polling_station.serializers import PollingStationSerializer


class PollingStationView(APIView):
    """
    Endpoint to add polling station
    """

    def post(self, request):
        serializer = PollingStationSerializer(data=request.data)
        if serializer.is_valid():
            pollingStation = serializer.save()
            return Response(
                PollingStationSerializer(pollingStation).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
