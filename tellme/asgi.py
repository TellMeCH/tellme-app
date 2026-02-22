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
    # WebSocket traffic for /ws/audiohook/ is routed directly to Cloud Run via the Load Balancer,
    # bypassing the API Gateway (which does not support WebSockets).
    # Authentication is handled by EphemeralTokenAuthentication inside AudioHookConsumer.
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/audiohook/", AudioHookConsumer.as_asgi()),
        ])
    ),
})
