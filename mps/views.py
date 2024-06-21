from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MemberOfParliament
from .serializers import MemberOfParliamentSerializer

class MpRegisterView(APIView):
    def post(self, request):
        serializer = MemberOfParliamentSerializer(data=request.data)
        if serializer.is_valid():
            mp = serializer.save()
            return Response(MemberOfParliamentSerializer(mp).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
