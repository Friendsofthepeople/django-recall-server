from django.urls import path

from county.views import *


urlpatterns = [
        path(
            'county/',
            CountyView.as_view(),
            name='County'
            ),
        path(
            'constituency/',
            ConstituencyView.as_view(),
            name='Constituency'
            ),
        ]
