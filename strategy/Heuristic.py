from hearthstone.enums import GameTag
from hearthstone.entities import Card
from gamestate.game.Hand import Hand
from gamestate.game.Minion import Minion
from gamestate.game.Player import Player


class Heuristic(Player, Minion, Hand):
    def __init__(self):
        super().__init__()

    def player_heuristic_val(self, health):
        if health <= 0:
            return -10000
        if health <= 5:
            return health
        if health <= 10:
            return 5 + (health - 5) * 0.6
        if health <= 20:
            return 8 + (health - 10) * 0.4
        else:
            return 12 + (health - 20) * 0.3

    def minion_heuristic_val(self, minion: Card):
        zone = minion.zone
        minion_status = self.get_minion_status(minion)
        health = minion_status.get(GameTag.HEALTH, 0)
        attack = minion_status.get(GameTag.ATK)
        divine_shield = minion_status.get(GameTag.DIVINE_SHIELD)
        stealth = minion_status.get(GameTag.STEALTH)
        taunt = minion_status.get(GameTag.TAUNT)
        poisonous = minion_status.get(GameTag.POISONOUS)
        life_steal = minion_status.get(GameTag.LIFESTEAL)
        rush = minion_status.get(GameTag.RUSH)

        if health <= 0:
            return 0

        h_val = attack + health
        if divine_shield:
            h_val += attack
        if stealth:
            h_val += attack / 2
        if taunt:  # 嘲讽不值钱
            h_val += health / 4
        if poisonous:
            h_val += health
            if divine_shield:
                h_val += 3
        if life_steal:
            h_val += attack / 2 + health / 4
        h_val += poisonous

        if zone == "HAND":
            if rush or attack:
                h_val += attack / 4

        # TODO
        # 计算光环价值
        # if self.detail_card is not None:
        #     h_val += self.detail_card.live_value

        return h_val

    def weapon_heuristic_val(self, hero_attack, hero_health):
        return hero_attack * hero_health

    @property
    def my_weapon_heuristic_val(self):
        return self.weapon_heuristic_val(self.my_hero_attack, self.my_health)

    @property
    def oppo_weapon_heuristic_val(self):
        return self.weapon_heuristic_val(self.oppo_hero_attack, self.oppo_health)

    @property
    def my_heuristic_value(self):
        total_h_val = self.player_heuristic_val(self.my_health)
        if self.my_weapon:
            total_h_val += self.my_weapon_heuristic_val
        for minion in self.my_play_minions:
            total_h_val += self.minion_heuristic_val(minion)
        return total_h_val

    @property
    def oppo_heuristic_value(self):
        total_h_val = self.player_heuristic_val(self.oppo_health)
        if self.oppo_weapon:
            total_h_val += self.oppo_weapon_heuristic_val
        for minion in self.oppo_play_minions:
            total_h_val += self.minion_heuristic_val(minion)
        return total_h_val

    @property
    def heuristic_value(self):
        return round(self.my_heuristic_value - self.oppo_heuristic_value, 3)
