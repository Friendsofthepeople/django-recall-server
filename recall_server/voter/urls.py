"""
URL config for the `voter` Django app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recall_server.voter.views import (
    #VoterRegisterView,
    UserRegisterView,
    VoterProfileViewSet
)

# Create a router for the VoterProfileViewSet
router = DefaultRouter()
router.register(r'profiles', VoterProfileViewSet)

urlpatterns = [
    # Legacy endpoint for backward compatibility
    # path("register/", VoterRegisterView.as_view(), name="voter-register"),
    
    # New endpoints using Django's User model
    path("user/register/", UserRegisterView.as_view(), name="user-register"),
    
    # Include the router URLs
    path("", include(router.urls)),
]
