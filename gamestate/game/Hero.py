

from gamestate.game.Base import Base
from hearthstone.entities import Game
from hearthstone.enums import GameTag


class Hero(Base):
    def __init__(self):
        super().__init__()
        self.game: Game
        self.my_player_id : int
        self.oppo_player_id : int

    @property
    def my_hero_attack(self) -> int:
        return self.my_hero_status.get(GameTag.ATK, 0)
        
    @property
    def oppo_hero_attack(self) -> int:
        return self.oppo_hero_status.get(GameTag.ATK, 0)

    @property
    def my_hero_power(self) -> str:
        status = self.my_hero_status
        dbf_id = status.get(GameTag.HERO_POWER, 0)
        hero_power = self.get_card_name(dbf_id=dbf_id)
        return hero_power

    @property
    def oppo_hero_power(self) -> str:
        status = self.oppo_hero_status
        dbf_id = status.get(GameTag.HERO_POWER, 0)
        hero_power = self.get_card_name(dbf_id=dbf_id)
        return hero_power

    @property
    def oppo_health(self) -> int:
        status = self.oppo_hero_status
        return status.get(GameTag.HEALTH) - status.get(GameTag.DAMAGE, 0)

    @property
    def my_health(self) -> int:
        status = self.my_hero_status
        return status.get(GameTag.HEALTH) - status.get(GameTag.DAMAGE, 0)

    @property
    def oppo_armor(self) -> int:
        status = self.oppo_hero_status
        return status.get(GameTag.ARMOR, 0)

    @property
    def my_armor(self) -> int:
        status = self.my_hero_status
        return status.get(GameTag.ARMOR, 0)