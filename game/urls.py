# main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('online/solo/<str:room_name>/', views.game_room, name='game_room'),  # room_name에 따른 게임방 연결
    path('torunament/solo/', views.torunament, name='torunament'),  # room_name에 따른 게임방 연결
    path('torunament/solo/game', views.torunament_game, name='torunament_game'),  # room_name에 따른 게임방 연결
	# path('update-score/', views.update_score, name='update_score'),
]
