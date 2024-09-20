from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from call_miner.models import Employee, Analyst, Agent


class EmployeeCreationForm(forms.ModelForm):
    user_username = forms.CharField(label='Username', required=False)
    user_password = forms.CharField(widget=forms.PasswordInput, label='Password', required=False)
    user_email = forms.EmailField(label='Email')

    class Meta:
        model = Employee
        fields = ['organization']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # If editing an existing employee
            self.fields['user_username'].widget.attrs['readonly'] = True
            self.fields['user_password'].required = False  # Don't require password when editing
            self.fields['user_email'].required = False  # Don't require password when editing
        else:  # For new employees
            self.fields['user_password'].required = True

    def clean_user_username(self):
        if self.instance.pk:  # When editing an existing instance
            return self.instance.user.username  # Prevent changes to the username
        else:
            return self.cleaned_data['user_username']

    def clean_user_password(self):
        password = self.cleaned_data['user_password']
        if not self.instance.pk and not password:  # If creating a new employee, password is required
            raise ValidationError('Password is required when creating a new employee.')
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                raise ValidationError({'user_password': e.messages})
        return password

    def save(self, commit=True):
        if not self.instance.pk:  # Only create user if this is a new employee
            user = User.objects.create_user(
                username=self.cleaned_data['user_username'],
                password=self.cleaned_data['user_password'],
                email=self.cleaned_data['user_email'],
            )
            employee = super().save(commit=False)
            employee.user = user
        else:
            employee = super().save(commit=False)
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
