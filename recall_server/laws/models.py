from django.db import models
import uuid
from django.conf import settings
from django.utils import timezone

from recall_server.config import settings

# from recall_server.county.models import County


HOUSE_CHOICES = [
        ('county_assembly', 'County Assembly'),
        ('senate', 'Senate'),
        ('parliament', 'Parliament')
        ]


class House(models.Model):
    name = models.CharField(
            max_length=100,
            choices=HOUSE_CHOICES,
            unique=True
            )
    house_id = models.UUIDField(
            primary_key=True,
            default=uuid.uuid4
            )

    def __str__(self):
        return self.get_name_display()


class Bill(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    bill_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    bill_number = models.CharField(max_length=100, unique=True)
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='bills')
    stage = models.CharField(max_length=100, choices=[
        ('draft', 'Draft'),
        ('first_reading', 'First Reading'),
        ('second_reading', 'Second Reading'),
        ('committee', 'Committee Stage'),
        ('third_reading', 'Third Reading'),
        ('passed', 'Passed'),
        ('rejected', 'Rejected')
    ])
    status = models.CharField(max_length=100, choices=[
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('closed', 'Closed')
    ])
    deadline_for_voting = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # New fields for better tracking
    proposed_date = models.DateField(auto_now_add=True)
    summary = models.TextField(blank=True, help_text="A citizen-friendly summary of what this bill proposes")
    impact_analysis = models.TextField(blank=True, help_text="Analysis of the potential impact of this bill")
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags for categorizing bills")
    
    # Track stage history
    stage_history = models.JSONField(default=list, blank=True, help_text="History of stage changes with dates")
    
    # Track votes summary
    yes_votes_count = models.PositiveIntegerField(default=0)
    no_votes_count = models.PositiveIntegerField(default=0)
    abstain_votes_count = models.PositiveIntegerField(default=0)
    
    # Public opinion metrics
    public_yes_votes = models.PositiveIntegerField(default=0)
    public_no_votes = models.PositiveIntegerField(default=0)
    public_abstain_votes = models.PositiveIntegerField(default=0)

    # Publishing workflow fields
    is_draft = models.BooleanField(default=True, help_text="Whether this bill is still in draft stage")
    current_revision = models.ForeignKey(
        'BillRevision', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='current_for_bill'
    )
    
    # Committee information
    referred_to_committee = models.CharField(max_length=255, blank=True, help_text="Committee this bill was referred to")
    committee_report = models.TextField(blank=True, help_text="Report from the committee")
    committee_recommendation = models.CharField(
        max_length=20, 
        blank=True, 
        choices=[
            ('pass', 'Pass'),
            ('pass_with_amendments', 'Pass with Amendments'),
            ('reject', 'Reject'),
            ('further_review', 'Further Review Needed')
        ]
    )
    
    # Public participation
    public_participation_start = models.DateTimeField(null=True, blank=True)
    public_participation_end = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['deadline_for_voting']
        indexes = [
            models.Index(fields=['status', 'stage']),
            models.Index(fields=['deadline_for_voting']),
            models.Index(fields=['bill_number']),
            models.Index(fields=['proposed_date']),
            models.Index(fields=['tags'])
        ]

    def __str__(self):
        return f"{self.house} {self.bill_number}: {self.title}"

    def is_active(self):
        return self.status == 'active'

    def can_be_voted(self):
        return self.status == 'active' and self.deadline_for_voting > timezone.now()
        
    def update_stage(self, new_stage, notes=""):
        """Update the bill's stage and record in history"""
        if not self.stage_history:
            self.stage_history = []
            
        # Add current stage to history
        self.stage_history.append({
            'stage': self.stage,
            'changed_at': timezone.now().isoformat(),
            'notes': notes
        })
        
        # Update to new stage
        self.stage = new_stage
        self.save()
        
    def update_vote_counts(self):
        """Update the vote count summaries"""
        official_votes = self.officialvote_set.all()
        self.yes_votes_count = official_votes.filter(vote='yes').count()
        self.no_votes_count = official_votes.filter(vote='no').count()
        self.abstain_votes_count = official_votes.filter(vote='abstain').count()
        
        public_votes = self.public_votes.all()
        self.public_yes_votes = public_votes.filter(vote='yes').count()
        self.public_no_votes = public_votes.filter(vote='no').count()
        self.public_abstain_votes = public_votes.filter(vote='abstain').count()
        
        self.save()
        
    def get_proposer(self):
        """Get the legislator who proposed this bill"""
        # Check if proposed by senator
        senator = self.proposed_by_senator.first()
        if senator:
            return senator
            
        # Check if proposed by MP
        mp = self.proposed_by_mp.first()
        if mp:
            return mp
            
        # Check if proposed by MCA
        mca = self.proposed_by_mca.first()
        if mca:
            return mca
            
        return None
        
    def get_public_opinion_percentage(self):
        """Calculate the percentage of public support"""
        total_votes = self.public_yes_votes + self.public_no_votes + self.public_abstain_votes
        if total_votes == 0:
            return {'yes': 0, 'no': 0, 'abstain': 0}
            
        return {
            'yes': round((self.public_yes_votes / total_votes) * 100, 2),
            'no': round((self.public_no_votes / total_votes) * 100, 2),
            'abstain': round((self.public_abstain_votes / total_votes) * 100, 2)
        }
        
    def get_official_vote_percentage(self):
        """Calculate the percentage of official support"""
        total_votes = self.yes_votes_count + self.no_votes_count + self.abstain_votes_count
        if total_votes == 0:
            return {'yes': 0, 'no': 0, 'abstain': 0}
            
        return {
            'yes': round((self.yes_votes_count / total_votes) * 100, 2),
            'no': round((self.no_votes_count / total_votes) * 100, 2),
            'abstain': round((self.abstain_votes_count / total_votes) * 100, 2)
        }

    def get_current_revision(self):
        """Get the current revision of the bill"""
        if self.current_revision:
            return self.current_revision
        
        # If no current revision is set, get the latest one
        latest = self.revisions.order_by('-version_number').first()
        if latest:
            self.current_revision = latest
            self.save(update_fields=['current_revision'])
            return latest
            
        return None
    
    def create_revision(self, content, summary="", created_by=None, is_published=False):
        """Create a new revision of this bill"""
        # Get the latest version number
        latest = self.revisions.order_by('-version_number').first()
        version_number = 1
        if latest:
            version_number = latest.version_number + 1
            
        # Create the new revision
        revision = BillRevision.objects.create(
            bill=self,
            version_number=version_number,
            content=content,
            summary=summary,
            created_by=created_by,
            stage=self.stage,
            is_published=is_published
        )
        
        # Update the current revision
        self.current_revision = revision
        self.save(update_fields=['current_revision'])
        
        return revision
        
    def publish_law(self, law_number, enactment_date, effective_date, gazette_reference=""):
        """Publish this bill as an enacted law"""
        if self.stage != 'passed':
            raise ValueError("Only passed bills can be published as laws")
            
        current_revision = self.get_current_revision()
        if not current_revision:
            raise ValueError("Cannot publish without a revision")
            
        # Create the published law
        law = PublishedLaw.objects.create(
            bill=self,
            title=self.title,
            law_number=law_number,
            content=current_revision.content,
            enactment_date=enactment_date,
            effective_date=effective_date,
            gazette_reference=gazette_reference,
            final_revision=current_revision
        )
        
        return law
        
    def start_public_participation(self, end_date):
        """Start the public participation period for this bill"""
        now = timezone.now()
        self.public_participation_start = now
        self.public_participation_end = end_date
        self.save(update_fields=['public_participation_start', 'public_participation_end'])
        
    def end_public_participation(self):
        """End the public participation period for this bill"""
        self.public_participation_end = timezone.now()
        self.save(update_fields=['public_participation_end'])
        
    def is_public_participation_active(self):
        """Check if public participation is currently active"""
        now = timezone.now()
        return (
            self.public_participation_start is not None and
            self.public_participation_end is not None and
            self.public_participation_start <= now <= self.public_participation_end
        )
        
    def refer_to_committee(self, committee_name):
        """Refer this bill to a committee"""
        self.referred_to_committee = committee_name
        self.save(update_fields=['referred_to_committee'])
        
    def add_committee_report(self, report, recommendation):
        """Add a committee report to this bill"""
        self.committee_report = report
        self.committee_recommendation = recommendation
        self.save(update_fields=['committee_report', 'committee_recommendation'])


