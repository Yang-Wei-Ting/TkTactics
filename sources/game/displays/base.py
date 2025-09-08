from tkinter import ttk

from game.base import GameObject, GameObjectModel, GameObjectView


class DisplayModel(GameObjectModel):
    pass


class DisplayView(GameObjectView):

    def _create_widgets(self) -> None:
        self._widgets["main"] = ttk.Label(
            self.canvas,
            cursor="arrow",
            style="SmallPanelBox.Black_CustomWood.TButton",
        )


class Display(GameObject):
    pass
