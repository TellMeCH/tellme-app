from django.views.generic import DetailView
from .models import Conversation


class CallView(DetailView):
    """
    This simple view shows the maximum granularity for a call. It is meant to display all the necessary information
    of a conversation item.
    """
    model = Conversation
    template_name = 'call_detail.html'
    context_object_name = 'call'

    def get_context_data(self, **kwargs):
        # Get the default context from the DetailView
        context = super().get_context_data(**kwargs)

        # Additional context
        call = self.get_object()
        context['agent'] = call.agent
        context['customer'] = call.customer
        context['date'] = call.date
        context['summary'] = call.summary
        context['topics'] = call.topics.all()
        context['transcript'] = call.processed_messages

        return context
