from rest_framework import serializers

from recall_server.discussions.models import (
        Post,
        Response
        )


class RecursiveResponseSerializer(serializers.ModelSerializer):
    # Handles responses by displaying them in a nested structure
    replies = serializers.SerializerMethodField()
    author = serializers.StringRelatedField()

    class Meta:
        model = Response
        fields = [
                'id',
                'response',
                'author',
                'created_at',
                'replies'
                ]

    def get_replies(self, obj):
        if obj.replies.exists():
            return RecursiveResponseSerializer(
                    obj.replies.all(),
                    many=True
                    ).data
        return []


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    responses = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
                'id',
                'title',
                'content',
                'author',
                'created_at',
                'responses'
                ]

    def get_responses(self, obj):
        responses = obj.responses.filter(parent=None)
        return RecursiveResponseSerializer(responses, many=True).data


class ResponseSerializer(serializers.ModelSerializer):
    # Handles individual response creation
    
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Response
        fields = [
                'id',
                'post',
                'response',
                'parent',
                'author',
                'created_at',
                'updated_at'
                ]
        read_only_fields = ['author']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
