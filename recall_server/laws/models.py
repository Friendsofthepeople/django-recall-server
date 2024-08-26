from django.db import models
import uuid

from recall_server.county.models import County


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
    house_id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    def __str__(self):
        return self.get_name_display()


class Bill(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    bill_number = models.CharField(max_length=100)
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    stage = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    deadline_for_voting = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    county = models.ForeignKey(
            County,
            on_delete=models.CASCADE,
            null=True,
            blank=True
            )

    def __str__(self):
        return f"{self.house} {self.bill_number}: {self.title}"
