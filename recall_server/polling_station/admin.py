"""
Register custom models to the Django Admin site for the `polling_station` Django app.
"""

from django.contrib import admin
from recall_server.polling_station.models import PollingStation

admin.site.register(PollingStation)
