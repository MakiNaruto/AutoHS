
from typing import Dict, List, Union
from hearthstone.entities import Game
from hearthstone.cardxml import CardXML, load, load_dbf
from hearthstone.entities import Card, Game
from hearthstone.enums import CardType, Zone


class GameCard:
    def __init__(self):
        super().__init__()
        self.game: Game
        self.my_player_id : int
        self.oppo_player_id : int
        self.dbf_card_db: Dict[str, CardXML] = None
        self.id_card_db: Dict[str, CardXML] = None
        self.init_cards()

    def init_cards(self):
        self.id_card_db, _ = load(locale='zhCN')
        self.dbf_card_db, _ = load_dbf(locale='zhCN')
    
    def get_card_info(self, card_id: int = None, dbf_id: int = None) -> CardXML:
        if card_id:
            return self.id_card_db.get(card_id)
        else:
            return self.dbf_card_db.get(dbf_id)
    
    def get_card_name(self, card_id: int = None, dbf_id: int = None) -> Union[str, None]:
        card = self.get_card_info(card_id=card_id, dbf_id=dbf_id)
        if card:
            return card.name

    def check_card_attributes(self, card: Card, owned_attributes, forbidden_attributes) -> bool:
        """
        过滤炉石卡牌，判断其是否满足指定的属性条件。

        Args:
            owned_attributes: 随从必须拥有的属性列表。
            forbidden_attributes: 随从不允许拥有的属性列表。
            minion_attributes: 待过滤随从的属性列表。

        Returns:
            True 如果随从满足所有条件，False 否则。
        """
        card_attributes = card.tags
        # 检查随从是否拥有所有必需的属性
        has_owned = all(attribute in card_attributes for attribute in owned_attributes)

        # 检查随从是否不包含任何不允许的属性
        is_not_forbidden = not any(attribute in card_attributes for attribute in forbidden_attributes)

        return has_owned and is_not_forbidden

    def cards_pool_filter(self, cards: List[Card], card_zone: Zone, card_type_list: List[CardType] = None) -> List[Card]:
        """ 
        根据条件筛选卡牌
        @param cards: 待筛选卡牌列表
        @param card_zone: 卡片所在的位置, 如手牌, 战场, 墓地等
        @param card_type_list: 卡牌类型列表, 卡牌的属性有在其中才回被返回
        @return: 筛选后的卡牌列表 List[Card]
        """
        if not card_type_list:
            card_type_list = []

        filter_cards = []
        for card in cards:
            zone = card.zone
            if not hasattr(card, 'card_id') or not card.card_id:
                continue
            if zone == card_zone:
                # 有卡牌类型过滤条件
                if card_type_list and card.type not in card_type_list:
                    continue
                filter_cards.append(card)
        return filter_cards



if __name__ == '__main__':
    g = GameCard()
    res = g.get_card_name('TOY_353')
    print(res)
