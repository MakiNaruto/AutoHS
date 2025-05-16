from typing import Optional
from gamestate.GameStateUpdater import GameStateUpdater
from gamestate.game.Hand import Hand
from gamestate.game.Minion import Minion
from gamestate.game.Player import Player
from hearthstone.entities import Game, Card
from hearthstone.enums import GameTag


class CommonStrategy(Player, Minion, Hand):
    def __init__(self, game_status: GameStateUpdater):
        super().__init__()
        self.my_turn = None
        self.play_state = None
        self.oppo_player_id = None
        self.my_player_id = None
        self.game = None
        self.game_status = game_status

    def execute(self):
        self.update_state()
        # TODO
        #  1. 根据场面信息进行计算, 根据信息决定操作模式.
        #  2. 调用策略, 计算攻击目标和攻击顺序.
        #  3. 调用方式?
        #     3.1 一次性调用: 直接返回所有操作流
        #     3.2 循环调用: 每一次操作都需要先调用一次策略
        print("执行策略...")
        # Controller 执行策略

        return

    def update_state(self):
        self.game: Optional[Game] = self.game_status.game
        self.my_player_id: int = self.game_status.my_player_id
        self.oppo_player_id: int = self.game_status.oppo_player_id
        self.play_state = self.game_status.play_state
        self.my_turn = self.game_status.my_turn

    @property
    def will_die_next_turn(self):
        if self.mine_has_taunt:
            return False

        if self.my_health <= self.oppo_total_attack:
            return True

        return False

    @property
    def mine_has_taunt(self):
        for my_minion in self.my_play_minions:
            check_res = self.check_minion_attributes(my_minion, owned_attributes=[GameTag.TAUNT], forbidden_attributes=[GameTag.STEALTH])
            if check_res:
                return True

        return False

    @property
    def oppo_has_taunt(self):
        for oppo_minion in self.oppo_play_minions:
            check_res = self.check_minion_attributes(oppo_minion, owned_attributes=[GameTag.TAUNT], forbidden_attributes=[GameTag.STEALTH, GameTag.UNTOUCHABLE])
            if check_res:
                return True

        return False

    @property
    def my_total_attack(self):
        count = 0
        for my_minion in self.my_play_minions:
            minion_tags = my_minion.tags
            if self.can_beat_face(my_minion):
                count += minion_tags.get(GameTag.ATK, 0)

        if self.my_hero_attack:
            count += self.my_hero_attack

        return count

    @property
    def oppo_total_attack(self):
        count = 0
        for oppo_minion in self.oppo_play_minions:
            minion_tags = oppo_minion.tags
            count += minion_tags.get(GameTag.ATK, 0)

        if self.oppo_hero_attack:
            count += self.oppo_hero_attack

        return count

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

    # TODO 下面的内容待完善
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

        if self.detail_card is not None:
            h_val += self.detail_card.live_value

        return h_val

    @property
    def detail_card(self) -> "Card":
        if self.is_coin:
            return ID2CARD_DICT["COIN"]
        else:
            return ID2CARD_DICT.get(self.card_id, None)

    # 用卡费体系算启发值
    @property
    def oppo_heuristic_value(self):
        total_h_val = 0
        if self.oppo_hero:
            total_h_val += self.player_heuristic_val(self.oppo_health)
        if self.oppo_weapon:
            total_h_val += self.oppo_weapon.heuristic_val
        for minion in self.oppo_minions:
            total_h_val += minion.heuristic_val
        return total_h_val

    @property
    def my_heuristic_value(self):
        total_h_val = 0
        if self.my_hero:
            total_h_val = self.player_heuristic_val(self.my_health)
        if self.my_weapon:
            total_h_val += self.my_weapon.heuristic_val
        for minion in self.my_minions:
            total_h_val += minion.heuristic_val
        return total_h_val

    @property
    def heuristic_value(self):
        return round(self.my_heuristic_value - self.oppo_heuristic_value, 3)

    @property
    def min_cost(self):
        minium = 100
        for hand_card in self.my_hand_cards:
            minium = min(minium, hand_card.current_cost)
        return minium

    @property
    def my_total_spell_power(self):
        return sum([minion.spell_power for minion in self.my_minions])

    @property
    def my_detail_hero_power(self):
        return self.my_hero_power.detail_hero_power
