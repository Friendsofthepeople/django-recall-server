"""
Model serializers for `county` Django app.
"""

from rest_framework import serializers

from county.models import Constituency, County


class CountySerializer(serializers.ModelSerializer):
    """
    Serializes a county to keep track of constituencies.
    """

    class Meta:
        model = County
        fields = ["name"]
        read_only_fields = ["constituency_count"]

    def create(self, validated_data):
        return County.objects.create(**validated_data)


class ConstituencySerializer(serializers.ModelSerializer):
    """
    Serializes a constituency to keep track of mp, polling station.
    """

    class Meta:
        model = Constituency
        fields = ["name", "mp", "polling_station"]
        read_only_fields = ["registeredvoter_count"]

    def create(self, validated_data):
        return Constituency.objects.create(**validated_data)
