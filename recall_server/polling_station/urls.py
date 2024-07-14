"""
URL config for the `polling_station` Django app.
"""

from django.urls import path
from recall_server.polling_station.views import PollingStationView

urlpatterns = [
    path("polling_station/", PollingStationView.as_view(), name="polling-station"),
]
