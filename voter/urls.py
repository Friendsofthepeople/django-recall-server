from django.urls import path
from .views import VoterRegisterView

urlpatterns = [
    path('register/', VoterRegisterView.as_view(), name='voter-register'),
]
