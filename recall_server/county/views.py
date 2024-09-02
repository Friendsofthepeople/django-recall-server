"""
Custom views for the `county` Django app.
"""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from recall_server.county.models import(
        County,
        Constituency,
        Senator,
        MCA
        )
from recall_server.county.serializers import(
        ConstituencySerializer,
        CountySerializer,
        SenatorSerializer,
        MCASerializer
        )


class CountyViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for County
    """
    queryset = County.objects.all()
    serializer_class = CountySerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['county', 'county_number']


class SenatorViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations on Senator
    """
    queryset = Senator.objects.all()
    serializer_class = SenatorSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'county']


class ConstituencyViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for Constituency
    """
    queryset = Constituency.objects.all()
    serializer_class = ConstituencySerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'mp']


class MCAViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for MCA
    """
    queryset = MCA.objects.all()
    serializer_class = MCASerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'ward']
