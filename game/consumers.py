# game/consumers.py
import json
import asyncio
import time
from asgiref.sync import sync_to_async
from main.models import User, Game
from channels.generic.websocket import AsyncWebsocketConsumer

# 게임 상태를 관리하는 클래스
class GameState:
    def __init__(self):
        self.players = {}
        self.ball = {'x': 400, 'y': 200, 'dx': 8, 'dy': 8}
        self.paddle_width = 10
        self.paddle_height = 100
        self.canvas_width = 800
        self.canvas_height = 400
        self.ball_radius = 10
        self.game_task = None
        self.player1 = None
        self.player2 = None
        self.paddle_speed = 12  # 패들의 속도
        self.disconnection_time = None
        self.locked = False

    def add_player(self, username):
        if self.locked:
            # 방이 잠긴 상태면 새로운 플레이어를 추가하지 않음
            return False

        if username in self.players:
            # 이미 존재하는 플레이어이면 연결 상태만 업데이트
            self.players[username]['connected'] = True
        elif self.player1 is None:
            self.player1 = username
            self.players[username] = {
                'y': 150,
                'score': 0,
                'ready': False,
                'direction': 0,
                'connected': True
            }
        elif self.player2 is None:
            self.player2 = username
            self.players[username] = {
                'y': 150,
                'score': 0,
                'ready': False,
                'direction': 0,
                'connected': True
            }
        else:
            # 이미 두 명의 플레이어가 있음
            pass
        return True

    def set_ready(self, player, ready):
        if player in self.players:
            self.players[player]['ready'] = ready

    def update_player_direction(self, player, direction):
        if player in self.players:
            self.players[player]['direction'] = direction

    def update_positions(self):
        # 연결된 플레이어만 업데이트
        for player in [self.player1, self.player2]:
            if self.players[player]['connected']:
                direction = self.players[player]['direction']
                if direction != 0:
                    new_y = self.players[player]['y'] + direction * self.paddle_speed
                    # 경계 체크
                    new_y = max(0, min(self.canvas_height - self.paddle_height, new_y))
                    self.players[player]['y'] = new_y

        # 공 이동
        self.ball['x'] += self.ball['dx']
        self.ball['y'] += self.ball['dy']

        # 상하 벽 충돌
        if self.ball['y'] - self.ball_radius <= 0 or self.ball['y'] + self.ball_radius >= self.canvas_height:
            self.ball['dy'] *= -1

        # 패들 충돌 및 득점 처리
        # 플레이어 1 패들과 충돌
        if self.ball['x'] - self.ball_radius <= self.paddle_width:
            paddle = self.players[self.player1]
            if paddle['y'] <= self.ball['y'] <= paddle['y'] + self.paddle_height:
                self.ball['dx'] *= -1
            else:
                self.players[self.player2]['score'] += 1
                self.reset_ball()
        # 플레이어 2 패들과 충돌
        elif self.ball['x'] + self.ball_radius >= self.canvas_width - self.paddle_width:
            paddle = self.players[self.player2]
            if paddle['y'] <= self.ball['y'] <= paddle['y'] + self.paddle_height:
                self.ball['dx'] *= -1
            else:
                self.players[self.player1]['score'] += 1
                self.reset_ball()

    def reset_ball(self):
        self.ball['x'] = self.canvas_width / 2
        self.ball['y'] = self.canvas_height / 2
        self.ball['dx'] *= -1  # 방향 반전

    def get_game_state(self):
        return {
            'players': self.players,
            'ball': self.ball
        }

# 방마다 게임 상태 저장을 위한 딕셔너리
game_states = {}
room_users = {}

