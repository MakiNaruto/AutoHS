from typing import Optional, List
from gamestate.game.Base import Base
from hearthstone.entities import Game, Card
from hearthstone.enums import CardType, GameTag, Zone
from hearthstone.game_types import GameTagsDict


class Minion(Base):
    def __init__(self):
        super().__init__()
        
    @property
    def play_minions(self) -> list[Card]:
        """ 我方桌面上的随从 """
        deck_cards = self.cards_pool_filter(self.entites, Zone.PLAY, [CardType.MINION])
        sorted_deck_cards = sorted(deck_cards, key=lambda item: item.tags.get(GameTag.ZONE_POSITION))
        return sorted_deck_cards

    @property
    def play_locations(self) -> list[Card]:
        """ 我方桌面上的地标 """
        deck_cards = self.cards_pool_filter(self.entites, Zone.PLAY, [CardType.LOCATION])
        sorted_deck_cards = sorted(deck_cards, key=lambda item: item.tags.get(GameTag.ZONE_POSITION))
        return sorted_deck_cards


def check_minion_attributes(minion: Card,
                            owned_attributes: Optional[List[GameTag]] = None,
                            forbidden_attributes: Optional[List[GameTag]] = None
                            ) -> bool:
    """
    根据条件筛选卡牌
    @param minion: 随从必须拥有的属性列表
    @param owned_attributes: 随从不允许拥有的属性列表
    @param forbidden_attributes: 待过滤随从的属性列表
    @return:  True 如果随从满足所有条件，否则False 。
    """
    if forbidden_attributes is None:
        forbidden_attributes = []
    if owned_attributes is None:
        owned_attributes = []
    minion_attributes = minion.tags
    # 检查随从是否拥有所有必需的属性
    has_owned = all(attribute in minion_attributes for attribute in owned_attributes)

    # 检查随从是否不包含任何不允许的属性
    is_not_forbidden = not any(attribute in minion_attributes for attribute in forbidden_attributes)

    return has_owned and is_not_forbidden

def minion_can_attack(minion: Card) -> bool:
    minion_attr = minion.tags
    result = check_minion_attributes(
        minion,
        owned_attributes=[GameTag.ATK, GameTag.EXHAUSTED],
        forbidden_attributes=[GameTag.DORMANT, GameTag.FROZEN, GameTag.CANT_ATTACK]
    )
    return result and minion_attr.get(GameTag.ATK) > 0 and (minion_attr.get(GameTag.EXHAUSTED) == 0 or minion_attr.get(GameTag.ATTACKABLE_BY_RUSH))

def can_beat_face(minion: Card) -> bool:
    minion_attr = minion.tags
    result = check_minion_attributes(
        minion,
        owned_attributes=[GameTag.ATK, GameTag.EXHAUSTED],
        forbidden_attributes=[GameTag.DORMANT, GameTag.FROZEN, GameTag.CANT_ATTACK]
    )
    return result and minion_attr.get(GameTag.ATK) > 0 and minion_attr.get(GameTag.EXHAUSTED) == 0

def can_be_pointed_minion(minion):
    """ 可以被随从战吼、法术、技能效果指向的随从 """
    forbidden_attributes = [GameTag.STEALTH, GameTag.UNTOUCHABLE, GameTag.DORMANT, GameTag.IMMUNE]
    check_res = check_minion_attributes(minion, forbidden_attributes=forbidden_attributes)
    return check_res

def get_minion_status(minion: Card) -> GameTagsDict:
    if hasattr(minion, 'tags'):
        return minion.tags
    else:
        return dict()

def get_minion_base_info(minion: Card) -> GameTagsDict:
    if hasattr(minion, 'base_tags'):
        return minion.base_tags
    else:
        return dict()

def get_minion_health(minion: Card):
    minion_status = get_minion_status(minion)
    return minion_status.get(GameTag.HEALTH) - minion_status.get(GameTag.DAMAGE)

def get_minion_attack(minion: Card):
    minion_status = get_minion_status(minion)
    return minion_status.get(GameTag.ATK)

def get_minion_spell_power(minion: Card):
    minion_status = get_minion_status(minion)
    return minion_status.get(GameTag.SPELLPOWER)
