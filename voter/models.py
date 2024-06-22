from datetime import datetime
from django.db import models
import uuid
from django.contrib.auth.hashers import make_password

class Voter(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100) 
    password = models.CharField(max_length=128, default=make_password(str(datetime.now())))  # Use UTC timezone
    tokenized_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
