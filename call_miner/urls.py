from django.urls import path, include
from rest_framework.routers import DefaultRouter
from call_miner import views

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
router.register(r'organizations', views.OrganizationViewSet, basename='organization')
router.register(r'api-keys', views.OrganizationAPIKeyViewSet, basename='api-key')
router.register(r'topics', views.TopicViewSet, basename='topic')
router.register(r'agents', views.AgentViewSet, basename='agent')
router.register(r'customers', views.CustomerViewSet, basename='customer')
router.register(r'employees', views.EmployeeViewSet, basename='employee')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
