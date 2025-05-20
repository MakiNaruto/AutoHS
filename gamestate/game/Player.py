from typing import Iterator
from gamestate.game.Hand import Hand
from gamestate.game.Hero import Hero
from gamestate.game.Minion import Minion
from hearthstone.entities import Game, Entity, Card
from hearthstone.enums import GameTag, Zone
from strategy.Heuristic import Heuristic


class Player(Hero, Minion, Hand):
    def __init__(self, game, player_id):
        super().__init__()
        self.game: Game = game
        self.player_id: int = player_id
        self.heuristic = Heuristic(player=self)

    @property
    def minion_num(self) -> int:
        return len(self.play_minions)

    @property
    def remaining_resources(self) -> int:
        status = self.player_status
        return status.get(GameTag.RESOURCES) + status.get(GameTag.TEMP_RESOURCES, 0) - status.get(GameTag.RESOURCES_USED)

    @property
    def total_resources(self) -> int:
        status = self.player_status
        return status.get(GameTag.RESOURCES)

    @property
    def all_cards(self) -> Iterator[Entity]:
        return self.game.entities

    @property
    def graveyard_cards(self) -> list[Card]:
        return self.cards_pool_filter(self.entites, Zone.GRAVEYARD)


