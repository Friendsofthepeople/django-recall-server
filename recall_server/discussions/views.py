from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from recall_server.discussions.models import Post, Response
from recall_server.discussions.serializers import (
        PostSerializer,
        ResponseSerializer
        )


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ResponseViewSet(viewsets.ModelViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
