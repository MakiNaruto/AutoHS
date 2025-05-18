from typing import List
from gamestate.game.Base import Base
from hearthstone.entities import Card, Game
from hearthstone.enums import GameTag, Zone


class Hand(Base):
    def __init__(self):
        super().__init__()
        self.game: Game
        self.my_player_id: int
        self.oppo_player_id: int

    def get_card_cost_by_index(self, index):
        """
            根据从左到右的顺序, 找到手牌中指定位置的卡牌, 返回打出需要的COST.
            @param index: 第 index张牌, 下标从0开始.
        """
        hand_card: Card = self.my_hand_cards[index]
        current_cost = hand_card.tags.get(GameTag.TAG_LAST_KNOWN_COST_IN_HAND)
        return current_cost

    def get_card_cost(self, card: Card):
        """
            返回卡牌当前打出所需要的COST
            @param card: 战场, 手中, 卡牌
        """
        current_cost = card.tags.get(GameTag.TAG_LAST_KNOWN_COST_IN_HAND)
        return current_cost

    @property
    def my_hand_cards(self) -> List[Card]:
        hand_cards = self.cards_pool_filter(self.my_entites, Zone.HAND)
        sorted_hand_cards = sorted(hand_cards, key=lambda item: item.tags.get(GameTag.ZONE_POSITION))
        return sorted_hand_cards

    @property
    def oppo_hand_cards(self) -> List[Card]:
        hand_cards = self.cards_pool_filter(self.oppo_entites, Zone.HAND)
        sorted_hand_cards = sorted(hand_cards, key=lambda item: item.tags.get(GameTag.ZONE_POSITION))
        return sorted_hand_cards

    @property
    def my_hand_card_num(self):
        return len(self.my_hand_cards)

    @property
    def oppo_hand_card_num(self):
        return len(self.oppo_hand_cards)
