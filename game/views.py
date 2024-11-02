from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from main.models import User, Game
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()

# 게임 대기열을 세션으로 관리
waiting_players = []

@login_required
def room(request):
    if not request.user.is_otp_verified:
        return redirect('login')
    return render(request, 'game/room.html')

@login_required
def game(request, room_name):
    if not request.user.is_otp_verified:
        return redirect('login')
    context = {'room_name': room_name}
    return render(request, 'game/game.html', context)

def torunament(request):
    if not request.user.is_otp_verified:
        return redirect('login')
    context = {'room_name': 'test'}
    return render(request, 'game/torunament.html', context)

def torunament_game(request):
    if not request.user.is_otp_verified:
        return redirect('login')
    context = {'room_name': 'test'}
    return render(request, 'game/torunament_game.html', context)
