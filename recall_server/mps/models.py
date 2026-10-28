"""
Custom Database models for the `mps` Django app.
"""

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from recall_server.common.mixins import OwnerlessAbstract
from recall_server.voting.models import Legislator, OfficialVote


class MemberOfParliament(Legislator, OwnerlessAbstract):
    """
    Custom model to represent a parliament member for the `mps` Django app.
    """

    name = models.CharField(max_length=200)
    image = models.URLField(
        max_length=200,
        default="""https://img.freepik.com/free-vector/illustration-businessman_53876-5856.jpg?w=740&t=st=1719052890~
        exp=1719053490~hmac=4e6f9ee8ae73ee004e482dc13a877e58d9dc91abcc31b2f6cfe9d878199eaba6""",
    )
    county = models.CharField(max_length=100)
    constituency = models.CharField(max_length=100, unique=True)
    party = models.CharField(max_length=100)
    
    # Additional fields for tracking
    date_elected = models.DateField(null=True, blank=True)
    term_end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Track bills proposed by this MP
    bills_proposed = models.ManyToManyField(
        'laws.Bill',
        related_name='proposed_by_mp',
        blank=True
    )
    
    # Track voting record
    votes = GenericRelation(
        OfficialVote,
        content_type_field='legislator_content_type',
        object_id_field='legislator_object_id'
    )
    
    # Committee memberships
    committee_memberships = models.CharField(max_length=500, blank=True)
    
    # Performance metrics
    attendance_rate = models.FloatField(default=0.0, help_text="Percentage of sessions attended")
    bills_passed_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Member of Parliament"
        verbose_name_plural = "Members of Parliament"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['constituency']),
            models.Index(fields=['party']),
            models.Index(fields=['is_active'])
        ]

    def __str__(self):
        return f"{self.name} - {self.constituency}"
        
    @property
    def voting_history(self):
        return super().voting_history.select_related('bill')
        
    def is_term_active(self):
        from django.utils import timezone
        current_date = timezone.now().date()
        return self.is_active and self.date_elected <= current_date <= self.term_end_date
        
    def get_voting_alignment_with_public(self):
        """Calculate how often the MP's votes align with public opinion"""
        alignment_count = 0
        total_votes = 0
        
        for vote in self.votes.all():
            bill = vote.bill
            bill.update_vote_counts()  # Ensure counts are up to date
            
            # Get the majority public opinion
            public_opinion = bill.get_public_opinion_percentage()
            max_opinion = max(public_opinion, key=public_opinion.get)
            
            # Check if MP's vote aligns with majority public opinion
            if vote.vote == max_opinion:
                alignment_count += 1
                
            total_votes += 1
            
        if total_votes == 0:
            return 0
            
        return round((alignment_count / total_votes) * 100, 2)
