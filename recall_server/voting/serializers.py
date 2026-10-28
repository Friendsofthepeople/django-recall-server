from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.contenttypes.models import ContentType

from recall_server.voting.models import PublicVote, OfficialVote


class PublicVoteSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    bill_title = serializers.SerializerMethodField()
    region_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PublicVote
        fields = [
            'id', 
            'bill', 
            'bill_title',
            'user', 
            'user_name',
            'vote', 
            'comment', 
            'region',
            'region_name',
            'date'
        ]
        
    def get_user_name(self, obj):
        if hasattr(obj.user, 'get_full_name'):
            return obj.user.get_full_name()
        return str(obj.user)
        
    def get_bill_title(self, obj):
        return obj.bill.title
        
    def get_region_name(self, obj):
        return obj.region.name


class OfficialVoteSerializer(serializers.ModelSerializer):
    legislator_name = serializers.SerializerMethodField()
    legislator_type = serializers.SerializerMethodField()
    bill_title = serializers.SerializerMethodField()
    
    class Meta:
        model = OfficialVote
        fields = [
            'id',
            'bill', 
            'bill_title',
            'legislator_content_type',
            'legislator_object_id',
            'legislator_name',
            'legislator_type',
            'vote',
            'date',
            'session_name',
            'reason'
        ]
        
    def get_legislator_name(self, obj):
        return obj.get_legislator_name()
        
    def get_legislator_type(self, obj):
        return obj.get_legislator_type()
        
    def get_bill_title(self, obj):
        return obj.bill.title


class VoteStatsSerializer(serializers.Serializer):
    county = serializers.CharField()
    yes_votes = serializers.IntegerField()
    no_votes = serializers.IntegerField()
    abstain_votes = serializers.IntegerField()
    total_votes = serializers.IntegerField()
    yes_percentage = serializers.FloatField()
    no_percentage = serializers.FloatField()
    abstain_percentage = serializers.FloatField()


class VoteComparisonSerializer(serializers.Serializer):
    """Serializer for comparing public opinion with official votes"""
    bill_id = serializers.UUIDField()
    bill_title = serializers.CharField()
    public_opinion = serializers.DictField()
    official_votes = serializers.DictField()
    alignment_percentage = serializers.FloatField()
    
    
class LegislatorVotingRecordSerializer(serializers.Serializer):
    """Serializer for legislator voting records and alignment with public opinion"""
    legislator_id = serializers.CharField()
    legislator_name = serializers.CharField()
    legislator_type = serializers.CharField()
    total_votes = serializers.IntegerField()
    yes_votes = serializers.IntegerField()
    no_votes = serializers.IntegerField()
    abstain_votes = serializers.IntegerField()
    public_alignment_percentage = serializers.FloatField()
