"""
© 2022-2025 Wei-Ting Yang. All rights reserved.
"""

import sys
import tkinter as tk
from random import choices

from game.buildings import Barrack
from game.configurations import Color, Dimension
from game.controls import EndTurnControl
from game.displays import CoinDisplay, DayDisplay, ProductionDisplay, StatDisplay
from game.images import Image
from game.soldiers import Hero
from game.states import Environment, GameState
from game.style import Style
from game.utilities import get_pixels


class Program:

    def __init__(self) -> None:
        self._window = tk.Tk()
        self._detect_environment()
        self._check_requirements()
        self._window.title("TkTactics")
        self._window.resizable(width=False, height=False)

        self._canvas = tk.Canvas(
            self._window,
            width=Dimension.TILE_DIMENSION * Dimension.HORIZONTAL_TILE_COUNT,
            height=Dimension.TILE_DIMENSION * Dimension.VERTICAL_TILE_COUNT,
            background="Black",
            highlightthickness=0,
        )
        self._canvas.pack()

        Image.initialize()
        Style.initialize()

        self._create_side_panel()
        self._create_landscape()
        self._create_initial_buildings()
        self._create_initial_blue_soldiers()

        self._window.mainloop()

    def _detect_environment(self) -> None:
        Environment.screen_height = self._window.winfo_screenheight()
        Environment.screen_width = self._window.winfo_screenwidth()
        Environment.tcl_tk_version = self._window.call("info", "patchlevel")
        Environment.windowing_system = self._window.call("tk", "windowingsystem")

    def _check_requirements(self) -> None:
        if sys.version_info < (3, 12):
            sys.exit("Python version >= 3.12 is required.")

        if Environment.windowing_system == "aqua":
            sys.exit("Aqua windowing system is currently not supported.")

    def _create_side_panel(self) -> None:
        self._canvas.create_image(
            *get_pixels(Dimension.HORIZONTAL_FIELD_TILE_COUNT + 1, Dimension.VERTICAL_TILE_COUNT // 2),
            image=Image.side_panel,
        )
        self._create_displays()
        self._create_controls()

    def _create_displays(self) -> None:
        x = Dimension.HORIZONTAL_FIELD_TILE_COUNT + 1
        DayDisplay.create({"x": x, "y": 0}, {"canvas": self._canvas})
        CoinDisplay.create({"x": x, "y": 1}, {"canvas": self._canvas})
        StatDisplay.create({"x": x, "y": 4.43}, {"canvas": self._canvas})
        ProductionDisplay.create({"x": x, "y": 9.43}, {"canvas": self._canvas})

    def _create_controls(self) -> None:
        x = Dimension.HORIZONTAL_FIELD_TILE_COUNT + 1
        y = Dimension.VERTICAL_TILE_COUNT - 1
        EndTurnControl.create({"x": x, "y": y}, {"canvas": self._canvas})

    def _create_landscape(self) -> None:
        FIELDS = tuple(
            [
                *(getattr(Image, f"grass_{i}") for i in range(1, 16)),
                Image.rock,
                Image.tree,
            ]
        )
        WEIGHTS = (56, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 15, 15)

        for y in range(Dimension.VERTICAL_TILE_COUNT):
            for x in range(Dimension.HORIZONTAL_FIELD_TILE_COUNT):
                [image] = choices(FIELDS, weights=WEIGHTS)
                GameState.image_id_by_coordinate[(x, y)] = self._canvas.create_image(
                    *get_pixels(x, y),
                    image=image,
                )

                if image in {Image.rock, Image.tree}:
                    GameState.cost_by_coordinate[(x, y)] = -1
                else:
                    GameState.cost_by_coordinate[(x, y)] = 1

    def _create_initial_buildings(self) -> None:
        x = Dimension.HORIZONTAL_FIELD_TILE_COUNT // 2
        y = Dimension.VERTICAL_TILE_COUNT // 2

        for dx, dy in {(0, 0), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)}:
            coordinate = (x + dx, y + dy)
            self._canvas.delete(GameState.image_id_by_coordinate[coordinate])
            GameState.image_id_by_coordinate[coordinate] = self._canvas.create_image(
                *get_pixels(*coordinate),
                image=Image.grass_1,
            )
            GameState.cost_by_coordinate[coordinate] = 1

        Barrack.create({"x": x, "y": y}, {"canvas": self._canvas})

    def _create_initial_blue_soldiers(self) -> None:
        x = Dimension.HORIZONTAL_FIELD_TILE_COUNT // 2
        y = Dimension.VERTICAL_TILE_COUNT // 2 + 1
        Hero.create({"x": x, "y": y, "color": Color.BLUE}, {"canvas": self._canvas})


if __name__ == "__main__":
    program = Program()
