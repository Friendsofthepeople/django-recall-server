"""
Custom Database models for the `voter` Django app.
"""

import datetime

from django.contrib.auth.hashers import make_password
from django.db import models
from recall_server.common.mixins import OwnerlessAbstract


class Voter(OwnerlessAbstract):
    """
    Custom model to represent a voter for the `voter` Django app.
    """

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    password = models.CharField(
        max_length=128,
        default=make_password(str(datetime.datetime.now(tz=datetime.timezone.utc))),
    )  # Use UTC timezone

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