class Comment(models.Model):
    bill = models.ForeignKey(
            Bill,
            on_delete=models.CASCADE,
            related_name='discussions'
            )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bill_comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Add parent comment for threaded discussions
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    # Track likes/reactions
    likes_count = models.PositiveIntegerField(default=0)
    
    # Flag for featured comments (e.g., from experts or verified users)
    is_featured = models.BooleanField(default=False)
    
    # Flag for moderation
    is_approved = models.BooleanField(default=True)
    reported_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['likes_count']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['is_approved'])
        ]

    def __str__(self):
        return f"Discussion by {self.user.first_name} on {self.bill.title}"
        
    def get_replies_count(self):
        """Get the count of replies to this comment"""
        return self.replies.count()
        
    def get_all_replies(self):
        """Get all replies in a threaded structure"""
        return self.replies.all().order_by('created_at')
        
    def report(self):
        """Report this comment for moderation"""
        self.reported_count += 1
        if self.reported_count >= 5:  # Auto-hide after 5 reports
            self.is_approved = False
        self.save()
        
    def like(self):
        """Increment the like count"""
        self.likes_count += 1
        self.save()


class BillRevision(models.Model):
    """
    Model to track revisions of a bill throughout the legislative process.
    """
    revision_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    bill = models.ForeignKey('Bill', on_delete=models.CASCADE, related_name='revisions')
    version_number = models.PositiveIntegerField(help_text="Sequential version number of this revision")
    content = models.TextField(help_text="The full text content of this revision")
    summary = models.TextField(blank=True, help_text="Summary of changes in this revision")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='bill_revisions'
    )
    stage = models.CharField(max_length=100, help_text="The bill stage when this revision was created")
    is_published = models.BooleanField(default=False, help_text="Whether this revision is publicly available")
    
    class Meta:
        ordering = ['-version_number']
        unique_together = ['bill', 'version_number']
        indexes = [
            models.Index(fields=['bill', 'version_number']),
            models.Index(fields=['is_published']),
        ]
        
    def __str__(self):
        return f"{self.bill.bill_number} - v{self.version_number}"


