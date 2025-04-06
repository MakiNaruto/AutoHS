from json_op import *
from abc import abstractmethod
from card.id2card import ID2CARD_DICT
from constants.state_and_key import *
from constants.number import *
from autohs_logger import *
from log_state import LogState, CardEntity
import copy


class StrategyEntity:
    def __init__(self, card_id, zone, zone_pos,
                 current_cost, overload, is_mine, powered_up):
        self.card_id = card_id
        self.zone = zone
        self.zone_pos = zone_pos
        self.current_cost = current_cost
        self.overload = overload
        self.is_mine = is_mine

        # 有特效的手牌（比如姐夫），在他的特效可以触发时会亮起黄框，
        # powered_up属性表示的就是黄框是否亮起
        self.powered_up = powered_up

    @property
    def name(self):
        return query_json_get_name(self.card_id)

    @property
    def races(self):
        return query_json_get_races(self.card_id)

    @property
    def is_pirate(self):
        return "PIRATE" in self.races or "ALL" in self.races

    @property
    def is_shadow_spell(self):
        return query_json_get_spell_school(self.card_id) == "SHADOW"

    @property
    def heuristic_val(self):
        return 0

    @property
    @abstractmethod
    def cardtype(self):
        pass

    @property
    def is_coin(self):
        return self.name == "幸运币"

    @property
    def detail_card(self):
        if self.is_coin:
            return ID2CARD_DICT["COIN"]
        else:
            return ID2CARD_DICT.get(self.card_id, None)

