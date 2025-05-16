from gamestate.game.Hero import Hero
from gamestate.game.Minion import Minion
from hearthstone.entities import Game
from hearthstone.enums import GameTag


class Player(Hero, Minion):
    def __init__(self):
        super().__init__()
        self.game: Game
        self.my_player_id: int
        self.oppo_player_id: int

    @property
    def oppo_minion_num(self) -> int:
        return len(self.oppo_play_minions)

    @property
    def my_minion_num(self) -> int:
        return len(self.my_play_minions)

    @property
    def my_remaining_resources(self) -> int:
        status = self.my_player_status
        return status.get(GameTag.RESOURCES) + status.get(GameTag.TEMP_RESOURCES, 0) - status.get(GameTag.RESOURCES_USED)
