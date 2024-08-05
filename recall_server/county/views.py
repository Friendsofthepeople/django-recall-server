"""
Custom views for the `county` Django app.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from county.serializers import ConstituencySerializer, CountySerializer


class CountyView(APIView):
    """
    Custom, class-based API dispatcher for the `common.County` model.
    """

    def post(self, request):
        serializer = CountySerializer(data=request.data)
        if serializer.is_valid():
            county = serializer.save()
            return Response(
                CountySerializer(county).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConstituencyView(APIView):
    """
    Custom, class-based API dispatcher for the `common.Constituency` model.
    """

    def post(self, request):
        serializer = ConstituencySerializer(data=request.data)
        if serializer.is_valid():
            constituency = serializer.save()
            return Response(
                ConstituencySerializer(constituency).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
