from django.contrib import admin
from .models import User, Game, Relation  # 사용할 모델을 import

# User 모델을 위한 ModelAdmin 설정
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_active')  # 리스트에서 표시할 필드
    search_fields = ('email', 'username')  # 검색 필드
    list_filter = ('is_active',)           # 필터링할 필드

# Game 모델을 위한 ModelAdmin 설정
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('date', 'player1', 'score1', 'player2', 'score2', 'winner')  # 리스트에서 표시할 필드
    list_filter = ('date', 'winner')  # 필터링할 필드
    search_fields = ('player1__username', 'player2__username')  # 검색 필드, 외래키는 __ 사용

# Relation 모델을 위한 ModelAdmin 설정
@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = ('requester', 'receiver')  # 리스트에서 표시할 필드
    search_fields = ('requester__username', 'receiver__username')  # 검색 필드
