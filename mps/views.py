from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MemberOfParliament
from .serializers import MemberOfParliamentSerializer
import json
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

class MpRegisterView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = MemberOfParliamentSerializer(data=request.data)
        if serializer.is_valid():
            mp = serializer.save()
            return Response(MemberOfParliamentSerializer(mp).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class ImportDataView(APIView):
#     def post(self, request):
#         file_path = "/code/mps/mps.json"
#         print(f"Importing data from {file_path}")
#         with open(file_path, 'r') as file:
#             data = json.load(file)
#             print(f"Found {len(data)} MPs")
#             # print(data)
        
#         serializer = MemberOfParliamentSerializer(data=data, many=True)
#         if serializer.is_valid():
#             print(f"Validating {len(serializer.validated_data)} MPs")
#             serializer.save()
#             return JsonResponse({'message': 'Data imported successfully'}, status=201, safe=False)
#         return JsonResponse(serializer.errors, status=400, safe=False)

class MpListView(generics.ListAPIView):
    # permission_classes = [IsAuthenticated]
    queryset = MemberOfParliament.objects.all()
    serializer_class = MemberOfParliamentSerializer
