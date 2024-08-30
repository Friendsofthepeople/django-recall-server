from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from recall_server.voting.models import PublicVote, OfficialVote


class PublicVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicVote
        fields = ['bill', 'user', 'vote', 'comment', 'date']


class OfficialVoteSerialzer(serializers.ModelSerializers):
    class Meta:
        model = OfficialVote
        fields = ['bill', 'legislator', 'vote']
