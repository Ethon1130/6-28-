"""
ASGI config for Xiaochengx_back project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from Xiaochengx_back import consumers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Xiaochengx_back.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/ascend/", consumers.ImageConsumer.as_asgi()),
        ])
    ),
})
