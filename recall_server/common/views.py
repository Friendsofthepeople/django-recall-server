from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from county.models import *
from county.serializers import *


class CountyView(APIView):
    def post(self, request):
        serializer = CountySerializer(data=request.data)
        if serializer.is_valid():
            county = serializer.save()
            return Response(
                    CountySerializer(county).data,
                    status=HTTP_201_CREATED
                    )
        return Response(
                serializer.errors,
                status=HTTP_400_BAD_REQUEST
                )


class ConstituencyView(APIView):
    def post(self, request):
        serializer = ConstituencySerializer(data=request.data)
        if serializer.is_valid():
            constituency = serializer.save()
            return Response(
                    ConstituencySerializer(constituency).data,
                    status=HTTP_201_CREATED
                    )
        return Response(
                serializer.errors,
                status=HTTP_400_BAD_REQUEST
                )
