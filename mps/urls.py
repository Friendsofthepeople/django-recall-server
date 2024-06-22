from django.urls import path
from .views import  MpListView, MpRegisterView

urlpatterns = [
    path('register/', MpRegisterView.as_view(), name='mp-register'),
    path('list/', MpListView.as_view(), name='mp-list'),
    # path('import-data/', ImportDataView.as_view(), name='import-data'),
]
