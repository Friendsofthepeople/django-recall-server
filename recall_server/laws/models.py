from django.db import models
import uuid
from django.contrib.auth.models import User

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
    bill_number = models.CharField(max_length=100)
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    stage = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    deadline_for_voting = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    """
    county = models.ForeignKey(
            County,
            on_delete=models.CASCADE,
            null=True,
            blank=True
            )
    """

    def __str__(self):
        return f"{self.house} {self.bill_number}: {self.title}"

    def count_public_votes(self):
        return self.publicvote_set.count()

    def count_yes_votes(self):
        return self.publicvote_set.filter(vote='yes').count()

    def count_no_votes(self):
        return self.publicvote_set.filter(vote='no').count()

    def count_abstain_votes(self):
        return self.publicvote_set.filter(vote='abstain').count()

    def official_votes(self):
        return self.officialvote_set.all()

    def public_votes(self):
        return self.publicvote_set.all()


class Discussion(models.Model):
    bill = models.ForeignKey(
            Bill,
            on_delete=models.CASCADE,
            related_name='discussions'
            )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    parent = models.ForeignKey(
            'self',
            null=True,
            blank=True,
            on_delete=models.CASCADE,
            related_name='replies'
            )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Discussion by {self.user.first_name}\
                on {self.bill.title}"
