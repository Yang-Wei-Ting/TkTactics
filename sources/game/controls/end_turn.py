import tkinter as tk
from collections.abc import Callable, Iterator
from functools import wraps
from math import ceil
from random import choice, sample
from tkinter import ttk

from game.base import GameObject, GameObjectModel, GameObjectView
from game.buildings.base import Building
from game.configurations import Color, Dimension
from game.controls.display_outcome import DisplayOutcomeControl
from game.recruitments.base import SoldierRecruitment
from game.soldiers import Archer, Cavalry, Infantry
from game.soldiers.base import Soldier
from game.states import Environment, GameState
from game.utilities import msleep


def block_user_input_during(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        overlay = tk.Toplevel(self.view.canvas.master)
        overlay.wm_geometry(f"{Environment.screen_width}x{Environment.screen_height}+0+0")

        match Environment.windowing_system:
            case "win32":
                overlay.wm_attributes("-alpha", 0.01, "-disabled", 1, "-topmost", 1)
                overlay.wm_overrideredirect(True)
            case "x11":
                overlay.wm_overrideredirect(True)
                overlay.wait_visibility()
                overlay.wm_attributes("-alpha", 0.01, "-topmost", 1)

                # Wait until the overlay becomes transparent.
                msleep(self.view.canvas.master, 20)

        value = func(self, *args, **kwargs)

        overlay.destroy()

        return value

    return wrapper


class EndTurnControlModel(GameObjectModel):
    pass


class EndTurnControlView(GameObjectView):

    def _create_widgets(self) -> None:
        self._widgets["main"] = ttk.Button(
            self.canvas,
            cursor="hand2",
            style="SmallPanelBox.Black_CustomWood.TButton",
            takefocus=False,
            text="End turn ",
        )

    def refresh(self, data: dict, event_handlers: dict[str, Callable]) -> None:
        self._widgets["main"].configure(command=event_handlers["click"])


class EndTurnControl(GameObject):

    def __init__(self, model: EndTurnControlModel, view: EndTurnControlView) -> None:
        self._day_generator_iterator = self._day_generator_function()
        self._wave_generator_iterator = self._wave_generator_function()
        super().__init__(model, view)

    def _register(self) -> None:
        GameState.controls["end_turn"] = self

    def _unregister(self) -> None:
        GameState.controls["end_turn"] = None

    @property
    def event_handlers(self) -> dict[str, Callable]:
        return {"click": self.handle_click_event}

    @block_user_input_during
    def handle_click_event(self) -> None:
        match GameState.selected_game_objects:
            case [Building(), SoldierRecruitment() as recruitment]:
                recruitment.handle_click_event()

        if GameState.soldiers["red"]:
            for soldier in GameState.soldiers["red"]:
                soldier.model.moved_this_turn = False
                soldier.model.attacked_this_turn = False
                soldier.refresh()

            self._execute_computer_turn()
        else:
            next(self._day_generator_iterator)

        for soldier in GameState.soldiers["blue"]:
            soldier.model.moved_this_turn = False
            soldier.model.attacked_this_turn = False
            soldier.refresh()

    def _execute_computer_turn(self) -> None:
        if not GameState.soldiers["blue"] and not GameState.buildings["critical"]:
            DisplayOutcomeControl.create(
                {"text": "You have been defeated."},
                {"canvas": self.view.canvas},
            )
            return

        for soldier in GameState.soldiers["red"]:
            soldier.hunt()

            if not GameState.soldiers["blue"] and not GameState.buildings["critical"]:
                DisplayOutcomeControl.create(
                    {"text": "You have been defeated."},
                    {"canvas": self.view.canvas},
                )
                break

    def _day_generator_function(self) -> Iterator[None]:
        while True:
            GameState.displays["day"].model.day += 1
            GameState.displays["day"].refresh()
            for soldier in GameState.soldiers["blue"]:
                soldier.restore_health_by(10.0)
            yield

            GameState.displays["day"].model.day += 1
            GameState.displays["day"].refresh()
            try:
                next(self._wave_generator_iterator)
                yield
            except StopIteration:
                while True:
                    DisplayOutcomeControl.create(
                        {"text": "Victory is yours!"},
                        {"canvas": self.view.canvas},
                    )
                    yield

            GameState.displays["day"].model.day += 1
            GameState.displays["day"].refresh()
            GameState.displays["coin"].model.coin += 8 + (GameState.wave * 2)
            GameState.displays["coin"].refresh()
            for soldier in GameState.soldiers["blue"]:
                soldier.restore_health_by(10.0)
            yield

    def _wave_generator_function(self) -> Iterator[None]:
        H = Dimension.HORIZONTAL_FIELD_TILE_COUNT
        V = Dimension.VERTICAL_TILE_COUNT
        area_north_east = [
            *[(x, 0) for x in range(H - 3, H - 1)],     #     2
            *[(H - 1, y) for y in range(6)],            #     ▔▕ 6
        ]
        area_north_west = [
            *[(x, 0) for x in range(1, 3)],             #    2
            *[(0, y) for y in range(6)],                # 6▕ ▔
        ]
        area_south_east = [
            *[(H - 1, y) for y in range(V - 6, V)],     #     ▁▕ 6
            *[(x, V - 1) for x in range(H - 3, H - 1)], #     2
        ]
        area_south_west = [
            *[(0, y) for y in range(V - 6, V)],         # 6▕ ▁
            *[(x, V - 1) for x in range(1, 3)],         #    2
        ]

        def sample_n_coordinates_from_m_areas(n: int, m: int) -> list[tuple[int, int]]:
            coordinates = []
            for area in sample(
                [area_north_east, area_north_west, area_south_east, area_south_west], m
            ):
                coordinates.extend(area)
            return sample(coordinates, n)

        def sample_common_soldiers() -> type[Soldier]:
            return choice([Archer, Cavalry, Infantry])

        common_soldiers = {Archer, Cavalry, Infantry}
        while common_soldiers:
            GameState.wave += 1
            [(x, y)] = sample_n_coordinates_from_m_areas(1, 1)
            common_soldiers.pop().create(
                {"x": x, "y": y, "color": Color.RED},
                {"canvas": self.view.canvas},
            )
            yield

        for n in range(2, 18 + 1, 2):
            m = ceil(n / 6)
            GameState.wave += 1
            for x, y in sample_n_coordinates_from_m_areas(n, m):
                sample_common_soldiers().create(
                    {"x": x, "y": y, "color": Color.RED},
                    {"canvas": self.view.canvas},
                )
            yield
