"""
Model serializers for the `mps` Django app.
"""

from rest_framework import serializers

from .models import MemberOfParliament
from recall_server.voting.serializers import OfficialVoteSerializer


class MemberOfParliamentSerializer(serializers.ModelSerializer):
    """
    Serializer to serialize/deserialize instances of the `MemberOfParliament` model.
    """
    voting_history = OfficialVoteSerializer(many=True, source='voting_history')

    class Meta:
        model = MemberOfParliament
        fields = [
            "image",
            "name",
            "county",
            "constituency",
            "party",
            "voting_history",
            "tokenized_id",
            "created_at",
        ]
        read_only_fields = ["tokenized_id", "created_at"]

    def create(self, validated_data):
        return MemberOfParliament.objects.create(**validated_data)
