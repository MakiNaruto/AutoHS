
from gamestate.game.Base import Base
from hearthstone.entities import Game
from hearthstone.enums import GameTag


class Weapon(Base):
    def __init__(self):
        super().__init__()
        self.game: Game
        self.my_player_id : int
        self.oppo_player_id : int

    @property
    def my_weapon(self):
        weapon_dbfid = self.my_hero_status.get(GameTag.WEAPON)
        # TODO
    
    @property
    def oppo_weapon(self):
        weapon_dbfid = self.oppo_hero_status.get(GameTag.WEAPON)
        # TODO