class StrategyMinion(StrategyEntity):
    def __init__(self, card_id, zone, zone_pos,
                 current_cost, overload, is_mine, powered_up,
                 attack, max_health, damage=0,
                 taunt=0, divine_shield=0, stealth=0,
                 windfury=0, poisonous=0, life_steal=0,
                 spell_power=0, freeze=0, battlecry=0,
                 not_targeted_by_spell=0, not_targeted_by_power=0,
                 charge=0, rush=0,
                 attackable_by_rush=0, frozen=0,
                 dormant=0, untouchable=0, immune=0,
                 cant_attack=0, exhausted=1, num_turns_in_play=1
        ):
        super().__init__(card_id, zone, zone_pos,
                         current_cost, overload, is_mine, powered_up)
        self.attack = attack
        self.max_health = max_health
        self.damage = damage
        self.taunt = taunt
        self.divine_shield = divine_shield
        self.stealth = stealth
        self.windfury = windfury
        self.poisonous = poisonous
        self.life_steal = life_steal
        self.spell_power = spell_power
        self.freeze = freeze
        self.battlecry = battlecry
        self.not_targeted_by_spell = not_targeted_by_spell
        self.not_targeted_by_power = not_targeted_by_power
        self.charge = charge
        self.rush = rush
        # 当一个随从具有毛刺绿边（就是突袭随从刚出来时的绿边）的时候就会有这个属性
        self.attackable_by_rush = attackable_by_rush
        self.frozen = frozen
        self.dormant = dormant
        # 休眠的随从会在休眠时具有UNTOUCHABLE属性，星舰在未发射时也具有这个属性
        self.untouchable = untouchable
        self.immune = immune
        self.cant_attack = cant_attack
        self.num_turns_in_play = num_turns_in_play
        # exhausted == 1: 随从没有绿边, 不能动
        # 普通随从一入场便具有 exhausted == 1,
        # 但是突袭随从和冲锋随从一开始不具有这个标签,
        # 所以还要另作判断(尤其是突袭随从一开始不能打脸)
        self.exhausted = exhausted

        # 对于突袭随从, 第一回合应不能打脸, 而能攻击随从由
        # attackable_by_rush体现
        if self.rush and not self.charge \
                and self.num_turns_in_play < 2:
            self.exhausted = 1

    def __str__(self):
        temp = f"[{self.zone_pos}] {self.name} " \
               f"{self.attack}-{self.health}({self.max_health})"

        if self.can_beat_face:
            temp += " [能打脸]"
        elif self.can_attack_minion:
            temp += " [能打怪]"
        else:
            temp += " [不能动]"

        if self.dormant:
            temp += " 休眠"
        if self.immune:
            temp += " 免疫"
        if self.frozen:
            temp += " 被冻结"
        if self.taunt:
            temp += " 嘲讽"
        if self.divine_shield:
            temp += " 圣盾"
        if self.stealth:
            temp += " 潜行"
        if self.charge:
            temp += " 冲锋"
        if self.rush:
            temp += " 突袭"
        if self.windfury:
            temp += " 风怒"
        if self.poisonous:
            temp += " 剧毒"
        if self.life_steal:
            temp += " 吸血"
        if self.freeze:
            temp += " 冻结敌人"
        if self.not_targeted_by_spell and self.not_targeted_by_power:
            temp += " 魔免"
        if self.spell_power:
            temp += f" 法术伤害+{self.spell_power}"
        if self.cant_attack:
            temp += " 不能攻击"
        if self.powered_up:
            temp += " 特效激活"
        if self.detail_card is not None and self.detail_card.live_value > 0:
            temp += " 光环价值:" + str(self.detail_card.live_value)

        temp += f" h_val:{self.heuristic_val}"

        return temp

    @property
    def cardtype(self):
        return CARD_MINION

    @property
    def health(self):
        return self.max_health - self.damage

    @property
    def can_beat_face(self):
        return self.attack > 0 \
               and not self.dormant \
               and not self.frozen \
               and not self.cant_attack \
               and self.exhausted == 0

    @property
    def can_attack_minion(self):
        return self.attack > 0 \
               and not self.dormant \
               and not self.frozen\
               and not self.cant_attack \
               and (self.exhausted == 0
                    or self.attackable_by_rush)

    @property
    def can_be_pointed_by_spell(self):
        return not self.stealth \
               and not self.untouchable \
               and not self.not_targeted_by_spell \
               and not self.dormant \
               and not self.immune

    @property
    def can_be_pointed_by_hero_power(self):
        return not self.stealth \
               and not self.untouchable \
               and not self.not_targeted_by_power \
               and not self.dormant \
               and not self.immune

    @property
    def can_be_pointed_by_minion(self):
        return not self.stealth \
               and not self.untouchable \
               and not self.dormant \
               and not self.immune

    @property
    def can_be_attacked(self):
        return not self.stealth \
               and not self.untouchable \
               and not self.immune \
               and not self.dormant

    # 简单介绍一下卡费理论
    # 一点法力水晶 = 抽0.5张卡 = 造成1点伤害 = 2点攻击力 = 2点生命值 = 回复2点血
    # 一张卡自带一点水晶
    # 可以类比一下月火术, 奥术射击, 小精灵, 战斗法师等卡
    @property
    def heuristic_val(self):
        if self.health <= 0:
            return 0

        h_val = self.attack + self.health
        if self.divine_shield:
            h_val += self.attack
        if self.stealth:
            h_val += self.attack / 2
        if self.taunt:  # 嘲讽不值钱
            h_val += self.health / 4
        if self.poisonous:
            h_val += self.health
            if self.divine_shield:
                h_val += 3
        if self.life_steal:
            h_val += self.attack / 2 + self.health / 4
        h_val += self.poisonous

        if self.zone == "HAND":
            if self.rush or self.attack:
                h_val += self.attack / 4

        if self.detail_card is not None:
            h_val += self.detail_card.live_value

        return h_val

    def get_damaged(self, damage):
        if damage <= 0:
            return False
        if self.divine_shield:
            self.divine_shield = False
        else:
            self.damage += damage
            if self.health <= 0:
                return True
        return False

    def get_heal(self, heal):
        if heal > self.damage:
            self.damage = 0
        else:
            self.damage -= heal

    def delta_h_after_damage(self, damage):
        temp_minion = copy.copy(self)
        temp_minion.get_damaged(damage)
        delta = self.heuristic_val - temp_minion.heuristic_val

        if self.is_mine:
            delta *= MY_MINION_DELTA_H_FACTOR
        else:
            delta *= OPPO_MINION_DELTA_H_FACTOR

        return delta

    def delta_h_after_heal(self, heal):
        temp_minion = copy.copy(self)
        temp_minion.get_heal(heal)

        delta = temp_minion.heuristic_val - self.heuristic_val

        if self.is_mine:
            delta *= MY_MINION_DELTA_H_FACTOR
        else:
            delta *= OPPO_MINION_DELTA_H_FACTOR

        return delta


