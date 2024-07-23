"""
Custom Database models for the `mps` Django app.
"""

from django.db import models
from recall_server.common.mixins import OwnerlessAbstract


class MemberOfParliament(OwnerlessAbstract):
    """
    Custom model to represent a parliament member for the `mps` Django app.
    """

    name = models.CharField(max_length=200)
    image = models.URLField(
        max_length=200,
        default="""https://img.freepik.com/free-vector/illustration-businessman_53876-5856.jpg?w=740&t=st=1719052890~
        exp=1719053490~hmac=4e6f9ee8ae73ee004e482dc13a877e58d9dc91abcc31b2f6cfe9d878199eaba6""",
    )
    county = models.CharField(max_length=100)
    constituency = models.CharField(max_length=100)
    party = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.constituency}"
