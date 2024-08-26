from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from recall_server.laws.models import Bill, House
from recall_server.laws.serializers import BillSerializer, HouseSerializer
from recall_server.county.models import County
from recall_server.county.serializers import CountySerializer


class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        queryset = self.queryset
        house = self.request.query_params.get('house')
        county = self.request.query_params.get('county')

        if house:
            queryset = queryset.filter(house__name=house)

        if house == 'county_assembly' and county:
            queryset = queryset.filter(county__name=county)

        return queryset

    @action(detail=False, methods=['get'])
    def houses(self, request):
        """
        Returns a list of houses i.e Senate, Parliament, County
        """
        houses = House.objects.all()
        serializer = HouseSerializer(houses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def counties(self, request):
        """
        Returns a list of countries when County Assembly is selected
        """
        house = request.query_params.get('house')
        if house == 'county_assembly':
            counties = County.objects.all()
            serializer = CountySerializer(counties, many=True)
            return Response(serializer.data)
        return Response({"detail": "County data currently unavailable"})

    @action(detail=False, methods=['get'])
    def bills_by_county(self, request):
        """
        Returns a list of bills by county
        """
        county = request.query_params.get('county')
        if county:
            bills = self.get_queryset().filter(county__name=county)
            serializer = BillSerializer(bills, many=True)
            return Response(serializer.data)
        return Response({"detail": "No county provided."})
