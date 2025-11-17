from collections.abc import Callable

from game.displays.base import Display, DisplayModel, DisplayView
from game.states import GameState


class CoinDisplayModel(DisplayModel):

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.coin = 10

    def get_data(self) -> dict:
        data = {
            **super().get_data(),
            "coin": self.coin,
        }
        return data


class CoinDisplayView(DisplayView):

    def refresh(self, data: dict, event_handlers: dict[str, Callable]) -> None:
        self._widgets["main"].configure(text=f"Coin: {data["coin"]:3d}")


class CoinDisplay(Display):

    def _register(self) -> None:
        GameState.displays["coin"] = self

    def _unregister(self) -> None:
        GameState.displays["coin"] = None
