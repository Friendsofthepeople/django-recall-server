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


class CountyView(viewsets.ModelViewSet):
    """
    Handles CRUD operations for County
    """
    queryset = County.objects.all()
    serializer_class = CountySerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['county', 'county_number']


class SenatorView(viewsets.ModelViewSet):
    """
    Handles CRUD operations on Senator
    """
    queryset = Senator.objects.all()
    serializer_class = SenatorSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'county']


class ConstituencyView(viewsets.ModelViewSet):
    """
    Handles CRUD operations for Constituency
    """
    queryset = Constituency.objects.all()
    serializer_class = ConstituencySerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'mp']


class MCAView(viewsets.ModelViewSet):
    """
    Handles CRUD operations for MCA
    """
    queryset = MCA.objects.all()
    serializer_class = MCASerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'ward']
