from django.contrib import admin
from .models import Organization, Topic, Analyst, Manager, Agent, Customer, Conversation


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name']  # Only the name is available
    search_fields = ['name']  # Allow searching by name


class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'description']
    search_fields = ['name', 'organization__name']
    list_filter = ['organization']


class AnalystAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization']
    search_fields = ['name', 'organization__name']
    list_filter = ['organization']


class ManagerAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization']
    search_fields = ['name', 'organization__name']
    list_filter = ['organization']


class AgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'slug']
    search_fields = ['name', 'organization__name']
    list_filter = ['organization']


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'slug']
    search_fields = ['name', 'organization__name']
    list_filter = ['organization']


class ConversationAdmin(admin.ModelAdmin):
    list_display = ['path', 'date', 'agent', 'customer', 'duration', 'sentiment']
    search_fields = ['path', 'agent__name', 'customer__name']
    list_filter = ['date', 'agent', 'customer']


# Register the models and their customized admin interfaces
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Analyst, AnalystAdmin)
admin.site.register(Manager, ManagerAdmin)
admin.site.register(Agent, AgentAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Conversation, ConversationAdmin)