from django.db import models
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

class Recall(models.Model):
    recaller = models.ForeignKey(User, related_name='initiated_recalls', on_delete=models.CASCADE)
    recalled = models.ForeignKey(User, related_name='recalls', on_delete=models.CASCADE)
    recall_supporters = models.ManyToManyField(User, related_name='supported_recalls', blank=True)
    recall_reasons = models.TextField()
    tokenized_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
