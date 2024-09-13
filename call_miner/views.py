import re
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

        # Process the transcript by splitting it into parts by 'Agent:' and 'Customer:'
        context['transcript'] = self.process_transcript(call.transcript)

        return context

    @staticmethod
    def process_transcript(transcript):
        # Split the transcript on "Agent:" and "Customer:", while keeping the labels as part of the results
        # This regex will split the transcript based on "Agent:" or "Customer:" while preserving these words
        messages = re.split(r'(?=(Agent:|Customer:))', transcript)

        # Pair up the message and assign the appropriate class (agent or customer) for coloring
        processed_messages = []
        for i in range(1, len(messages), 2):  # We start at 1 because 0 is an empty string from the split
            speaker = messages[i].strip()  # Either "Agent:" or "Customer:"
            message_text = messages[i + 1][len(speaker):].strip()  # The message following the speaker identifier
            processed_messages.append({
                'speaker': speaker,
                'message': message_text,
                'class': 'agent-message' if speaker == 'Agent:' else 'customer-message'
            })
        return processed_messages
