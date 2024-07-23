"""
Model serializers for the `polling_station` Django app.
"""

from recall_server.polling_station.models import PollingStation
from rest_framework import serializers


class PollingStationSerializer(serializers.ModelSerializer):
    """
    Serializer to serialize/deserialize instances of the `PollingStation` model.

    Serializers voters polling station and location while
    keeping track of registered voters count.
    """

    class Meta:
        model = PollingStation
        fields = ["name", "location"]
        read_only_fields = ["registeredVoters_count"]

    def create(self, validated_data):
        return PollingStation.objects.create(**validated_data)
