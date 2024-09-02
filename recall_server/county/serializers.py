"""
Model serializers for `county` Django app.
"""

from rest_framework import serializers

from recall_server.county.models import Constituency, County, Senator, MCA
# from recall_server.voting.serializers import 
from recall_server.voting.serializers import OfficialVoteSerializer


class CountySerializer(serializers.ModelSerializer):
    """
    Serializes a county to keep track of constituencies.
    """

    class Meta:
        model = County
        fields = ["name", "county_number"]
        read_only_fields = ["constituency_count"]

    def create(self, validated_data):
        return County.objects.create(**validated_data)


class SenatorSerializer(serializers.ModelSerializer):
    """
    Serializes a senator to keep track of their senate activities
    """
    voting_history = OfficialVoteSerializer(many=True, source='voting_history')

    class Meta:
        model = Senator
        fields = ["name", "county", "bill_proposed", "voting_history"]

    def create(self, validated_data):
        return Senator.objects.create(**validated_data)


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


class MCASerializer(serializers.ModelSerializer):
    """
    Keeps track of MCA voting history
    """
    voting_history = OfficialVoteSerializer(many=True, source='voting_history')

    class Meta:
        model = MCA
        fields = ["name", "ward", "voting_history", "constituency"]

    def create(self, validated_data):
        return MCA.objects.create(**validated_data)
