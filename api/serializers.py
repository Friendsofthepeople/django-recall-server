from rest_framework import serializers
from .models import Diaspora, County, PollingStation

class DiasporaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diaspora
        fields = '__all__'


class  CountySerializer(serializers.ModelSerializer):
    class Meta:
        model = County
        fields = '__all__'
    
class PollingStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollingStation
        fields = '__all__'