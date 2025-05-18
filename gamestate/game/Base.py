from typing import Iterator, Optional
from gamestate.game.Card import GameCard
from hearthstone.entities import Game, Entity, Card, Player
from hearthstone.game_types import GameTagsDict


class Base(GameCard):
    def __init__(self):
        super().__init__()
        self.game: Game = None
        self.my_player_id: int = 0
        self.oppo_player_id: int = 0

    def get_player(self, player_id) -> Optional[Player]:
        return self.game.get_player(player_id)

    def get_player_entites(self, player_id) -> Iterator[Entity]:
        return self.get_player(player_id).entities

    def get_player_hero(self, player_id) -> Optional[Card]:
        return self.get_player(player_id).hero

    @property
    def my_player(self) -> Optional[Player]:
        return self.get_player(self.my_player_id)

    @property
    def oppo_player(self) -> Optional[Player]:
        return self.get_player(self.oppo_player_id)

    @property
    def my_hero(self) -> Optional["Card"]:
        return self.get_player_hero(self.my_player_id)

    @property
    def oppo_hero(self) -> Optional["Card"]:
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
    def my_entites(self) -> Iterator[Entity]:
        return self.get_player_entites(self.my_player_id)
    
    @property
    def oppo_entites(self) -> Iterator[Entity]:
        return self.get_player_entites(self.oppo_player_id)

    