class BillAmendment(models.Model):
    """
    Model to track amendments proposed to a bill.
    """
    amendment_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    bill = models.ForeignKey('Bill', on_delete=models.CASCADE, related_name='amendments')
    title = models.CharField(max_length=255)
    description = models.TextField()
    proposed_text = models.TextField(help_text="The text to be added, modified, or removed")
    section_reference = models.CharField(max_length=255, help_text="Reference to the section being amended")
    proposed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='proposed_amendments'
    )
    proposed_date = models.DateTimeField(auto_now_add=True)
    
    # For legislator proposals
    proposed_by_mp = models.ForeignKey(
        'mps.MemberOfParliament', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='proposed_amendments'
    )
    proposed_by_senator = models.ForeignKey(
        'county.Senator', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='proposed_amendments'
    )
    proposed_by_mca = models.ForeignKey(
        'county.MCA', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='proposed_amendments'
    )
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Voting on amendments
    yes_votes_count = models.PositiveIntegerField(default=0)
    no_votes_count = models.PositiveIntegerField(default=0)
    abstain_votes_count = models.PositiveIntegerField(default=0)
    
    # If approved, which revision incorporated it
    incorporated_in = models.ForeignKey(
        'BillRevision', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='incorporated_amendments'
    )
    
    class Meta:
        ordering = ['-proposed_date']
        indexes = [
            models.Index(fields=['bill', 'status']),
            models.Index(fields=['proposed_date']),
        ]
        
    def __str__(self):
        return f"Amendment to {self.bill.bill_number}: {self.title}"
        
        
class PublishedLaw(models.Model):
    """
    Model to represent a bill that has been enacted into law.
    """
    law_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    bill = models.OneToOneField('Bill', on_delete=models.CASCADE, related_name='enacted_law')
    title = models.CharField(max_length=255)
    law_number = models.CharField(max_length=100, unique=True)
    content = models.TextField(help_text="The full text of the enacted law")
    enactment_date = models.DateField()
    effective_date = models.DateField()
    gazette_reference = models.CharField(max_length=255, blank=True)
    
    # Final version that was enacted
    final_revision = models.ForeignKey(
        'BillRevision', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='enacted_as_law'
    )
    
    # PDF document
    pdf_document = models.URLField(blank=True, null=True, help_text="URL to the PDF document of the law")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-enactment_date']
        indexes = [
            models.Index(fields=['enactment_date']),
            models.Index(fields=['effective_date']),
            models.Index(fields=['law_number']),
        ]
        
    def __str__(self):
        return f"{self.law_number}: {self.title}"
