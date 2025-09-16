from tkinter import ttk

from game.base import GameObject
from game.displays.base import Display, DisplayModel, DisplayView


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
        GameObject.singletons["production_display"] = self

    def _unregister(self) -> None:
        del GameObject.singletons["production_display"]
