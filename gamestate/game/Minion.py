from typing import Optional, List
from gamestate.game.EntityList import EntityList
from hearthstone.entities import Game, Card
from hearthstone.enums import GameTag
from hearthstone.game_types import GameTagsDict


class Minion(EntityList):
    def __init__(self):
        super().__init__()
        self.game: Game
        self.my_player_id: int
        self.oppo_player_id: int

    def check_minion_attributes(self, minion: Card,
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

    def minion_can_attack(self, minion: Card) -> bool:
        minion_attr = minion.tags
        result = self.check_minion_attributes(
            minion,
            owned_attributes=[GameTag.ATK, GameTag.EXHAUSTED],
            forbidden_attributes=[GameTag.DORMANT, GameTag.FROZEN, GameTag.CANT_ATTACK]
        )
        return result and minion_attr.get(GameTag.ATK) > 0 and (minion_attr.get(GameTag.EXHAUSTED) == 0 or minion_attr.get(GameTag.ATTACKABLE_BY_RUSH))

    def can_beat_face(self, minion: Card) -> bool:
        minion_attr = minion.tags
        result = self.check_minion_attributes(
            minion,
            owned_attributes=[GameTag.ATK, GameTag.EXHAUSTED],
            forbidden_attributes=[GameTag.DORMANT, GameTag.FROZEN, GameTag.CANT_ATTACK]
        )
        return result and minion_attr.get(GameTag.ATK) > 0 and minion_attr.get(GameTag.EXHAUSTED) == 0

    def can_be_pointed_minion(self, minion):
        """ 可以被随从战吼、法术、技能效果指向的随从 """
        forbidden_attributes = [GameTag.STEALTH, GameTag.UNTOUCHABLE, GameTag.DORMANT, GameTag.IMMUNE]
        check_res = self.check_minion_attributes(minion, forbidden_attributes=forbidden_attributes)
        return check_res

    def get_minion_status(self, minion: Card) -> GameTagsDict:
        if hasattr(minion, 'tags'):
            return minion.tags
        else:
            return dict()

    def get_minion_base_info(self, minion: Card) -> GameTagsDict:
        if hasattr(minion, 'base_tags'):
            return minion.base_tags
        else:
            return dict()

    def get_minion_health(self, minion: Card):
        minion_status = self.get_minion_status(minion)
        return minion_status.get(GameTag.HEALTH)

    def get_minion_attack(self, minion: Card):
        minion_status = self.get_minion_status(minion)
        return minion_status.get(GameTag.HEALTH)

    def get_minion_spell_power(self, minion: Card):
        minion_status = self.get_minion_status(minion)
        return minion_status.get(GameTag.SPELLPOWER)
