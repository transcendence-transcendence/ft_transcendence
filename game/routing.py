from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/game/online/solo/(?P<room_name>\w+)/$', consumers.GameConsumer.as_asgi()),
    re_path(r'ws/game/tournament/solo)/$', consumers.GameConsumer.as_asgi()),
]

# websocket_urlpatterns = [
#     re_path(r'ws/game/(?P<room_name>\w+)/$', GameConsumer.as_asgi()),
# ]
