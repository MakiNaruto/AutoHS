from gamestate.game.Weapon import Weapon
from hearthstone.entities import Game
from hearthstone.enums import GameTag


class Hero(Weapon):
    def __init__(self):
        super().__init__()

    @property
    def hero_attack(self) -> int:
        return self.hero_status.get(GameTag.ATK, 0)

    @property
    def hero_power(self) -> str:
        status = self.hero_status
        dbf_id = status.get(GameTag.HERO_POWER, 0)
        hero_power = self.get_card_name(dbf_id=dbf_id)
        return hero_power

    @property
    def hero_health(self) -> int:
        status = self.hero_status
        return status.get(GameTag.HEALTH) - status.get(GameTag.DAMAGE, 0)

    @property
    def hero_armor(self) -> int:
        status = self.hero_status
        return status.get(GameTag.ARMOR, 0)

