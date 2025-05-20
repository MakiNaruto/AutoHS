from typing import Iterator, Optional
from gamestate.game.Card import GameCard
from hearthstone.entities import Game, Entity, Card, Player
from hearthstone.game_types import GameTagsDict


class Base(GameCard):
    def __init__(self):
        super().__init__()
        self.game: Game = None
        self.player_id: int = 0

    @property
    def player_info(self) -> Optional[Player]:
        return self.game.get_player(self.player_id)

    @property
    def hero(self) -> Optional[Card]:
        return self.player_info.hero

    @property
    def player_status(self) -> GameTagsDict:
        return self.player_info.tags

    @property
    def hero_status(self) -> GameTagsDict:
        return self.hero.tags

    @property
    def entites(self) -> Iterator[Entity]:
        return self.player_info.entities
