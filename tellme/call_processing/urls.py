from django.urls import path
from django.http import JsonResponse
from tellme.call_processing.views import (
    QueueRecordingView, ProcessRecordingView, SummarizationView, TicketCreationView
)


def root_view(request):
    return JsonResponse({"detail": "This is the processing v1 API root."})


urlpatterns = [
    path('', root_view, name='processing-root'),
    path('queue/', QueueRecordingView.as_view(), name='queue'),
    path('process/', ProcessRecordingView.as_view(), name='process'),
    path('summarize/', SummarizationView.as_view(), name='summarize'),
    path('create_ticket/', TicketCreationView.as_view(), name='create_ticket'),
]