from django.shortcuts import render
from django.http import JsonResponse
import json
from main.models import User, Game
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()

# 게임 대기열을 세션으로 관리
waiting_players = []

# @login_required
# def game(request):
#     # 현재 로그인한 사용자가 대기열에 있는지 확인
#     if request.user.username not in waiting_players:
#         waiting_players.append(request.user.username)

#     # 대기열에 두 명이 있으면 게임 시작
#     if len(waiting_players) == 2:
#         player1 = User.objects.get(username=waiting_players[0])
#         player2 = User.objects.get(username=waiting_players[1])
#         context = {'player1': player1, 'player2': player2}

#         # 게임을 시작했으므로 대기열 초기화
#         waiting_players.clear()

#         return render(request, 'game/game.html', context)
#     else:
#         # 두 번째 사용자를 기다리는 동안 대기 페이지 표시
#         messages.info(request, '두 번째 사용자를 기다리는 중입니다...')
#         return render(request, 'game/waiting.html')

@login_required
def game_room(request, room_name):
	# player1 = User.objects.get(username="root")
	# player2 = User.objects.get(username="testuser")
	context = {
            'room_name': room_name,
            # 'player1': player1,
            # 'player2': player2
        }
	return render(request, 'game/game.html', context)

def torunament(request):
    context = {'room_name': 'test'}
    return render(request, 'game/torunament.html', context)

def torunament_game(request):
    context = {'room_name': 'test'}
    return render(request, 'game/torunament_game.html', context)

# def update_score(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             player1_username = data.get('player1')
#             player2_username = data.get('player2')
#             player1_score = data.get('player1_score')
#             player2_score = data.get('player2_score')
#             winner_username = data.get('winner')  # JSON에서 전달된 winner 닉네임
            
#             player1 = User.objects.get(username=player1_username)
#             player2 = User.objects.get(username=player2_username)
#             winner = User.objects.get(username=winner_username)

#             # Game 테이블에 새로운 게임 결과 저장
#             game = Game.objects.create(
#                 player1=player1,
#                 score1=player1_score,
#                 player2=player2,
#                 score2=player2_score,
#                 winner=winner
#             )

#             print(game)

#             return JsonResponse({"message": "Score updated successfully"}, status=200)
        
#         except User.DoesNotExist:
#             return JsonResponse({"error": "User not found"}, status=400)
#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON"}, status=400)
#     return JsonResponse({"error": "Invalid request method"}, status=405)