from django.urls import re_path

from . import consumers

# specify chat room url 
websocket_urlpatterns = [
    re_path(r'ws/chat/room/$', consumers.ChatConsumer.as_asgi()),
]