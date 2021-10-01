from django.urls import re_path

from . import consumers

# run chatconsumer class after websocket connection
websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
]