# 플레이어가 참여 중인 방을 추적
active_players = {}

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'game_%s' % self.room_name
     
        # 현재 접속한 사용자 이름 가져오기
        self.username = self.scope['user'].username

        # 플레이어가 이미 다른 방에 참여 중인지 확인
        if self.username in active_players:
            # 다른 방에 참여 중인 경우
            await self.close()
            return

        # 방에 대한 사용자 목록 초기화
        if self.room_group_name not in room_users:
            room_users[self.room_group_name] = []

        if self.username not in room_users[self.room_group_name]:
            room_users[self.room_group_name].append(self.username)

        # 게임 상태 초기화
        if self.room_group_name not in game_states:
            game_states[self.room_group_name] = GameState()

        # room_group_name 에 해당하는 game_state 가져오기.
        self.game_state = game_states[self.room_group_name]

        await self.accept()

        # 플레이어 추가 또는 연결 상태 업데이트
        if self.username in self.game_state.players:
            # 재접속한 플레이어
            self.game_state.players[self.username]['connected'] = True
            self.game_state.disconnection_time = None
        else:
            if not self.game_state.add_player(self.username):
                await self.close()
                return

        # 플레이어를 활성 플레이어 목록에 추가
        active_players[self.username] = self.room_name

        # 그룹에 연결
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # 현재 저장된 게임 상태를 클라이언트로 전송하여 복원
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'data': self.game_state.get_game_state()
        }))

        # 두 플레이어의 정보 전달 (players_ready 이벤트)
        if self.game_state.player1 and self.game_state.player2:
            self.game_state.locked = True
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'players_ready',
                    'player1': self.game_state.player1,
                    'player2': self.game_state.player2
                }
            )

    async def disconnect(self, code):
        # 그룹에서 연결 해제
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # 플레이어의 연결 상태를 False로 설정
        if self.username in self.game_state.players:
            self.game_state.players[self.username]['connected'] = False

        # 플레이어가 모두 방에서 나갔을 때 타이머 시작.
        if all(not player_data['connected'] for player_data in self.game_state.players.values()):
            self.game_state.disconnection_time = time.time()

        # active_players에서 해당 플레이어 삭제
        if self.username in active_players:
            del active_players[self.username]

    async def receive(self, text_data):
        data = json.loads(text_data)
        game_state = self.game_state

        if data['type'] == 'ready':
            player = data['player']
            ready = data['ready']
            game_state.set_ready(player, ready)

            # 모든 플레이어의 준비 상태를 확인
            if all(p['ready'] for p in game_state.players.values()) and len(game_state.players) == 2:
                # 게임 루프가 이미 시작되었는지 확인
                if not game_state.game_task:
                    game_state.game_task = asyncio.create_task(self.game_loop())
                # 모든 클라이언트에게 게임 시작 알림
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'start_game',
                    }
                )

        elif data['type'] == 'paddle_move':
            player = data['player']
            direction = data['direction']
            game_state.update_player_direction(player, direction)

        elif data['type'] == 'paddle_stop':
            player = data['player']
            game_state.update_player_direction(player, 0)

    async def game_loop(self):
        game_state = self.game_state
        while True:
            # 게임 상태 업데이트
            game_state.update_positions()

            # 모든 클라이언트에게 게임 상태 전송
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_state_update',
                    'game_state': game_state.get_game_state()
                }
            )

            # 게임 종료 체크
            if game_state.players[game_state.player1]['score'] >= 5 or game_state.players[game_state.player2]['score'] >= 5:
                winner = game_state.player1 if game_state.players[game_state.player1]['score'] >= 5 else game_state.player2
                
                # 게임 결과를 DB에 저장
                await self.save_game_result(
                    player1=self.game_state.player1,
                    player2=self.game_state.player2,
                    player1_score=self.game_state.players[self.game_state.player1]['score'],
                    player2_score=self.game_state.players[self.game_state.player2]['score'],
                    winner=winner
                )
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_over',
                        'winner': winner
                    }
                )
                if self.room_group_name in game_states:
                    self.game_state.locked = False
                    del game_states[self.room_group_name]
                if self.room_group_name in room_users:
                    del room_users[self.room_group_name]
                game_state.game_task = None
                break

            if game_state.disconnection_time:
                elapsed_time = time.time() - game_state.disconnection_time
                if elapsed_time >= 60:
                    # 시간 초과, 게임 강제 종료
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'game_over',
                            'winner': "None (Time Out)"
                        }
                    )
                    if self.room_group_name in game_states:
                        self.game_state.locked = False
                        del game_states[self.room_group_name]
                    if self.room_group_name in room_users:
                        del room_users[self.room_group_name]
                    game_state.game_task = None
                    break

            await asyncio.sleep(1/60)  # 60FPS

    async def game_state_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'data': event['game_state']
        }))

    async def start_game(self, event):
        await self.send(text_data=json.dumps({
            'type': 'start_game'
        }))

    async def game_over(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_over',
            'winner': event['winner'],
            'location': '/'
        }))

    async def players_ready(self, event):
        # 두 플레이어의 정보를 클라이언트에 전달
        await self.send(text_data=json.dumps({
            'type': 'players_ready',
            'player1': event['player1'],
            'player2': event['player2']
        }))
    
    async def save_game_result(self, player1, player2, player1_score, player2_score, winner, game_type='', round=1):
        """게임 결과를 데이터베이스에 저장"""
        try:
            # player1, player2, winner의 User 객체 가져오기
            player1_user = await sync_to_async(User.objects.get)(username=player1)
            player2_user = await sync_to_async(User.objects.get)(username=player2)
            winner_user = await sync_to_async(User.objects.get)(username=winner)

            # Game 모델에 게임 기록 저장
            await sync_to_async(Game.objects.create)(
                player1=player1_user,
                score1=player1_score,
                player2=player2_user,
                score2=player2_score,
                winner=winner_user,
                game_type=game_type,
                round=round
            )

            print("게임 결과가 성공적으로 저장되었습니다.")
        except User.DoesNotExist:
            print("플레이어 정보를 찾을 수 없습니다.")
        except Exception as e:
            print(f"게임 결과 저장 중 오류 발생: {e}")