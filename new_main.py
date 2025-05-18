import time
import threading
from hearthstone.enums import PlayState
from strategy.StrategyManager import StrategyManager
from gamestate.GameStateUpdater import GameStateUpdater


class HearthStoneBuddy(GameStateUpdater):
    def __init__(self):
        super().__init__()

    @property
    def game_status(self):
        ...


class HearthStoneBuddyController:
    def __init__(self, game_status: GameStateUpdater):
        self.game_status = game_status
        self.strategyManager = StrategyManager(game_status)
        self.strategy = self.strategyManager.create_strategy('暗牧')

    def change_strategy(self, strategy_name):
        self.strategy = self.strategyManager.create_strategy(strategy_name)

    def game_strategy_check(self):
        """ 切换对战策略 """
        if self.strategyManager.current_strategy == '切换的策略名称':
            return

        self.change_strategy('其他策略')
        # 更换策略
        print("Watting Game Start")

    def game_interface_check(self):
        # TODO 判断界面状态
        # 准备进入到对战中
        ...

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
                self.game_strategy_check()
                self.game_interface_check()
                time.sleep(1)


if __name__ == "__main__":
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
