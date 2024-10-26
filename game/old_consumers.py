# game/consumers.py
import json
import asyncio  # 추가
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.http import JsonResponse
from django.core.handlers.asgi import ASGIRequest
from django.urls import reverse
from django.test import RequestFactory
from .game.views import update_score

class GameState:
    def __init__(self):
        self.players = {
            'root': {'x': 0, 'y': 0, 'score': 0, 'ready': False},  # ready 상태 추가
            'testuser': {'x': 0, 'y': 0, 'score': 0, 'ready': False}   # ready 상태 추가
        }
        self.ball = {'x': 400, 'y': 200, 'dx': 5, 'dy': 5}  # 공의 초기 위치 및 이동 방향

    def update_player_position(self, player, x, y):
        if player in self.players:
            self.players[player]['x'] = x
            self.players[player]['y'] = y

    def update_ball_position(self, x, y, dx, dy):
        self.ball['x'] = x
        self.ball['y'] = y
        self.ball['dx'] = dx
        self.ball['dy'] = dy

    def set_ready(self, player, ready):
        """플레이어의 준비 상태를 업데이트"""
        if player in self.players:
            self.players[player]['ready'] = ready  # 플레이어의 ready 상태 업데이트

    def update_score(self, player, score):
        if player in self.players:
            self.players[player]['score'] = score
            print(player)
            print(self.players[player]['score'])

    def get_game_state(self):
        return {
            'players': self.players,
            'ball': self.ball
        }

# 방마다 게임 상태 저장을 위한 딕셔너리
game_states = {}

class GameConsumer(AsyncWebsocketConsumer):
    players_ready = {}  # 유저 이름을 기반으로 준비 상태를 관리
    connected_clients = []

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'game_%s' % self.room_name

        self.connected_clients.append(self.channel_name)
        
        # 게임방 상태가 없으면 새로 생성
        if self.room_group_name not in game_states:
            game_states[self.room_group_name] = GameState()

        # 그룹에 연결
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # 서버에서 3초 대기 처리
        await self.send(text_data=json.dumps({
            'type': 'wait',
            'message': 'Please wait for 3 seconds...'
        }))

        await asyncio.sleep(3)  # 3초 대기

        # 현재 저장된 게임 상태를 클라이언트로 전송하여 복원
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'data': game_states[self.room_group_name].get_game_state()
        }))

    async def disconnect(self, close_code):
        # 그룹에서 연결 해제
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # 연결된 클라이언트 목록에서 제거
        if self.channel_name in self.connected_clients:
            self.connected_clients.remove(self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data['type'] == 'ready':
            player = data['player']
            ready = data['ready']

            # 준비 상태 업데이트
            # self.players_ready[player] = ready
            game_states[self.room_group_name].set_ready(player, ready)  # 유저의 준비 상태 업데이트
            print(game_states[self.room_group_name].players.values())

            # 두 플레이어 모두 준비되었는지 확인
            if all(player['ready'] for player in game_states[self.room_group_name].players.values()):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'start_game',
                    }
                )

        elif data['type'] == 'paddle_move':
        #elif data['type'] == 'paddle_move' and all(player['ready'] for player in game_states[self.room_group_name].players.values()):
            player = data['player']
            position = data['position']
            game_states[self.room_group_name].update_player_position(player, 0, position)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'paddle_move',
                    'player': player,
                    'position': position
                }
            )
        
        elif data['type'] == 'score_update':
            player1_score = data['player1_score']
            player2_score = data['player2_score']

            # 스코어를 중복 업데이트하지 않도록 한 클라이언트에서만 업데이트
            if self.channel_name == self.connected_clients[0]:
                game_states[self.room_group_name].update_score('root', player1_score)
                game_states[self.room_group_name].update_score('testuser', player2_score)
                await self.handle_score_update(player1_score, player2_score)
                # await asyncio.sleep(3)

                # 다른 클라이언트들에게 스코어 전송
                # await self.channel_layer.group_send(
                #     self.room_group_name,
                #     {
                #         'type': 'score_update',
                #         'player1_score': player1_score,
                #         'player2_score': player2_score
                #     }
                # )

        elif data['type'] == 'ball_move':
            game_states[self.room_group_name].update_ball_position(
                data['x'], data['y'], data['dx'], data['dy']
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'ball_move',
                    'x': data['x'],
                    'y': data['y'],
                    'dx': data['dx'],
                    'dy': data['dy']
                }
            )

        # 게임 종료 시 점수 업데이트
        elif data['type'] == 'game_over':
            await self.handle_game_over(data)

    async def handle_score_update(self, player1_score, player2_score):
        # 점수를 업데이트하고 클라이언트들에게 전송
        game_states[self.room_group_name].update_score('root', player1_score)
        game_states[self.room_group_name].update_score('testuser', player2_score)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'score_update',
                'player1_score': player1_score,
                'player2_score': player2_score
            }
        )

        # 3초 대기
        await asyncio.sleep(3)

        # 공의 위치를 리셋하고 클라이언트들에게 게임 재시작 신호 전송
        game_states[self.room_group_name].update_ball_position(400, 200, 5, 5)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'start_game',
            }
        )
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'ball_move',
                'x': game_states[self.room_group_name].ball['x'],
                'y': game_states[self.room_group_name].ball['y'],
                'dx': game_states[self.room_group_name].ball['dx'],
                'dy': game_states[self.room_group_name].ball['dy']
            }
        )
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         'type': 'game_state',
        #     }
        # )

    async def start_game(self, event):
        await self.send(text_data=json.dumps({
            'type': 'start_game'
        }))

    async def paddle_move(self, event):
        await self.send(text_data=json.dumps({
            'type': 'paddle_move',
            'player': event['player'],
            'position': event['position']
        }))

    async def ball_move(self, event):
        await self.send(text_data=json.dumps({
            'type': 'ball_move',
            'x': event['x'],
            'y': event['y'],
            'dx': event['dx'],
            'dy': event['dy']
        }))
    # 추가된 score_update 핸들러
    async def score_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'score_update',
            'player1_score': event['player1_score'],
            'player2_score': event['player2_score']
        }))

    async def handle_game_over(self, data):
        """한 클라이언트만 게임 종료 메시지를 전송하고 처리"""
        # 현재 연결된 클라이언트 중 하나만 게임 종료 메시지를 전송
        if len(self.connected_clients) > 0:
            primary_client = self.connected_clients[0]  # 첫 번째 클라이언트를 대표로 선택
            if self.channel_name == primary_client:
                # 중복 방지를 위해 한 클라이언트만 게임 종료 메시지를 처리
                await self.process_game_over(data)

    @sync_to_async
    def process_game_over(self, data):
        """게임 종료 후 점수 데이터를 Django 뷰에 전달"""
        # WebSocket에서 받은 데이터를 POST 요청으로 변환
        factory = RequestFactory()
        request = factory.post(reverse('update_score'), json.dumps(data), content_type='application/json')

        # update_score 뷰 호출
        response = update_score(request)

        # response를 반환하지는 않지만, 에러를 로그로 남기거나 추가 처리할 수 있음
        if response.status_code == 200:
            print("Score updated successfully.")
        else:
            print("Error updating score:", response.content)
