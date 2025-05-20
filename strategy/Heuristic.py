from hearthstone.enums import GameTag
from hearthstone.entities import Card


class WeaponHeuristic():
    def __init__(self, player=None):
        self.player = player

    @property
    def weapon_heuristic_val(self):
        return self.player.hero_attack * self.player.hero_health


class MinionHeuristic():
    def __init__(self, player=None):
        self.player = player

    def minion_heuristic_value(self, minion: Card):
        zone = minion.zone
        minion_status = self.player.get_minion_status(minion)
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

class HeroHeuristic():
    def __init__(self, player=None):
        self.player = player
    
    @property
    def hero_heuristic_value(self):
        if self.player.hero_health <= 0:
            return -10000
        if self.player.hero_health <= 5:
            return self.player.hero_health
        if self.player.hero_health <= 10:
            return 5 + (self.player.hero_health - 5) * 0.6
        if self.player.hero_health <= 20:
            return 8 + (self.player.hero_health - 10) * 0.4
        else:
            return 12 + (self.player.hero_health - 20) * 0.3


class Heuristic(WeaponHeuristic, HeroHeuristic, MinionHeuristic):
    def __init__(self, player):
        super().__init__(player)

    @property
    def heuristic_value(self):
        total_h_val = self.player_heuristic_value
        if self.player.weapon:
            total_h_val += self.weapon_heuristic_val
        for minion in self.player.play_minions:
            total_h_val += self.minion_heuristic_value(minion)
        return total_h_val
