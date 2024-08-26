from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from recall_server.laws.models import Bill, House


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = (
                'title',
                'description',
                'bill_number',
                'house',
                'stage',
                'status',
                'deadline_for_voting',
                'county'
                )


class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = ('house_id', 'name')
