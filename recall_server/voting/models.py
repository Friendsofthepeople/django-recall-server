from django.db import models
from django.db.models import Count
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from recall_server.config import settings

# from recall_server.county.models import County


class VoteChoices(models.TextChoices):
    YES = 'yes', 'Yes'
    NO = 'no', 'No'
    ABSTAIN = 'abstain', 'Abstain'


class Legislator(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        abstract = True

    @property
    def voting_history(self):
        content_type = ContentType.objects.get_for_model(self)
        return OfficialVote.objects.filter(
                legislator_content_type=content_type,
                legislator_object_id=self.id
                )


class PublicVote(models.Model):
    bill = models.ForeignKey(
            'laws.Bill',
            on_delete=models.CASCADE,
            related_name='public_votes'
            )
    user = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name='votes'
            )
    vote = models.CharField(
            max_length=10,
            choices=VoteChoices.choices
            )
    comment = models.TextField(blank=True)
    region = models.ForeignKey(
            'county.County',
            on_delete=models.CASCADE,
            related_name='votes'
            )
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['vote'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['bill', 'user'],
                name='unique_user_vote_per_bill'
            )
        ]

    def __str__(self):
        return f"{self.user}: {self.bill} {self.vote}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.bill.can_be_voted():
            raise ValidationError('This bill is not currently open for voting.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class OfficialVote(models.Model):
    bill = models.ForeignKey(
            'laws.Bill',
            on_delete=models.CASCADE,
            related_name='official_votes'
            )
    legislator_content_type = models.ForeignKey(
            ContentType,
            on_delete=models.CASCADE
            )
    legislator_object_id = models.PositiveIntegerField()
    legislator = GenericForeignKey(
            'legislator_content_type',
            'legislator_object_id'
            )
    vote = models.CharField(
            max_length=10,
            choices=VoteChoices.choices
            )
    date = models.DateTimeField(auto_now_add=True)
    
    # Additional fields for better tracking
    session_name = models.CharField(max_length=255, blank=True, help_text="Name of the voting session")
    reason = models.TextField(blank=True, help_text="Reason given by the legislator for their vote")
    
    class Meta:
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['vote']),
            models.Index(fields=['legislator_content_type', 'legislator_object_id'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['bill', 'legislator_content_type', 'legislator_object_id'],
                name='unique_legislator_vote_per_bill'
            )
        ]

    def __str__(self):
        return f"{self.legislator}: {self.bill} - {self.vote}"
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update bill vote counts when a vote is saved
        self.bill.update_vote_counts()
        
    def get_legislator_name(self):
        """Get the name of the legislator who cast this vote"""
        if hasattr(self.legislator, 'name'):
            return self.legislator.name
        return "Unknown"
        
    def get_legislator_type(self):
        """Get the type of legislator (MP, Senator, MCA)"""
        return self.legislator_content_type.model.capitalize()
        
    def get_party_alignment(self):
        """Check if this vote aligns with the legislator's party position"""
        if not hasattr(self.legislator, 'party'):
            return None
            
        # This would require additional logic to determine party position
        # For now, return None as a placeholder
        return None
