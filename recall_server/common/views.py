"""
Custom views for the `common` Django app.
"""

from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from common.serializers import ConstituencySerializer, CountySerializer


class CountyView(APIView):
    """
    Custom, class-based API dispatcher for the `common.County` model.
    """

    def post(self, request):
        serializer = CountySerializer(data=request.data)
        if serializer.is_valid():
            county = serializer.save()
            return Response(CountySerializer(county).data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


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
                status=HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
