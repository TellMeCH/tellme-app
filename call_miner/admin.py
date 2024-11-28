from django.contrib import admin
from .models import Organization, Employee, Analyst, Agent, Topic, Customer, Conversation
from .forms import EmployeeCreationForm, AnalystCreationForm, AgentCreationForm


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'description']
    search_fields = ['name', 'organization__name']
    list_filter = ['organization']
    readonly_fields = ['summary', 'summary_date', 'summary_call_count', 'is_active', 'created', 'updated']


class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeCreationForm
    list_display = ['user', 'organization']
    search_fields = ['user__username', 'organization__name']
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
    list_display = ['name', 'organization']
    search_fields = ['name', 'organization__name']
    list_filter = ['organization']
    readonly_fields = ['summary', 'summary_date', 'summary_call_count']


class ConversationAdmin(admin.ModelAdmin):
    list_display = ['path', 'date', 'agent', 'customer', 'duration', 'sentiment']
    search_fields = ['path', 'agent__name', 'customer__name']
    list_filter = ['date', 'agent', 'customer']


# Register the models and their customized admin interfaces
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Analyst, AnalystAdmin)
admin.site.register(Agent, AgentAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Conversation, ConversationAdmin)