class StrategyWeapon(StrategyEntity):
    def __init__(self, card_id, zone, zone_pos,
                 current_cost, overload, is_mine, powered_up,
                 attack, durability, damage=0, windfury=0):
        super().__init__(card_id, zone, zone_pos,
                         current_cost, overload, is_mine, powered_up)
        self.attack = attack
        self.durability = durability
        self.damage = damage
        self.windfury = windfury

    def __str__(self):
        temp = f"{self.name} {self.attack}-{self.health}" \
               f"({self.durability}) h_val:{self.heuristic_val}"
        if self.windfury:
            temp += " 风怒"
        return temp

    @property
    def cardtype(self):
        return CARD_WEAPON

    @property
    def health(self):
        return self.durability - self.damage

    @property
    def heuristic_val(self):
        return self.attack * self.health


class StrategyHero(StrategyEntity):
    def __init__(self, card_id, zone, zone_pos,
                 current_cost, overload, is_mine, powered_up,
                 max_health, damage=0,
                 stealth=0, immune=0,
                 not_targeted_by_spell=0, not_targeted_by_power=0,
                 armor=0, attack=0, exhausted=1):
        super().__init__(card_id, zone, zone_pos,
                         current_cost, overload, is_mine, powered_up)
        self.max_health = max_health
        self.damage = damage
        self.stealth = stealth
        self.immune = immune
        self.not_targeted_by_spell = not_targeted_by_spell
        self.not_targeted_by_power = not_targeted_by_power
        self.armor = armor
        self.attack = attack
        self.exhausted = exhausted

    def __str__(self):
        temp = f"{self.name} {self.attack}-{self.health}" \
               f"({self.max_health - self.damage}+{self.armor})"

        if self.can_attack:
            temp += " [能动]"
        else:
            temp += " [不能动]"

        if self.stealth:
            temp += " 潜行"
        if self.immune:
            temp += " 免疫"

        temp += f" h_val:{self.heuristic_val}"
        return temp

    @property
    def cardtype(self):
        return CARD_HERO

    @property
    def health(self):
        return self.max_health + self.armor - self.damage

    @property
    def heuristic_val(self):
        if self.health <= 0:
            return -10000
        if self.health <= 5:
            return self.health
        if self.health <= 10:
            return 5 + (self.health - 5) * 0.6
        if self.health <= 20:
            return 8 + (self.health - 10) * 0.4
        else:
            return 12 + (self.health - 20) * 0.3

    @property
    def can_attack(self):
        return self.attack > 0 and not self.exhausted

    @property
    def can_be_pointed_by_spell(self):
        return not self.stealth \
               and not self.not_targeted_by_spell \
               and not self.immune

    @property
    def can_be_pointed_by_hero_power(self):
        return not self.stealth \
               and not self.not_targeted_by_power \
               and not self.immune

    @property
    def can_be_pointed_by_minion(self):
        return not self.stealth \
               and not self.immune

    @property
    def can_be_attacked(self):
        return not self.stealth and not self.immune

    def get_damaged(self, damage):
        if self.immune:
            return

        if damage <= self.armor:
            self.armor -= damage
        else:
            last_damage = damage - self.armor
            self.armor = 0
            self.damage += last_damage

    def get_heal(self, heal):
        if heal >= self.damage:
            self.damage = 0
        else:
            self.damage -= heal

    def delta_h_after_damage(self, damage):
        temp_hero = copy.copy(self)
        temp_hero.get_damaged(damage)
        return (self.heuristic_val - temp_hero.heuristic_val) * (1 if self.is_mine else OPPO_HERO_DELTA_H_FACTOR)

    def delta_h_after_heal(self, heal):
        temp_hero = copy.copy(self)
        temp_hero.get_heal(heal)
        return (temp_hero.heuristic_val - self.heuristic_val) * (1 if self.is_mine else OPPO_HERO_DELTA_H_FACTOR)


class StrategySpell(StrategyEntity):
    @property
    def cardtype(self):
        return CARD_SPELL


