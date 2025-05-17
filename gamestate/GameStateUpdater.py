
import re
from typing import Optional
from collections import deque
from gamestate.game.Player import Player
from hslog.export import EntityTreeExporter
from hslog.parser import LogParser
from hsreplay.elements import GameNode
from hsreplay.dumper import add_packets_recursive
from hsreplay.document import HSReplayDocument
from hearthstone.entities import Game, Entity
from hearthstone.enums import BlockType, GameTag, PlayState, State, Step
from gamestate.LogWatcher import HearthStoneLogWatcher


class GameStateUpdater(HearthStoneLogWatcher, Player):
    def __init__(self):
        super().__init__()
        self.parser: LogParser = LogParser()
        self.updater: EntityTreeExporter = EntityTreeExporter(self.parser._parsing_state.packet_tree)
        self.game: Optional[Game] = None
        # 用于标识一局游戏的状态,  PlayState.Playing游戏中, PlayState.INVALID 等待中.
        self.play_state = PlayState.INVALID             
        self.my_turn = False

    def init_player(self, line):
        pattern = r"SHOW_ENTITY - Updating Entity=.*?id=(\w+)"
        match = re.search(pattern, line)
        if not match:
            return

        entity_id = match.group(1)

        card: Entity = self.game.find_entity_by_id(entity_id)
        if hasattr(card, 'card_id') and not card.card_id:
            return

        self.my_player_id = card.controller.player_id
        self.oppo_player_id = 3 - self.my_player_id

        # 设置玩家姓名
        players_info = self.parser.player_manager._players_by_name
        for player_name, info in players_info.items():
            player_id = info.player_id
            player = self.game.get_player(player_id)
            player.name = player_name

    def reset_status(self):
        self.parser = LogParser()
        self.updater = EntityTreeExporter(self.parser._parsing_state.packet_tree)
        self.game = None
        self.my_player_id = None
        self.oppo_player_id = None

    def flush_status(self, bucket_node):
        self.updater.export_packet(bucket_node)
        self.updater.flush()
        self.game = self.updater.game
        if self.game.current_player:
            self.my_turn = self.game.current_player.player_id == self.my_player_id

        # # DEBUG
        game_element = GameNode(bucket_node.ts)
        add_packets_recursive([bucket_node], game_element)
        xml_block = game_element.nodes[0]
        self.update(xml_block)

    def log_praser(self, line):
        # 若没添加新状态桶, 则说明之前的状态桶没有处理完
        packet_tree = self.parser._parsing_state.packet_tree
        if not packet_tree or not packet_tree.packets:
            if self.play_state == PlayState.INVALID:
                if re.search('CREATE_GAME', line):
                    self.parser.read_line(line)
                    self.play_state = PlayState.PLAYING
                return
            else:
                self.parser.read_line(line)

        if not self.my_player_id:
            self.init_player(line)

        packets = packet_tree.packets
        last_block_index = len(packets)
        self.parser.read_line(line)
        current_block_index = len(packets)

        # 等待一个完整的block块, 最新的状态块的内容可能不完整
        if current_block_index == last_block_index or current_block_index == 0:
            return

        # 重置游戏状态器
        if hasattr(packets[-1], 'value'):
            if self.play_state == PlayState.PLAYING and packets[-1].value == Step.FINAL_GAMEOVER:
                self.play_state = PlayState.INVALID
                self.flush_status(packets[-1])
                self.reset_status()
                return

        self.flush_status(packets[-2])

    def xml_parser(self, file_path):
        doc = HSReplayDocument.from_xml_file(file_path)
        xml_tree = doc.to_packet_tree()
        packet_tree = xml_tree[0]
        self.game = packet_tree.export().game
        packets = packet_tree.packets
        for packet in packets:
            self.flush_status(packet)

    def update(self, xml_block):
        # 深度优先遍历
        stack = deque([xml_block])
        while stack:
            node = stack.pop()
            if node.tagname == "Block":
                # TODO 完善
                if node.type == BlockType.ATTACK:
                    from hearthstone.enums import Zone
                    # print(self.cards_pool_filter(self.my_entites, Zone.HAND))
                    print(self.my_health)
                    import time
                    # time.sleep(10)
                    # for minion in self.oppo_board_minions:
                    ...

                elif node.type == BlockType.POWER:
                    ...
                elif node.type == BlockType.TRIGGER:
                    ...
                elif node.type == BlockType.DEATHS:
                    ...
                elif node.type == BlockType.PLAY:
                    ...
                elif node.type == BlockType.FATIGUE:
                    ...

            if node.tagname == "TagChange":
                if node.tag == State.COMPLETE:
                    ...
                if node.tag == PlayState.PLAYING:
                    ...
                if node.tag == GameTag.NUM_TURNS_IN_HAND:
                    ...
            # 深度优先访问节点, 返回最后一个添加的节点.
            if len(node.nodes) > 0:
                stack.extendleft(node.nodes)
