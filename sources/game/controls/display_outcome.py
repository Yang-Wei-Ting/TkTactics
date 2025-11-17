from collections.abc import Callable
from tkinter import ttk

from game.base import GameObject, GameObjectModel, GameObjectView
from game.configurations import Dimension
from game.states import GameState


class DisplayOutcomeControlModel(GameObjectModel):

    def __init__(self, text: str) -> None:
        x = Dimension.HORIZONTAL_FIELD_TILE_COUNT // 2
        y = Dimension.VERTICAL_TILE_COUNT // 2
        super().__init__(x, y)
        self.text = text

    def get_data(self) -> dict:
        data = {
            **super().get_data(),
            "text": self.text,
        }
        return data


class DisplayOutcomeControlView(GameObjectView):

    def _create_widgets(self) -> None:
        self._widgets["main"] = ttk.Button(
            self.canvas,
            cursor="hand2",
            style="OutcomeBanner.Black_CustomWood.TButton",
            takefocus=False,
        )

    def refresh(self, data: dict, event_handlers: dict[str, Callable]) -> None:
        self._widgets["main"].configure(
            command=event_handlers["click"],
            text=data["text"],
        )


class DisplayOutcomeControl(GameObject):

    def __init__(self, model: DisplayOutcomeControlModel, view: DisplayOutcomeControlView) -> None:
        if control := GameState.controls["display_outcome"]:
            control.handle_click_event()

        super().__init__(model, view)

    def _register(self) -> None:
        GameState.controls["display_outcome"] = self

    def _unregister(self) -> None:
        GameState.controls["display_outcome"] = None

    @property
    def event_handlers(self) -> dict[str, Callable]:
        return {"click": self.handle_click_event}

    def handle_click_event(self) -> None:
        self.destroy()