# TODO: 目前脚本不支持使用地标
class StrategyLocation(StrategyEntity):
    def __init__(self, card_id, zone, zone_pos,
                 current_cost, overload, is_mine, powered_up,
                 health):
        super().__init__(card_id, zone, zone_pos,
                         current_cost, overload, is_mine, powered_up)
        self.health = health
        self.taunt = False
        self.stealth = False
        self.attack = 0

    def __str__(self):
        return f"[{self.zone_pos}] {self.name} 耐久:{self.health}"

    @property
    def cardtype(self):
        return CARD_LOCATION

    @property
    def can_beat_face(self):
        return False

    @property
    def can_attack_minion(self):
        return False

    @property
    def can_be_pointed_by_spell(self):
        return False

    @property
    def can_be_pointed_by_hero_power(self):
        return False

    @property
    def can_be_pointed_by_minion(self):
        return False

    @property
    def can_be_attacked(self):
        return False

    @property
    def heuristic_val(self):
        return 0

    def get_damaged(self, damage):
        return False

    def get_heal(self, heal):
        return

    # 这样应该就不会被攻击或是指向了
    def delta_h_after_damage(self, damage):
        return -1

    def delta_h_after_heal(self, heal):
        return -1


class StrategyHeroPower(StrategyEntity):
    def __init__(self, card_id, zone, zone_pos,
                 current_cost, overload, is_mine, powered_up,
                 exhausted):
        super().__init__(card_id, zone, zone_pos,
                         current_cost, overload, is_mine, powered_up)
        self.exhausted = exhausted

    @property
    def cardtype(self):
        return CARD_HERO_POWER

    @property
    def detail_hero_power(self):
        if self.name == "次级治疗术":
            return ID2CARD_DICT["LESSER_HEAL"]
        elif self.name == "图腾召唤":
            return ID2CARD_DICT["TOTEMIC_CALL"]
        elif self.name == "稳固射击":
            return ID2CARD_DICT["BALLISTA_SHOT"]
        elif self.name == "心灵尖刺":
            return ID2CARD_DICT["MIND_SPIKE"]
        else:
            logger.error("发现我方英雄具有尚未支持的英雄技能：" + self.name)
        return None

