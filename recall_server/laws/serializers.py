from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from recall_server.laws.models import Bill, House, Discussion


class BillSerializer(serializers.ModelSerializer):
    total_votes = serializers.SerializerMethodField()
    yes_votes = serializers.SerializerMethodField()
    no_votes = serializers.SerializerMethodField()
    abstain_votes = serializers.SerializerMethodField()

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
                'county'
                )


class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = ('house_id', 'name')


class DiscussionSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Discussion
        fields = [
                'bill',
                'user',
                'comment',
                'parent',
                'created_at',
                'replies'
                ]

    def get_replies(self, obj):
        if obj.replies.exists():
            return DiscussionSerializer(
                    obj.replies.all(),
                    many=True).data
        return None
