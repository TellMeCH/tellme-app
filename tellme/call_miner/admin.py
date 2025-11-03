from django.contrib import admin
from .models import (
    PeriodSummary, Organization, Employee, Analyst, Agent, Topic, SuggestedTopic, Customer, Conversation, User
)
from .forms import EmployeeCreationForm, AnalystCreationForm, AgentCreationForm


class PeriodSummaryAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'object_id', 'period_type', 'period_label', 'call_count', 'last_call_at']
    readonly_fields = ['created', 'updated']


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'auth_type']
    search_fields = ['first_name', 'email']


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'description']
    search_fields = ['name', 'organization__name']
    list_filter = ['organization']
    readonly_fields = ['is_active', 'created', 'updated']


class SuggestedTopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'description']
    search_fields = ['name', 'organization__name']
    list_filter = ['organization']
    readonly_fields = ['created', 'updated']


class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeCreationForm
    list_display = ['user', 'user__first_name', 'user__last_name', 'organization']
    search_fields = ['user__email', 'organization__name']
    list_filter = ['organization']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ['user', 'created', 'updated', 'is_organization_admin', 'role']
        return []


class AnalystAdmin(admin.ModelAdmin):
    form = AnalystCreationForm
    list_display = ['user', 'organization']
    search_fields = ['user__username', 'organization__name']
    list_filter = ['organization']


class AgentAdmin(EmployeeAdmin):
    form = AgentCreationForm
    list_display = ['user', 'organization', 'manager']
    search_fields = ['user__username', 'organization__name', 'manager__user__username']
    list_filter = ['organization']


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['external_id', 'organization', 'first_name', 'last_name', 'birth_date', 'postcode', 'loyalty_number']
    search_fields = ['external_id', 'organization__name', 'first_name', 'last_name']
    list_filter = ['organization']


class ConversationAdmin(admin.ModelAdmin):
    list_display = ['path', 'date', 'agent', 'customer', 'duration', 'sentiment', 'starting_sentiment',
                    'ending_sentiment']
    search_fields = ['path', 'agent__name', 'customer__name']
    list_filter = ['date', 'agent']
    sortable_by = ['date', 'agent']


# Register the models and their customized admin interfaces
admin.site.register(PeriodSummary, PeriodSummaryAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(SuggestedTopic, SuggestedTopicAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Analyst, AnalystAdmin)
admin.site.register(Agent, AgentAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Conversation, ConversationAdmin)
