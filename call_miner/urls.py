from django.urls import path, include
from rest_framework.routers import DefaultRouter
from call_miner import views

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r'conversations', views.ConversationViewSet, basename='conversation')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
