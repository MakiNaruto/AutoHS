from gamestate.GameStateUpdater import GameStateUpdater
from gamestate.strategy.ShadowFormStrategy import ShadowFormStrategy


class StrategyManager:
    def __init__(self, game_status: GameStateUpdater) -> None:
        self.game_status = game_status

    def create_strategy(self, name):
        if name == "aggressive":
            return ShadowFormStrategy(self.game_status)
        elif name == "control":
            ...
        else:
            print(f"策略 '{name}' 不存在！")
            return None

