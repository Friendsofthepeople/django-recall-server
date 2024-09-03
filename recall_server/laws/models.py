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

    def __str__(self):
        return f"{self.house} {self.bill_number}: {self.title}"


class Comment(models.Model):
    bill = models.ForeignKey(
            Bill,
            on_delete=models.CASCADE,
            related_name='discussions'
            )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Discussion by {self.user.first_name}\
                on {self.bill.title}"
