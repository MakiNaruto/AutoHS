from gamestate.GameStateUpdater import GameStateUpdater
from strategy.ShadowFormStrategy import ShadowFormStrategy


class StrategyManager:
    def __init__(self, game_status: GameStateUpdater) -> None:
        self.game_status = game_status
        self.current_strategy: str = None

    def create_strategy(self, name: str):
        self.current_strategy: str = name
        if name == "暗牧":
            return ShadowFormStrategy(self.game_status)
        elif name == "其他策略":
            ...
        else:
            print(f"策略 '{name}' 不存在！")
            return None

