# window_project/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import member.routing

# ⭐ Set Django settings module FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'window_project.settings')

# ⭐ Get Django ASGI application AFTER settings are set
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            member.routing.websocket_urlpatterns
        )
    ),
})