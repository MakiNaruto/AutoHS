

from typing import Dict, Generator
from gamestate.game.Card import GameCard
from hearthstone.entities import Game
from hearthstone.game_types import GameTagsDict



class Base(GameCard):
    def __init__(self):
        super().__init__()
        self.game: Game
        self.my_player_id : int
        self.oppo_player_id : int

    def get_player(self, player_id):
        return self.game.get_player(player_id)

    def get_player_entites(self, player_id) -> Generator:
        return self.get_player(player_id).entities

    def get_player_hero(self, player_id):
        return self.get_player(player_id).hero

    @property
    def my_player(self):
        return self.get_player(self.my_player_id)

    @property
    def oppo_player(self):
        return self.get_player(self.oppo_player_id)

    @property
    def my_hero(self):
        return self.get_player_hero(self.my_player_id)

    @property
    def oppo_hero(self):
        return self.get_player_hero(self.oppo_player_id)

    @property
    def my_player_status(self) -> GameTagsDict:
        return self.my_player.tags

    @property
    def oppo_player_status(self) -> GameTagsDict:
        return self.oppo_player.tags

    @property
    def my_hero_status(self) -> GameTagsDict:
        return self.my_hero.tags

    @property
    def oppo_hero_status(self) -> GameTagsDict:
        return self.oppo_hero.tags

    @property
    def my_entites(self) -> Generator:
        return self.get_player_entites(self.my_player_id)
    
    @property
    def oppo_entites(self) -> Generator:
        return self.get_player_entites(self.oppo_player_id)

    