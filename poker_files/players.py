from enum import Enum

class PlayerStatus(Enum):
    BROKE = 0
    FOLDED = 1
    ALL_IN = 2
    PLAYING = 3

class Player:
    def __init__(self, player, channel, stack=5000):
        self.player = player
        self.stack = stack
        self.channel = channel
        self.status = PlayerStatus.PLAYING
        self.hand = []
        self.channel = None

    def went_broke(self):
        self.status = PlayerStatus.BROKE

    def folded(self):
        self.status = PlayerStatus.FOLDED

    def all_in(self):
        self.status = PlayerStatus.ALL_IN

    def reset_status(self):
        self.status = PlayerStatus.PLAYING
        self.hand = []