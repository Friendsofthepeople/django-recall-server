from rest_framework import decorators, response
from .models import Diaspora, County, PollingStation
from .serializers import DiasporaSerializer, CountySerializer,PollingStationSerializer

@decorators.api_view(['GET'])
def DiasporaList(request):
    diaspora = Diaspora.objects.all()
    serializer = DiasporaSerializer(diaspora, many=True)

    return response.Response(serializer.data)


@decorators.api_view(['POST'])
def addDiaspora(request):
    new_diaspora = request.data
    serializer = DiasporaSerializer(data=new_diaspora)
    if serializer.is_valid():
        serializer.save()
    
    return response.Response(serializer.data)


@decorators.api_view(['GET'])
def county(request):
    county_data = County.objects.all()
    serialzer = CountySerializer(county_data, many=True)

    return response.Response(serialzer.data)

@decorators.api_view(['POST'])
def addCounty(request):
    county_data = request.data
    serializer = CountySerializer(data=county_data)
    if serializer.is_valid():
        serializer.save()

    return response.Response(serializer.data)

@decorators.api_view(['GET'])
def pollingStation(request):
    polling_station_data = PollingStation.objects.all()
    serializer = PollingStationSerializer(polling_station_data, many=True)

    return response.Response(serializer.data)

@decorators.api_view(['POST'])
def addStation(request):
    polling_station_data = request.data
    serializer = PollingStationSerializer(data=polling_station_data)

    if serializer.is_valid():
        serializer.save()
    return response.Response(serializer.data)