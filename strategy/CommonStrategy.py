from typing import Optional
from hearthstone.enums import GameTag
from hearthstone.entities import Game
from strategy.Heuristic import Heuristic
from gamestate.GameStateUpdater import GameStateUpdater


class CommonStrategy(Heuristic):
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

    def is_card_in_hand(self, card_id: str = None):
        return any([card.card_id == card_id for card in self.my_hand_cards])

    @property
    def should_give_up(self):
        # 为时尚早
        threshold = 7

        if self.my_total_resources <= 6:
            return False

        score = 0
        if self.my_health >= 30:
            score += 4
        if self.oppo_health >= 25:
            score += 2
        elif self.oppo_health >= 15:
            score += 1

        if self.my_hand_card_num <= 1:
            score += 2

        if self.my_minion_num <= 1:
            score += 2

        if self.oppo_hand_card_num >= 4:
            score += 1

        if self.oppo_minion_num >= 4:
            score += 2

        if self.oppo_has_taunt:
            score += 1

        if score >= threshold:
            return True
        return False

    @property
    def will_die_next_turn(self):
        if self.mine_has_taunt:
            return False

        if self.my_health <= self.oppo_total_attack:
            return True

        return False

    @property
    def min_cost(self):
        minium = 100
        for hand_card in self.my_hand_cards:
            minium = min(minium, self.get_card_cost(hand_card))
        return minium

    @property
    def my_total_spell_power(self):
        return sum([self.get_minion_spell_power(minion) for minion in self.my_play_minions])

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
