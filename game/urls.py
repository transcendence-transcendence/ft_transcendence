from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('online/room', views.RoomView.as_view(), name='room'),  # room_name에 따른 게임방 연결
    path('online/room/<str:room_name>/', views.GameView.as_view(), name='online_game'),  # room_name에 따른 게임방 연결
    path('local/torunament/', views.TournamentView.as_view(), name='torunament'),  # room_name에 따른 게임방 연결
    path('local/torunament/game', views.TournamentGameView.as_view(), name='torunament_game'),  # room_name에 따른 게임방 연결
]
