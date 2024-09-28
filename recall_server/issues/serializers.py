from rest_framework import serializers

from recall_server.issues.models import Issue

class IssueSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Issue
        fields = [
                'id',
                'serial',
                'title',
                'content',
                'author',
                'status',
                'deadline',
                'created_at',
                ]
 