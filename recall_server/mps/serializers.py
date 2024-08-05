"""
Model serializers for the `mps` Django app.
"""

from rest_framework import serializers

from .models import MemberOfParliament


class MemberOfParliamentSerializer(serializers.ModelSerializer):
    """
    Serializer to serialize/deserialize instances of the `MemberOfParliament` model.
    """

    class Meta:
        model = MemberOfParliament
        fields = [
            "image",
            "name",
            "county",
            "constituency",
            "party",
            "tokenized_id",
            "created_at",
        ]
        read_only_fields = ["tokenized_id", "created_at"]

    def create(self, validated_data):
        return MemberOfParliament.objects.create(**validated_data)
