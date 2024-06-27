# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from .models import Voter
# from .serializers import VoterSerializer

# class VoterRegisterView(APIView):
#     def post(self, request):
#         serializer = VoterSerializer(data=request.data)
#         if serializer.is_valid():
#             voter = serializer.save()
#             return Response(VoterSerializer(voter).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Voter
from .serializers import VoterSerializer

class VoterRegisterView(APIView):
    def post(self, request):
        serializer = VoterSerializer(data=request.data)
        if serializer.is_valid():
            voter = serializer.save()
            return Response(VoterSerializer(voter).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
