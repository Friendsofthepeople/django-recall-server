from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Recall
from .serializers import RecallSerializer

class RecallCreateView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        recalls = Recall.objects.all()
        serializer = RecallSerializer(recalls, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RecallSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RecallDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Recall.objects.get(pk=pk)
        except Recall.DoesNotExist:
            return None

    def get(self, request, pk):
        recall = self.get_object(pk)
        if recall is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = RecallSerializer(recall)
        return Response(serializer.data)

    def put(self, request, pk):
        recall = self.get_object(pk)
        if recall is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = RecallSerializer(recall, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        recall = self.get_object(pk)
        if recall is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        recall.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
