from django import forms
from django.core.exceptions import ValidationError
from tellme.call_miner.models import Employee, Analyst, Agent, User, Organization


class EmployeeCreationForm(forms.ModelForm):
    user_first_name = forms.CharField(label='First Name')
    user_last_name = forms.CharField(label='Last Name')
    user_auth_type = forms.CharField(label='Authentication Method')
    user_email = forms.EmailField(label='Email')

    class Meta:
        model = Employee
        fields = ['organization']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # If editing an existing employee
            for field in ['user_first_name', 'user_last_name', 'user_auth_type', 'user_email']:
                self.fields[field].required = False

    def save(self, commit=True):
        if not self.instance.pk:  # Only create user if this is a new employee
            user = User.objects.create_user(
                email=self.cleaned_data['user_email'],
                auth_type=self.cleaned_data['user_auth_type'],
                first_name=self.cleaned_data['user_first_name'],
                last_name=self.cleaned_data['user_last_name'],
            )
            employee = super().save(commit=False)
            employee.user = user
        else:
            employee = Employee.objects.get(pk=self.instance.pk)
            for attr, value in self.cleaned_data.items():
                setattr(employee.user, attr, value)
            employee.user.save()
        if commit:
            employee.save()
        return employee


class AnalystCreationForm(EmployeeCreationForm):
    class Meta(EmployeeCreationForm.Meta):
        model = Analyst
        fields = ['organization']


class AgentCreationForm(EmployeeCreationForm):
    manager = forms.ModelChoiceField(queryset=Agent.objects.all(), required=False)

    class Meta(EmployeeCreationForm.Meta):
        model = Agent
        fields = ['organization', 'manager']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # If editing an existing agent
            self.fields['manager'].queryset = Agent.objects.filter(organization=self.instance.organization)
        else:
            self.fields['manager'].queryset = Agent.objects.none()

    def clean_manager(self):
        manager = self.cleaned_data.get('manager')
        if manager and self.cleaned_data['organization'] != manager.organization:
            raise ValidationError("Manager must belong to the same organization.")
        return manager

    def save(self, commit=True):
        agent = super().save(commit=False)
        agent.manager = self.cleaned_data['manager']
        if commit:
            agent.save()
        return agent


class OrganizationAdminForm(forms.ModelForm):
    """
    Custom form for Organization that handles encrypted Jira API key.
    Provides a plain text input field for the API key that gets encrypted on save.
    """
    ticket_api_key = forms.CharField(
        label='Jira API Key',
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text='Enter your Jira API token. Leave blank to keep existing key. This will be encrypted when saved.'
    )

    class Meta:
        model = Organization
        fields = ['name', 'max_user_count', 'max_topic_count', 'transcription_method',
                  'enrichment_method', 'revenue_search_prefix', 'language',
                  'ticket_account', 'ticket_project', 'ticket_api_key']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing an existing organization with a key, show a placeholder
        if self.instance.pk and self.instance.ticket_key_encrypted:
            self.fields['ticket_api_key'].help_text = '🔒 API key is currently set. Enter a new key to replace it, or leave blank to keep the existing key.'

    def save(self, commit=True):
        organization = super().save(commit=False)

        # Handle API key encryption
        ticket_api_key = self.cleaned_data.get('ticket_api_key')
        if ticket_api_key:
            # New key provided - encrypt it
            organization.store_ticket_key(ticket_api_key)
        # If no key provided and it's a new organization, ticket_key_encrypted remains None
        # If no key provided and it's an existing organization, keep the existing encrypted key

        if commit:
            organization.save()
        return organization
