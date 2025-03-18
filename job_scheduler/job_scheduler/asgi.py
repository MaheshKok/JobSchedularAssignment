import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from jobs.routing import websocket_urlpatterns
import jobs

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "job_scheduler.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "job_scheduler.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter(jobs.routing.websocket_urlpatterns)),
    }
)
