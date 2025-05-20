from gamestate.game.Base import Base
from hearthstone.entities import Card
from hearthstone.enums import GameTag, Zone


class Weapon(Base):
    def __init__(self):
        super().__init__()

    @property
    def weapon(self):
        weapon = None
        weapon_dbfid = self.hero_status.get(GameTag.WEAPON)
        if weapon_dbfid:
            weapon = self.get_card_info(dbf_id=weapon_dbfid)
        return weapon

    @property
    def durability(self):
        weapon: Card = self.equiped_weapon
        if not weapon:
            return 0
        weapon_status = weapon.tags
        return weapon_status.get(GameTag.DURABILITY) - weapon_status.get(GameTag.DAMAGE, 0)

    @property
    def equiped_weapon(self) -> list[Card]:
        weapon = self.cards_pool_filter(self.entites, Zone.PLAY)
        return weapon[0] if weapon else None
