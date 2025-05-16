import time
import threading
from hearthstone.enums import PlayState
from gamestate.game.Hand import Hand
from gamestate.game.Minion import Minion
from gamestate.game.Player import Player
from strategy.StrategyManager import StrategyManager
from gamestate.GameStateUpdater import GameStateUpdater


class HearthStoneBuddy(GameStateUpdater, Player, Minion, Hand):
    def __init__(self):
        super().__init__()

    @property
    def game_status(self):
        ...


class HearthStoneBuddyController:
    def __init__(self, game_status: GameStateUpdater):
        self.game_status = game_status
        self.strategy = StrategyManager(game_status).create_strategy('aggressive')

    def turn_controller(self):
        while True:
            if self.game_status.play_state == PlayState.PLAYING:
                if self.game_status.my_turn:
                    self.strategy.execute()
                    print("This Is My turn")
                    time.sleep(1)
                    ...
                else:
                    print("Watting")
                    time.sleep(1)
            else:
                if "change":
                    self.strategy = StrategyManager(self.game_status).create_strategy('aggressive')
                print("Watting Game Start")
                time.sleep(1)


if __name__ == "__main__":
    # export PYTHONPATH=$(pwd)
    log_file_path = 'test-0512.log'
    hs_buddy = HearthStoneBuddy()
    
    # watcher.log_listener(log_file_path)

    # watcher.xml_parser('test-0512.xml')

    controller = HearthStoneBuddyController(hs_buddy)
    # 正式运行
    threading.Thread(target=hs_buddy.log_listener, args=(log_file_path,), daemon=True).start()
    threading.Thread(target=controller.turn_controller, daemon=True).start()

    while True:
        time.sleep(1)  # 主线程保持存活
