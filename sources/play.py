"""
© 2022-2025 Wei-Ting Yang. All rights reserved.
"""

import sys
import tkinter as tk
from random import choices

from game.base import GameObjectModel
from game.buildings import Barrack
from game.controls import EndTurnControl
from game.displays import CoinDisplay, DayDisplay, ProductionDisplay, StatDisplay
from game.miscellaneous import Configuration as C
from game.miscellaneous import Environment as E
from game.miscellaneous import Image, Style, get_pixels
from game.soldiers import Hero


class Program:

    def __init__(self) -> None:
        self._window = tk.Tk()
        self._detect_environment()
        self._check_requirements()
        self._window.title("TkTactics")
        self._window.resizable(width=False, height=False)

        self._canvas = tk.Canvas(
            self._window,
            width=C.TILE_DIMENSION * C.HORIZONTAL_TILE_COUNT,
            height=C.TILE_DIMENSION * C.VERTICAL_TILE_COUNT,
            background="Black",
            highlightthickness=0,
        )
        self._canvas.pack()

        Image.initialize()
        Style.initialize()

        self._create_side_panel()
        self._create_landscape()
        self._create_initial_buildings()
        self._create_initial_allied_soldiers()

        self._window.mainloop()

    def _detect_environment(self) -> None:
        E.SCREEN_HEIGHT = self._window.winfo_screenheight()
        E.SCREEN_WIDTH = self._window.winfo_screenwidth()
        E.TCL_TK_VERSION = self._window.call("info", "patchlevel")
        E.WINDOWING_SYSTEM = self._window.call("tk", "windowingsystem")

    def _check_requirements(self) -> None:
        if E.WINDOWING_SYSTEM == "aqua":
            sys.exit("Aqua windowing system is currently not supported.")

    def _create_side_panel(self) -> None:
        self._canvas.create_image(
            *get_pixels(C.HORIZONTAL_FIELD_TILE_COUNT + 1, C.VERTICAL_TILE_COUNT // 2),
            image=Image.side_panel,
        )
        self._create_displays()
        self._create_controls()

    def _create_displays(self) -> None:
        x = C.HORIZONTAL_FIELD_TILE_COUNT + 1
        DayDisplay.create({"x": x, "y": 0}, {"canvas": self._canvas})
        CoinDisplay.create({"x": x, "y": 1}, {"canvas": self._canvas})
        StatDisplay.create({"x": x, "y": 4.43}, {"canvas": self._canvas})
        ProductionDisplay.create({"x": x, "y": 9.43}, {"canvas": self._canvas})

    def _create_controls(self) -> None:
        x = C.HORIZONTAL_FIELD_TILE_COUNT + 1
        y = C.VERTICAL_TILE_COUNT - 1
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

        for y in range(C.VERTICAL_TILE_COUNT):
            for x in range(C.HORIZONTAL_FIELD_TILE_COUNT):
                [image] = choices(FIELDS, weights=WEIGHTS)
                GameObjectModel.image_id_by_coordinate[(x, y)] = self._canvas.create_image(*get_pixels(x, y), image=image)

                if image in {Image.rock, Image.tree}:
                    GameObjectModel.cost_by_coordinate[(x, y)] = -1
                else:
                    GameObjectModel.cost_by_coordinate[(x, y)] = 1

    def _create_initial_buildings(self) -> None:
        x = C.HORIZONTAL_FIELD_TILE_COUNT // 2
        y = C.VERTICAL_TILE_COUNT // 2

        for dx, dy in {(0, 0), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)}:
            coordinate = (x + dx, y + dy)
            self._canvas.delete(GameObjectModel.image_id_by_coordinate[coordinate])
            GameObjectModel.image_id_by_coordinate[coordinate] = self._canvas.create_image(*get_pixels(*coordinate), image=Image.grass_1)
            GameObjectModel.cost_by_coordinate[coordinate] = 1

        Barrack.create({"x": x, "y": y}, {"canvas": self._canvas})

    def _create_initial_allied_soldiers(self) -> None:
        x = C.HORIZONTAL_FIELD_TILE_COUNT // 2
        y = C.VERTICAL_TILE_COUNT // 2 + 1
        Hero.create({"x": x, "y": y, "color": C.BLUE}, {"canvas": self._canvas})


if __name__ == "__main__":
    program = Program()
