from hearthstone.enums import CardType
from strategy.CommonStrategy import CommonStrategy
from gamestate.GameStateUpdater import GameStateUpdater


class ShadowFormStrategy(CommonStrategy):
    def __init__(self, game_status: GameStateUpdater):
        super().__init__(game_status)
        
    @property
    def will_die_next_turn(self):
        if self.mine_has_taunt:
            return False

        if self.my_player.hero_health <= self.oppo_total_attack + self.num_voidtouched_attendant_on_board * self.oppo_player.minion_num:
            return True

        return False
    
    @property
    def num_voidtouched_attendant_on_board(self):
        """ 场上有多少个虚触侍从，敌我双方都会生效，所以都算进去 """
        count = 0

        for minion in self.my_player.play_minions + self.oppo_player.play_minions:
            if minion.card_id == "SW_446":
                count += 1

        return count

    @property
    def num_mindbreaker_on_board(self):
        count = 0
        for minion in self.my_player.play_minions + self.oppo_player.play_minions:
            if minion.card_id == "CORE_ICC_902" or minion.card_id == "ICC_902":
                count += 1

        return count
    
    @property
    def airborne_gangsters_in_hand(self):
        """ 手牌里有几个空降歹徒，有的话就应该丢海盗 """
        count = 0
        for hand_card in self.my_player.hand_cards:
            if hand_card.card_id == "DRG_056":
                count += 1

        return count

    @property
    # 给亡者复生用的
    def num_minions_in_my_graveyard(self):
        count = 0
        for entity in self.my_player.graveyard_cards:
            if entity.type == CardType.MINION:
                count += 1

        return count
