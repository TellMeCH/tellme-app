"""
URL configuration for tellme project.
"""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from two_factor.urls import urlpatterns as tf_urls
from two_factor.admin import AdminSiteOTPRequired

# Any access to /admin/ will now redirect to the 2FA login flow if not authenticated.
admin.site.__class__ = AdminSiteOTPRequired

class PublicSpectacularAPIView(SpectacularAPIView):
    authentication_classes = []
    permission_classes = []


class PublicSpectacularSwaggerView(SpectacularSwaggerView):
    authentication_classes = []
    permission_classes = []

urlpatterns = [
    path('admin/two-factor/', include(tf_urls)), # Views for login, setup, and device management.

    path("api/v1/", include("tellme.call_miner.urls")),
    path("processing/v1/", include('tellme.call_processing.urls')),

    path('admin/', admin.site.urls),

    path('api/schema/', PublicSpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', PublicSpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path("health/", include("health_check.urls")),
]