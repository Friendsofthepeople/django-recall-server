from django.urls import path

from pollingStation.views import PollingStationView


urlpatterns = [
        path(
            'polling_station/',
            PollingStationView.as_view(),
            name='polling-station'
            ),
        ]
