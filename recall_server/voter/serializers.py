"""
Model serializers for the `voter` Django app.
"""

from django.contrib.auth.hashers import make_password
from recall_server.voter.models import Voter
from rest_framework import serializers


class VoterSerializer(serializers.ModelSerializer):
    """
    Serializer to serialize/deserialize instances of the `Voter` model.
    """

    class Meta:
        model = Voter
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "tokenized_id",
            "created_at",
        ]
        read_only_fields = ["tokenized_id", "created_at"]

        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)
