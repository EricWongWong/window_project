# member/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # ⭐ Remove the ^ from the pattern
    re_path(r'ws/dashboard/$', consumers.DashboardConsumer.as_asgi()),
]

