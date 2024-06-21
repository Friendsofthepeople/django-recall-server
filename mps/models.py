from django.db import models
import uuid

class MemberOfParliament(models.Model):
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    constituency = models.CharField(max_length=100)
    party = models.CharField(max_length=100)
    tokenized_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.middle_name} {self.surname} - {self.constituency}"
