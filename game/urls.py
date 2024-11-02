from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('online/room', views.room, name='room'),  # room_name에 따른 게임방 연결
    path('online/room/<str:room_name>/', views.game, name='online_game'),  # room_name에 따른 게임방 연결
    path('local/torunament/', views.torunament, name='torunament'),  # room_name에 따른 게임방 연결
    path('local/torunament/game', views.torunament_game, name='torunament_game'),  # room_name에 따른 게임방 연결
]
