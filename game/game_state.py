# game_state.py
class GameState:
    def __init__(self):
        self.players = {
            'player1': {'x': 0, 'y': 0, 'score': 0},
            'player2': {'x': 0, 'y': 0, 'score': 0}
        }
        self.ball = {'x': 400, 'y': 200, 'dx': 5, 'dy': 5}  # 공의 초기 위치 및 이동 방향

    def update_player_position(self, player, x, y):
        if player in self.players:
            self.players[player]['x'] = x
            self.players[player]['y'] = y

    def update_score(self, player):
        if player in self.players:
            self.players[player]['score'] += 1

    def update_ball_position(self, x, y, dx, dy):
        self.ball['x'] = x
        self.ball['y'] = y
        self.ball['dx'] = dx
        self.ball['dy'] = dy

    def get_game_state(self):
        return {
            'players': self.players,
            'ball': self.ball
        }
