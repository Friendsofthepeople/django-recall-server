"""
Custom Database models for the `polling_station` Django app.
"""

from django.db import models
from recall_server.common.mixins import OwnerlessAbstract


class PollingStation(OwnerlessAbstract):
    """
    Keep track of Polling Station name, location, and count of registered voters.
    """

    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    registered_voters_count = models.IntegerField()

    def __str__(self):
        return f"{self.name} {self.location} {self.registered_voters_count}"
