from django.urls import path
from .views import MpRegisterView

urlpatterns = [
    path('register/', MpRegisterView.as_view(), name='mp-register'),
]
