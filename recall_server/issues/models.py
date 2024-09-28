from django.db import models
from django.conf import settings

class Issue(models.Model):
    category = models.CharField(max_length=200)
    serial = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    author = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE
            )
    content = models.TextField()
    status = models.CharField(max_length=200)
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Issue: {self.title} published by {self.author}"
