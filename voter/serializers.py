from rest_framework import serializers
from .models import Voter
from django.contrib.auth.hashers import make_password

class VoterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voter
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'tokenized_id', 'created_at']
        read_only_fields = ['tokenized_id', 'created_at']

        extra_kwargs = {'password': {'write_only': True}}


    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        # return Voter.objects.create(**validated_data)
        return super().create(validated_data)
