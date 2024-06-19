from django.urls import path
from . import views

urlpatterns = [
    path('diaspora/', views.DiasporaList, name='diaspora'),
    path('add-diaspora/', views.addDiaspora, name='add-diaspora'),
    path('county/', views.county, name='county'),
    path('add-county/', views.addCounty, name='add-county'),
    path('polling-station/', views.pollingStation, name='polling-station'),
    path('add-station/', views.addStation, name='add-station')
    # path('diaspora/<int:pk>/', views.DiasporaDetail),
]