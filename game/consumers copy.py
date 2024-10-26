# game/consumers.py
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

# 게임 상태를 관리하는 클래스
class GameState:
    def __init__(self, player1, player2):
        self.players = {
            player1: {'y': 150, 'score': 0, 'ready': False, 'direction': 0},
            player2: {'y': 150, 'score': 0, 'ready': False, 'direction': 0}
        }
        self.ball = {'x': 400, 'y': 200, 'dx': 5, 'dy': 5}
        self.paddle_width = 10
        self.paddle_height = 100
        self.canvas_width = 800
        self.canvas_height = 400
        self.ball_radius = 10
        self.game_task = None
        self.player1 = player1
        self.player2 = player2
        self.paddle_speed = 7  # 패들의 속도

    def update_player_direction(self, player, direction):
        if player in self.players:
            self.players[player]['direction'] = direction

    def update_positions(self):
        # 패들 위치 업데이트
        for player in [self.player1, self.player2]:
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

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'game_%s' % self.room_name

        # 플레이어 이름 추출 (예: room_name이 'root_vs_testuser' 형태라고 가정)
        player_names = self.room_name.split('_vs_')
        if len(player_names) != 2:
            await self.close()
            return
        
        self.player1, self.player2 = player_names

        # 현재 접속한 사용자 이름 가져오기
        self.player_name = self.scope['user'].username

        # 게임 상태 초기화
        if self.room_group_name not in game_states:
            game_states[self.room_group_name] = GameState(self.player1, self.player2)

        # 그룹에 연결
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

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

    async def receive(self, text_data):
        data = json.loads(text_data)
        game_state = game_states[self.room_group_name]

        if data['type'] == 'ready':
            player = data['player']
            ready = data['ready']
            game_state.players[player]['ready'] = ready

            if all(p['ready'] for p in game_state.players.values()):
                # 게임 루프 시작
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
        game_state = game_states[self.room_group_name]
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
            if game_state.players[self.player1]['score'] >= 5 or game_state.players[self.player2]['score'] >= 5:
                winner = self.player1 if game_state.players[self.player1]['score'] >= 5 else self.player2
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_over',
                        'winner': winner
                    }
                )
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
            'winner': event['winner']
        }))
