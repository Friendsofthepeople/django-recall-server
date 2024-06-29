from rest_framework import serializers

from recall_server.polling_station.models import PollingStation


class PollingStationSerializer(serializers.ModelSerializer):
    """
    Serializers voters polling station and location while
    keeping track of registered voters count
    """

    class Meta:
        model = PollingStation
        fields = ["name", "location"]
        read_only_fields = ["registeredVoters_count"]

    def create(self, validated_data):
        return PollingStation.objects.create(**validated_data)
