"""
ASGI config for tellme project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tellme.settings')
django_asgi_app = get_asgi_application()

from tellme.call_processing.consumers import AudioHookConsumer

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # WebSocket support temporarily disabled due to Google Cloud API Gateway limitations
    # API Gateway does not support WebSocket connections as of December 2025
    # See: https://cloud.google.com/api-gateway/docs/limitations
    #
    # "websocket": AuthMiddlewareStack(
    #     URLRouter([
    #         path("ws/audiohook/", AudioHookConsumer.as_asgi()),
    #     ])
    # ),
})
