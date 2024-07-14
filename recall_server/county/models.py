# ruff: noqa: D101, DJ008
"""
Custom Database models for the `county` Django app.

Note:
    Remove the noqa on line 1, once the following county models
    have been implemented to re-enable ruff lint checks.
"""

from django.db import models


class County(models.Model):
    pass


class Constituency(models.Model):
    pass
