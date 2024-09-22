from django.urls import path, include
from rest_framework.routers import DefaultRouter
from call_miner import views

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
router.register(r'topics', views.TopicViewSet, basename='topic')
router.register(r'agents', views.AgentViewSet, basename='agent')
router.register(r'customers', views.CustomerViewSet, basename='customer')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
