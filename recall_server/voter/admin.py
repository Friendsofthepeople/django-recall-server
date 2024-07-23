"""
Register custom models to the Django Admin site for the `voter` Django app.
"""

from django.contrib import admin

from .models import Voter

admin.site.register(Voter)
