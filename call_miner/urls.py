from django.urls import path
from .views import CallView

urlpatterns = [
    path('call/<int:pk>/', CallView.as_view(), name='call_detail'),
]