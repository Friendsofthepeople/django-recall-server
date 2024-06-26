from django.urls import path

from recall_server.voter.views import VoterRegisterView

urlpatterns = [
    path("register/", VoterRegisterView.as_view(), name="voter-register"),
]
