import uuid

from django.contrib.auth import get_user_model
from django.db import models

from recall_server.common.mixins import OwnerlessAbstract

User = get_user_model()


class Recall(OwnerlessAbstract):
    recaller = models.ForeignKey(
        User, related_name="initiated_recalls", on_delete=models.CASCADE
    )
    recalled = models.ForeignKey(User, related_name="recalls", on_delete=models.CASCADE)
    recall_supporters = models.ManyToManyField(
        User, related_name="supported_recalls", blank=True
    )
    recall_reasons = models.TextField()

    def __str__(self):
        return f"{self.recalled} recalled by {self.recaller}"
