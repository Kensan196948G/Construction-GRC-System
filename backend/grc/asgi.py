"""
ASGI config for Construction-GRC-System.

WebSocket対応準備済み。将来的にChannelsを導入する際は
ProtocolTypeRouterでHTTPとWebSocketをルーティングする。

Usage (uvicorn):
    uvicorn grc.asgi:application --host 0.0.0.0 --port 8000

Usage (daphne):
    daphne grc.asgi:application
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grc.settings.development")

# Django ASGI application
django_asgi_app = get_asgi_application()

# 将来的にdjango-channelsを導入する場合:
#
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
#
# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": AuthMiddlewareStack(
#         URLRouter([
#             # WebSocket URL patterns here
#             # e.g., path("ws/risks/", RiskConsumer.as_asgi()),
#             # e.g., path("ws/notifications/", NotificationConsumer.as_asgi()),
#         ])
#     ),
# })

application = django_asgi_app
