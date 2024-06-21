from django.urls import path
from .views import RecallCreateView, RecallDetailView

urlpatterns = [
     path('create/', RecallCreateView.as_view(), name='recall-create'),
    path('detail/<int:pk>/', RecallDetailView.as_view(), name='recall-detail'),
]
