from django.db import models

# Create your models here.
from django.db import models

# Create your models here.

class Diaspora(models.Model):
    code = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    area_code = models.CharField(max_length=200)
    area_name = models.CharField(max_length=200)
    center = models.CharField(max_length=200)
    center_code = models.CharField(max_length=200)
    polling_station_code = models.CharField(max_length=200)
    polling_station_name = models.CharField(max_length=200)
    voters = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
    

class County(models.Model):
    code  = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    voters = models.IntegerField()

    def __str__(self):
        return self.name

class PollingStation(models.Model):
    county_code = models.CharField(max_length=200)
    county_name = models.CharField(max_length=200)
    const_code = models.CharField(max_length=200)
    const_name = models.CharField(max_length=200)
    caw_code = models.CharField(max_length=200)
    caw_name = models.CharField(max_length=200)
    center_code = models.CharField(max_length=200)
    center_name = models.CharField(max_length=200)
    polling_station_code = models.CharField(max_length=200)
    polling_station_name = models.CharField(max_length=200)
    voters = models.IntegerField()

    def __str__(self):
        return self.county_name
