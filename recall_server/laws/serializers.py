from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from recall_server.laws.models import Bill, House, Comment, BillRevision, BillAmendment, PublishedLaw


class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 
            'user', 
            'user_name',
            'comment', 
            'created_at', 
            'updated_at',
            'likes_count',
            'is_featured',
            'replies_count',
            'parent'
        ]
        
    def get_user_name(self, obj):
        if hasattr(obj.user, 'get_full_name'):
            return obj.user.get_full_name()
        return str(obj.user)
        
    def get_replies_count(self, obj):
        return obj.get_replies_count()


class CommentDetailSerializer(CommentSerializer):
    replies = serializers.SerializerMethodField()
    
    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + ['replies']
        
    def get_replies(self, obj):
        replies = obj.get_all_replies()
        return CommentSerializer(replies, many=True).data


class BillRevisionSerializer(serializers.ModelSerializer):
    """
    Serializer for the BillRevision model.
    """
    class Meta:
        model = BillRevision
        fields = [
            'revision_id',
            'bill',
            'version_number',
            'content',
            'summary',
            'created_at',
            'created_by',
            'stage',
            'is_published',
        ]
        read_only_fields = ['revision_id', 'created_at']


class BillRevisionDetailSerializer(BillRevisionSerializer):
    """
    Detailed serializer for BillRevision with amendments.
    """
    incorporated_amendments = serializers.SerializerMethodField()
    
    class Meta(BillRevisionSerializer.Meta):
        fields = BillRevisionSerializer.Meta.fields + ['incorporated_amendments']
        
    def get_incorporated_amendments(self, obj):
        amendments = obj.incorporated_amendments.all()
        return BillAmendmentSerializer(amendments, many=True).data


class BillAmendmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the BillAmendment model.
    """
    proposed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BillAmendment
        fields = [
            'amendment_id',
            'bill',
            'title',
            'description',
            'proposed_text',
            'section_reference',
            'proposed_by',
            'proposed_by_name',
            'proposed_date',
            'status',
            'yes_votes_count',
            'no_votes_count',
            'abstain_votes_count',
        ]
        read_only_fields = ['amendment_id', 'proposed_date']
        
    def get_proposed_by_name(self, obj):
        if obj.proposed_by_mp:
            return f"MP {obj.proposed_by_mp.name}"
        elif obj.proposed_by_senator:
            return f"Senator {obj.proposed_by_senator.name}"
        elif obj.proposed_by_mca:
            return f"MCA {obj.proposed_by_mca.name}"
        elif obj.proposed_by:
            if hasattr(obj.proposed_by, 'get_full_name'):
                return obj.proposed_by.get_full_name()
            return str(obj.proposed_by)
        return "Unknown"


class PublishedLawSerializer(serializers.ModelSerializer):
    """
    Serializer for the PublishedLaw model.
    """
    bill_number = serializers.SerializerMethodField()
    
    class Meta:
        model = PublishedLaw
        fields = [
            'law_id',
            'bill',
            'bill_number',
            'title',
            'law_number',
            'content',
            'enactment_date',
            'effective_date',
            'gazette_reference',
            'pdf_document',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['law_id', 'created_at', 'updated_at']
        
    def get_bill_number(self, obj):
        return obj.bill.bill_number


class PublishedLawDetailSerializer(PublishedLawSerializer):
    """
    Detailed serializer for PublishedLaw with final revision.
    """
    final_revision = BillRevisionSerializer(read_only=True)
    
    class Meta(PublishedLawSerializer.Meta):
        fields = PublishedLawSerializer.Meta.fields + ['final_revision']


class BillSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()
    proposer = serializers.SerializerMethodField()
    vote_summary = serializers.SerializerMethodField()
    current_revision_number = serializers.SerializerMethodField()
    revisions_count = serializers.SerializerMethodField()
    amendments_count = serializers.SerializerMethodField()
    public_participation_active = serializers.SerializerMethodField()
    is_published_as_law = serializers.SerializerMethodField()
    
    class Meta:
        model = Bill
        fields = (
                'bill_id',
                'title',
                'description',
                'summary',
                'bill_number',
                'house',
                'stage',
                'status',
                'deadline_for_voting',
                'created_at',
                'updated_at',
                'proposed_date',
                'tags',
                'comments_count',
                'proposer',
                'vote_summary',
                'is_draft',
                'referred_to_committee',
                'committee_recommendation',
                'public_participation_start',
                'public_participation_end',
                'public_participation_active',
                'current_revision_number',
                'revisions_count',
                'amendments_count',
                'is_published_as_law',
                )
                
    def get_comments_count(self, obj):
        return obj.discussions.count()
        
    def get_proposer(self, obj):
        proposer = obj.get_proposer()
        if proposer:
            return {
                'id': proposer.id if hasattr(proposer, 'id') else proposer.tokenized_id,
                'name': proposer.name,
                'type': proposer.__class__.__name__
            }
        return None
        
    def get_vote_summary(self, obj):
        return {
            'official': {
                'yes': obj.yes_votes_count,
                'no': obj.no_votes_count,
                'abstain': obj.abstain_votes_count,
                'percentages': obj.get_official_vote_percentage()
            },
            'public': {
                'yes': obj.public_yes_votes,
                'no': obj.public_no_votes,
                'abstain': obj.public_abstain_votes,
                'percentages': obj.get_public_opinion_percentage()
            }
        }

    def get_current_revision_number(self, obj):
        current = obj.get_current_revision()
        return current.version_number if current else None
        
    def get_revisions_count(self, obj):
        return obj.revisions.count()
        
    def get_amendments_count(self, obj):
        return obj.amendments.count()
        
    def get_public_participation_active(self, obj):
        return obj.is_public_participation_active()
        
    def get_is_published_as_law(self, obj):
        return hasattr(obj, 'enacted_law')


class BillDetailSerializer(BillSerializer):
    comments = CommentSerializer(source='discussions', many=True, read_only=True)
    impact_analysis = serializers.CharField()
    stage_history = serializers.JSONField()
    current_revision = BillRevisionSerializer(read_only=True)
    committee_report = serializers.CharField()
    
    class Meta(BillSerializer.Meta):
        fields = BillSerializer.Meta.fields + (
            'comments',
            'impact_analysis',
            'stage_history',
            'current_revision',
            'committee_report',
        )


class HouseSerializer(serializers.ModelSerializer):
    bills_count = serializers.SerializerMethodField()
    
    class Meta:
        model = House
        fields = ('house_id', 'name', 'bills_count')
        
    def get_bills_count(self, obj):
        return obj.bills.count()
