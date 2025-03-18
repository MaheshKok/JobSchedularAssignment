from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/jobs/", consumers.JobConsumer.as_asgi()),
]
