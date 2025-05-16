

from gamestate.game.EntityList import EntityList
from hearthstone.entities import Game, Card
from hearthstone.enums import GameTag


class Minion(EntityList):
    def __init__(self):
        super().__init__()
        self.game: Game
        self.my_player_id : int
        self.oppo_player_id : int

    def check_minion_attributes(self, minion: Card, owned_attributes, forbidden_attributes) -> bool:
        """
        过滤炉石随从，判断其是否满足指定的属性条件。

        Args:
            owned_attributes: 随从必须拥有的属性列表。
            forbidden_attributes: 随从不允许拥有的属性列表。
            minion_attributes: 待过滤随从的属性列表。

        Returns:
            True 如果随从满足所有条件，False 否则。
        """
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

    def can_be_pointed_minion(self, entity):
        """ 可以被随从战吼、法术、技能效果指向的随从 """
        forbidden_attributes = [GameTag.STEALTH, GameTag.UNTOUCHABLE, GameTag.DORMANT, GameTag.IMMUNE]
        check_res = self.check_minion_attributes(entity, forbidden_attributes=forbidden_attributes)
        return check_res

    def get_minion_status(self, entity: Card):
        return entity.tags
    
    def get_minion_base_info(self, entity: Card):
        return entity.base_tags

    @property
    def touchable_oppo_minions(self):
        ret = []

        for oppo_minion in self.oppo_play_minions:
            check_res = self.check_minion_attributes(oppo_minion, owned_attributes=[GameTag.TAUNT])
            if check_res and self.can_be_pointed_minion(oppo_minion):
                ret.append(oppo_minion)

        if len(ret) == 0:
            for oppo_minion in self.oppo_play_minions:
                if self.can_be_pointed_minion(oppo_minion):
                    ret.append(oppo_minion)

        return ret