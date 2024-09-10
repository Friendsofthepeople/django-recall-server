from django.db import models
from django.conf import settings


class Post(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE
            )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Post: {self.title} published by {self.author}"


class Response(models.Model):
    post = models.ForeignKey(
            Post,
            on_delete=models.CASCADE,
            related_name='responses'
            )
    parent = models.ForeignKey(
            'self',
            on_delete=models.CASCADE,
            null=True,
            blank=True,
            related_name='replies'
            )
    author = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE
            )
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"
