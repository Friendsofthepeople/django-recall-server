from django.db import models


from mps.models import MemberOfParliament
from pollingStation.models import PollingStation


class County(models.Model):
    """
    Keep track of county and number of constituencies
    """
    name = models.CharField(unique=True, max_length=40)
    constituency_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name}: {self.constituency_count}"


class Constituency(models.Model):
    """
    Keep track of constituency
    """
    name = models.CharField(unique=True, max_length=20)
    registeredvoter_count = models.IntegerField(default=0)
    mp = models.ForeignKey(
            MemberOfParliament,
            related_name="constituencies",
            on_delete=models.CASCADE
            )
    polling_station = models.ForeignKey(
            PollingStation,
            related_name="constituencies",
            on_delete=models.CASCADE
            )

    def __str__(self):
        return f"{self.name} {self.mp} {self.polling_station}"
