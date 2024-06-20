from rest_framework import serializers
from .models import Voter

class VoterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voter
        fields = ['id', 'first_name', 'last_name', 'email', 'tokenized_id', 'created_at']
        read_only_fields = ['tokenized_id', 'created_at']

    def create(self, validated_data):
        return Voter.objects.create(**validated_data)
