from django.urls import path
from . import views

#TODO create endpoints for the API views that will be used to perform CRUD operations on the database tables

urlpatterns = [
    path('remove/', views.remove, name='remove'),
    
]