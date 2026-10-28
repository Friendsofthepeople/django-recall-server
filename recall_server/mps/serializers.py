"""
Model serializers for the `mps` Django app.
"""

from rest_framework import serializers

from recall_server.mps.models import MemberOfParliament
from recall_server.voting.serializers import OfficialVoteSerializer
from recall_server.laws.serializers import BillSerializer


class MemberOfParliamentSerializer(serializers.ModelSerializer):
    """
    Serializer to serialize/deserialize instances of the `MemberOfParliament` model.
    """
    voting_count = serializers.SerializerMethodField()
    bills_proposed_count = serializers.SerializerMethodField()
    is_term_active = serializers.SerializerMethodField()

    class Meta:
        model = MemberOfParliament
        fields = [
            "tokenized_id",
            "image",
            "name",
            "county",
            "constituency",
            "party",
            "is_active",
            "date_elected",
            "term_end_date",
            "committee_memberships",
            "attendance_rate",
            "bills_passed_count",
            "voting_count",
            "bills_proposed_count",
            "is_term_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["tokenized_id", "created_at", "updated_at"]
        
    def get_voting_count(self, obj):
        return obj.votes.count()
        
    def get_bills_proposed_count(self, obj):
        return obj.bills_proposed.count()
        
    def get_is_term_active(self, obj):
        return obj.is_term_active()


class MemberOfParliamentDetailSerializer(MemberOfParliamentSerializer):
    """
    Detailed serializer for MemberOfParliament with voting history and proposed bills.
    """
    voting_history = OfficialVoteSerializer(source='votes', many=True, read_only=True)
    bills_proposed = BillSerializer(many=True, read_only=True)
    public_alignment = serializers.SerializerMethodField()
    
    class Meta(MemberOfParliamentSerializer.Meta):
        fields = MemberOfParliamentSerializer.Meta.fields + [
            "voting_history",
            "bills_proposed",
            "public_alignment",
        ]
        
    def get_public_alignment(self, obj):
        return obj.get_voting_alignment_with_public()
