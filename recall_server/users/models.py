"""
This module defines models for the user accounts.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom user manager for User model with email as the unique identifier.
    """

    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("users must have an email address")
        user = self.model(
            email=self.normalize_email(email),
            **kwargs,
        )

        user.set_password(password)
        user.save(using=self._db)
        user.is_active = True
        return user


class User(AbstractBaseUser):
    """
    User model representing custom user accounts for the project.
    """

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_voter = models.BooleanField(default=True)
    is_voter = models.BooleanField(default=True)
    is_leader = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
