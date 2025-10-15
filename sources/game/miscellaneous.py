import shlex
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Optional


class Configuration:
    """
    A class that manages colors and dimensional settings.
    """

    BLUE = "#043E6F"
    GRAY = "#3B3B3B"
    RED = "#801110"
    COLOR_NAME_BY_HEX_TRIPLET = {
        BLUE: "blue",
        GRAY: "gray",
        RED: "red",
    }

    # In pixels
    TILE_DIMENSION = 60
    HEALTH_BAR_LENGTH = 45

    HORIZONTAL_FIELD_TILE_COUNT = 21
    HORIZONTAL_PANEL_TILE_COUNT = 3
    HORIZONTAL_TILE_COUNT = HORIZONTAL_FIELD_TILE_COUNT + HORIZONTAL_PANEL_TILE_COUNT
    VERTICAL_TILE_COUNT = 13


class Environment:

    SCREEN_HEIGHT: Optional[int] = None
    SCREEN_WIDTH: Optional[int] = None
    TCL_TK_VERSION: Optional[str] = None
    WINDOWING_SYSTEM: Optional[str] = None


class Image:

    @classmethod
    def initialize(cls) -> None:
        """
        Hook all images onto cls.
        """
        for path in Path("images").rglob("*.gif"):
            setattr(cls, path.stem, tk.PhotoImage(file=str(path)))


class ImproperlyConfigured(Exception):
    pass


def execute(command: str) -> str:
    options = {"capture_output": True, "check": True, "text": True}
    return subprocess.run(shlex.split(command), **options).stdout.rstrip()


def get_dpi() -> int:
    try:
        dpi = int(execute("xrdb -get Xft.dpi"))
        if dpi <= 0:
            raise ValueError
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        dpi = 96

    return dpi


class Style:

    _dpi = None

    @classmethod
    def initialize(cls) -> None:
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "TButton",
            anchor=tk.CENTER,
            borderwidth=3,
            focusthickness=0,
            padding=0,
            relief=tk.RAISED,
            width=-1,
        )
        style.map(
            "Black_CustomWood.TButton",
            background=[("#C4A66E",)],
            foreground=[("Black",)],
        )
        style.map(
            "CustomBlue.TButton",
            background=[(Configuration.BLUE,)],
        )
        style.map(
            "CustomGray.TButton",
            background=[(Configuration.GRAY,)],
        )
        style.map(
            "CustomRed.TButton",
            background=[(Configuration.RED,)],
        )
        style.map(
            "Royalblue1.TButton",
            background=[("Royalblue1",)],
        )
        style.configure(
            "OutcomeBanner.Black_CustomWood.TButton",
            compound="center",
            font=("Courier", cls._normalize_font_size(36), "bold italic"),
            image=Image.outcome_banner,
        )
        style.configure(
            "LargePanelBox.Black_CustomWood.TButton",
            compound="center",
            font=("Courier", cls._normalize_font_size(18), "bold"),
            image=Image.large_panel_box,
        )
        style.configure(
            "MiddlePanelBox.Black_CustomWood.TButton",
            image=Image.middle_panel_box,
        )
        style.configure(
            "SmallPanelBox.Black_CustomWood.TButton",
            compound="center",
            font=("Courier", cls._normalize_font_size(18), "bold"),
            image=Image.small_panel_box,
        )
        style.configure(
            "Flat.CustomBlue.TButton",
            borderwidth=0,
            relief=tk.FLAT,
        )
        style.configure(
            "Flat.CustomGray.TButton",
            borderwidth=0,
            relief=tk.FLAT,
        )
        style.configure(
            "Flat.CustomRed.TButton",
            borderwidth=0,
            relief=tk.FLAT,
        )
        style.configure(
            "Flat.Royalblue1.TButton",
            borderwidth=0,
            relief=tk.FLAT,
        )

        style.configure(
            "Green_Red.Horizontal.TProgressbar",
            background="Green",
            borderwidth=0,
            thickness=5,
            troughcolor="Red",
        )

    @classmethod
    def _normalize_font_size(cls, font_size: int) -> int:
        if cls._dpi is None:
            cls._dpi = get_dpi()

        return int(font_size * 96 / cls._dpi)


def get_pixels(x: int, y: int, *, x_pixel_shift: float = 0.0, y_pixel_shift: float = 0.0) -> tuple[float, float]:
    """
    Compute pixels from coordinates and custom pixel shifts.
    """
    return (
        Configuration.TILE_DIMENSION * (x + 0.5) + x_pixel_shift,
        Configuration.TILE_DIMENSION * (y + 0.5) + y_pixel_shift,
    )


def msleep(widget: tk.Misc, time: int) -> None:
    """
    Sleep for time milliseconds.
    """
    flag = tk.BooleanVar()
    widget.after(time, flag.set, True)
    widget.wait_variable(flag)