def generate_strategy_entity(input_card_entity: CardEntity, log_state : LogState):
    if input_card_entity.cardtype == "MINION":
        return StrategyMinion(
            card_id=input_card_entity.card_id,
            zone=input_card_entity.query_tag("ZONE"),
            zone_pos=int(input_card_entity.query_tag("ZONE_POSITION")),
            current_cost=int(input_card_entity.query_tag("TAG_LAST_KNOWN_COST_IN_HAND")),
            overload=int(input_card_entity.query_tag("OVERLOAD")),
            is_mine=log_state.is_my_entity(input_card_entity),
            powered_up=int(input_card_entity.query_tag("POWERED_UP")),
            attack=int(input_card_entity.query_tag("ATK")),
            max_health=int(input_card_entity.query_tag("HEALTH")),
            damage=int(input_card_entity.query_tag("DAMAGE")),
            taunt=int(input_card_entity.query_tag("TAUNT")),
            divine_shield=int(input_card_entity.query_tag("DIVINE_SHIELD")),
            stealth=int(input_card_entity.query_tag("STEALTH")),
            windfury=int(input_card_entity.query_tag("WINDFURY")),
            poisonous=int(input_card_entity.query_tag("POISONOUS")),
            freeze=int(input_card_entity.query_tag("FREEZE")),
            battlecry=int(input_card_entity.query_tag("BATTLECRY")),
            spell_power=int(input_card_entity.query_tag("SPELLPOWER")),
            not_targeted_by_spell=int(input_card_entity.query_tag("CANT_BE_TARGETED_BY_SPELLS")),
            not_targeted_by_power=int(input_card_entity.query_tag("CANT_BE_TARGETED_BY_HERO_POWERS")),
            charge=int(input_card_entity.query_tag("CHARGE")),
            rush=int(input_card_entity.query_tag("RUSH")),
            attackable_by_rush=int(input_card_entity.query_tag("ATTACKABLE_BY_RUSH")),
            frozen=int(input_card_entity.query_tag("FROZEN")),
            dormant=int(input_card_entity.query_tag("DORMANT")),
            untouchable=int(input_card_entity.query_tag("UNTOUCHABLE")),
            immune=int(input_card_entity.query_tag("IMMUNE")),
            # -1代表标签缺失, 有两种情况会产生-1: 断线重连; 卡刚从手牌中被打出来
            exhausted=int(input_card_entity.query_tag("EXHAUSTED")),
            cant_attack=int(input_card_entity.query_tag("CANT_ATTACK")),
            num_turns_in_play=int(input_card_entity.query_tag("NUM_TURNS_IN_PLAY")),
        )
    elif input_card_entity.cardtype == "SPELL":
        return StrategySpell(
            card_id=input_card_entity.card_id,
            zone=input_card_entity.query_tag("ZONE"),
            zone_pos=int(input_card_entity.query_tag("ZONE_POSITION")),
            current_cost=int(input_card_entity.query_tag("TAG_LAST_KNOWN_COST_IN_HAND")),
            overload=int(input_card_entity.query_tag("OVERLOAD")),
            is_mine=log_state.is_my_entity(input_card_entity),
            powered_up=int(input_card_entity.query_tag("POWERED_UP")),
        )
    elif input_card_entity.cardtype == "WEAPON":
        return StrategyWeapon(
            card_id=input_card_entity.card_id,
            zone=input_card_entity.query_tag("ZONE"),
            zone_pos=int(input_card_entity.query_tag("ZONE_POSITION")),
            current_cost=int(input_card_entity.query_tag("TAG_LAST_KNOWN_COST_IN_HAND")),
            overload=int(input_card_entity.query_tag("OVERLOAD")),
            is_mine=log_state.is_my_entity(input_card_entity),
            powered_up=int(input_card_entity.query_tag("POWERED_UP")),
            attack=int(input_card_entity.query_tag("ATK")),
            durability=int(input_card_entity.query_tag("DURABILITY")),
            damage=int(input_card_entity.query_tag("DAMAGE")),
            windfury=int(input_card_entity.query_tag("WINDFURY")),
        )
    elif input_card_entity.cardtype == "HERO":
        return StrategyHero(
            card_id=input_card_entity.card_id,
            zone=input_card_entity.query_tag("ZONE"),
            zone_pos=int(input_card_entity.query_tag("ZONE_POSITION")),
            current_cost=int(input_card_entity.query_tag("TAG_LAST_KNOWN_COST_IN_HAND")),
            overload=int(input_card_entity.query_tag("OVERLOAD")),
            is_mine=log_state.is_my_entity(input_card_entity),
            powered_up=int(input_card_entity.query_tag("POWERED_UP")),
            max_health=int(input_card_entity.query_tag("HEALTH")),
            damage=int(input_card_entity.query_tag("DAMAGE")),
            stealth=int(input_card_entity.query_tag("STEALTH")),
            immune=int(input_card_entity.query_tag("IMMUNE")),
            not_targeted_by_spell=int(input_card_entity.query_tag("CANT_BE_TARGETED_BY_SPELLS")),
            not_targeted_by_power=int(input_card_entity.query_tag("CANT_BE_TARGETED_BY_HERO_POWERS")),
            armor=int(input_card_entity.query_tag("ARMOR")),
            attack=int(input_card_entity.query_tag("ATK")),
            exhausted=int(input_card_entity.query_tag("EXHAUSTED")),
        )
    elif input_card_entity.cardtype == "HERO_POWER":
        return StrategyHeroPower(
            card_id=input_card_entity.card_id,
            zone=input_card_entity.query_tag("ZONE"),
            zone_pos=int(input_card_entity.query_tag("ZONE_POSITION")),
            current_cost=int(input_card_entity.query_tag("COST")),
            overload=int(input_card_entity.query_tag("OVERLOAD")),
            is_mine=log_state.is_my_entity(input_card_entity),
            powered_up=int(input_card_entity.query_tag("POWERED_UP")),
            exhausted=int(input_card_entity.query_tag("EXHAUSTED", default_val="0")),
        )
    elif input_card_entity.cardtype == "LOCATION":
        return StrategyLocation(
            card_id=input_card_entity.card_id,
            zone=input_card_entity.query_tag("ZONE"),
            zone_pos=int(input_card_entity.query_tag("ZONE_POSITION")),
            current_cost=int(input_card_entity.query_tag("COST")),
            overload=int(input_card_entity.query_tag("OVERLOAD")),
            is_mine=log_state.is_my_entity(input_card_entity),
            powered_up=int(input_card_entity.query_tag("POWERED_UP")),
            health=int(input_card_entity.query_tag("HEALTH")),
        )
    else:
        logger.warning(f"未知卡牌类型{input_card_entity.cardtype}")
        return None
