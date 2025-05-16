from typing import List
from gamestate.game.Card import GameCard
from hearthstone.entities import Card, Game
from hearthstone.enums import GameTag, Zone


class Hand(GameCard):
    def __init__(self):
        super().__init__()
        self.game: Game
        self.my_player_id: int
        self.oppo_player_id: int

    def get_card_cost(self, index):
        """ 会返回这张卡的cost """
        hand_card: Card = self.my_hand_cards[index]
        current_cost = hand_card.tags.get(GameTag.TAG_LAST_KNOWN_COST_IN_HAND)
        return current_cost

    @property
    def my_hand_cards(self) -> List[Card]:
        hand_cards = self.cards_pool_filter(self.my_entites, Zone.HAND)
        sorted_hand_cards = sorted(hand_cards, key=lambda item: item.tags.get(GameTag.ZONE_POSITION))
        return sorted_hand_cards

    @property
    def my_hand_card_num(self):
        return len(self.my_hand_cards)
