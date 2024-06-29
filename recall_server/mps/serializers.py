from rest_framework import serializers

from .models import MemberOfParliament


class MemberOfParliamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberOfParliament
        fields = [
            "id",
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
