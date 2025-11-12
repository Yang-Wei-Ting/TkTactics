import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from game.base import GameObject, GameObjectModel, GameObjectView
from game.configurations import Dimension
from game.images import Image
from game.recruitments.base import SoldierRecruitment
from game.states import GameState
from game.utilities import get_pixels


class BuildingModel(GameObjectModel):

    defense = 0.4
    health = 400.0

    def get_data(self) -> dict:
        data = {
            "class": "building",
            "name": type(self).__name__.removesuffix("Model"),
            **super().get_data(),
            "defense": self.defense,
            "health": self.health,
            "max_health": type(self).health,
        }
        return data


class BuildingView(GameObjectView):

    def _create_widgets(self) -> None:
        self._widgets["main"] = ttk.Button(
            self.canvas,
            cursor="hand2",
            image=getattr(Image, type(self).__name__.removesuffix("View").lower()),
            style="CustomBlue.TButton",
            takefocus=False,
        )
        self._widgets["health_bar"] = ttk.Progressbar(
            self.canvas,
            length=Dimension.HEALTH_BAR_LENGTH,
            mode="determinate",
            orient=tk.HORIZONTAL,
            style="Green_Red.Horizontal.TProgressbar",
        )

    def attach_widgets(self, data: dict) -> None:
        self._ids["main"] = self.canvas.create_window(
            *get_pixels(data["x"], data["y"], y_pixel_shift=5.0),
            window=self._widgets["main"],
        )
        self._ids["health_bar"] = self.canvas.create_window(
            *get_pixels(data["x"], data["y"], y_pixel_shift=-22.5),
            window=self._widgets["health_bar"],
        )

    def refresh(self, data: dict, event_handlers: dict[str, Callable]) -> None:
        self._widgets["main"].configure(
            command=event_handlers["click"],
            image=getattr(Image, type(self).__name__.removesuffix("View").lower()),
        )
        self._widgets["health_bar"].configure(
            value=round(data["health"], 2),
            maximum=round(data["max_health"], 2),
        )


class Building(GameObject):

    def _register(self) -> None:
        GameState.blue_unit_by_coordinate[(self.model.x, self.model.y)] = self

    def _unregister(self) -> None:
        del GameState.blue_unit_by_coordinate[(self.model.x, self.model.y)]

    @property
    def event_handlers(self) -> dict[str, Callable]:
        return {"click": self.handle_click_event}

    def handle_click_event(self) -> None:
        match GameState.selected_game_objects:
            case []:
                self._handle_selection()
                GameState.selected_game_objects.append(self)
            case [Building() as building]:
                if building is self:
                    GameState.selected_game_objects.pop()
                    self._handle_deselection()
                else:
                    building.handle_click_event()
                    self.handle_click_event()
            case [Building(), SoldierRecruitment() as recruitment]:
                recruitment.handle_click_event()
                self.handle_click_event()
            case [*rest]:
                raise NotImplementedError(rest)

    def _handle_selection(self) -> None:
        GameState.selected_unit = self
        if display := GameState.displays["stat"]:
            display.refresh()

    def _handle_deselection(self) -> None:
        GameState.selected_unit = None
        if display := GameState.displays["stat"]:
            display.refresh()
