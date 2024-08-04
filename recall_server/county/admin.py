"""
Register custom models to the Django Admin site for the `county` Django app.
"""

from django.contrib import admin
from recall_server.county.models import Constituency, County

admin.site.register(County)
admin.site.register(Constituency)
