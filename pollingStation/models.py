from django.db import models


class PollingStation(models.Model):
    """
    Keep track of Polling Station name, location
    and count of registered voters
    """
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    registeredVoters_count = models.IntegerField()

    def __str__(self):
        return f"{self.name} {self.location} {self.registeredVoters_count}"
