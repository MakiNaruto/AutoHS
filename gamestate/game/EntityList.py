from typing import List, Iterator
from gamestate.game.Base import Base
from hearthstone.entities import Card, Game, Entity
from hearthstone.enums import CardType, GameTag, Zone


class EntityList(Base):
    def __init__(self):
        super().__init__()
        self.game: Game
        self.my_player_id: int
        self.oppo_player_id: int

    @property
    def all_cards(self) -> Iterator[Entity]:
        return self.game.entities

    @property
    def my_graveyard_cards(self) -> List[Card]:
        return self.cards_pool_filter(self.my_entites, Zone.GRAVEYARD)

    @property
    def oppo_play_minions(self) -> List[Card]:
        """ 敌方桌面上的随从 """
        deck_cards = self.cards_pool_filter(self.my_entites, Zone.PLAY, [CardType.MINION])
        sorted_deck_cards = sorted(deck_cards, key=lambda item: item.tags.get(GameTag.ZONE_POSITION))
        return sorted_deck_cards

    @property
    def my_play_minions(self) -> List[Card]:
        """ 我方桌面上的随从 """
        deck_cards = self.cards_pool_filter(self.oppo_entites, Zone.PLAY, [CardType.MINION])
        sorted_deck_cards = sorted(deck_cards, key=lambda item: item.tags.get(GameTag.ZONE_POSITION))
        return sorted_deck_cards

    @property
    def oppo_play_locations(self) -> List[Card]:
        """ 敌方桌面上的地标 """
        deck_cards = self.cards_pool_filter(self.my_entites, Zone.PLAY, [CardType.LOCATION])
        sorted_deck_cards = sorted(deck_cards, key=lambda item: item.tags.get(GameTag.ZONE_POSITION))
        return sorted_deck_cards

    @property
    def my_play_locations(self) -> List[Card]:
        """ 我方桌面上的地标 """
        deck_cards = self.cards_pool_filter(self.oppo_entites, Zone.PLAY, [CardType.LOCATION])
        sorted_deck_cards = sorted(deck_cards, key=lambda item: item.tags.get(GameTag.ZONE_POSITION))
        return sorted_deck_cards
