"""
Custom Database models for the `county` Django app.
"""
from django.db import models

from recall_server.mps.models import MemberOfParliament
from recall_server.polling_station.models import PollingStation
from recall_server.laws.models import Bill


class County(models.Model):
    """
    Keep track of county and number of constituencies.
    """

    name = models.CharField(unique=True, max_length=40)
    county_number = models.CharField(max_length=3, unique=True, default=000)
    constituency_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name}: {self.constituency_count}"


class Senator(models.Model):
    """
    keep track of senators
    """
    name = models.CharField(max_length=200)
    county = models.ForeignKey(
            County,
            on_delete=models.CASCADE
            )
    bill_proposed = models.ForeignKey(
            Bill,
            on_delete=models.CASCADE
            )
    voting_history = models.CharField(max_length=20)


class Constituency(models.Model):
    """
    Keep track of constituency.
    """

    name = models.CharField(unique=True, max_length=20)
    registeredvoter_count = models.IntegerField(default=0)
    mp = models.ForeignKey(
        MemberOfParliament,
        related_name="constituencies",
        on_delete=models.CASCADE,
    )
    polling_station = models.ForeignKey(
        PollingStation,
        related_name="constituencies",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.name} {self.mp} {self.polling_station}"


class MCA(models.Model):
    """
    Keep track of wards
    """
    name = models.CharField(max_length=200)
    ward = models.CharField(max_length=20, unique=True)
    voting_history = models.CharField(max_length=20)
    constituency = models.ForeignKey(
            Constituency,
            on_delete=models.CASCADE
            )
