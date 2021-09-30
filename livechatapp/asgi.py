"""
ASGI config for livechatapp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing
from channels.routing import get_default_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'livechatapp.settings')

django.setup()

application = get_default_application()
