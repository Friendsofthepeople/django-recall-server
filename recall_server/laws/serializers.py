from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from recall_server.laws.models import Bill, House, Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['user', 'comment', 'created_at']


class BillSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Bill
        fields = (
                'title',
                'description',
                'bill_number',
                'house',
                'stage',
                'status',
                'deadline_for_voting',
                'comments'
                )


class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = ('house_id', 'name')
