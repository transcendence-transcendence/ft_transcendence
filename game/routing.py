from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'wss/game/room/(?P<room_name>\w+)/$', consumers.GameConsumer.as_asgi()),
]
