from tkinter import ttk

from game.displays.base import Display, DisplayModel, DisplayView
from game.states import GameState


class ProductionDisplayModel(DisplayModel):
    pass


class ProductionDisplayView(DisplayView):

    def _create_widgets(self) -> None:
        self._widgets["main"] = ttk.Label(
            self.canvas,
            cursor="arrow",
            style="MiddlePanelBox.Black_CustomWood.TButton",
        )


class ProductionDisplay(Display):

    def _register(self) -> None:
        GameState.displays["production"] = self

    def _unregister(self) -> None:
        GameState.displays["production"] = None
