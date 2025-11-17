import shlex
import subprocess
import tkinter as tk

from game.configurations import Dimension


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


def get_pixels(x: int, y: int, *, x_pixel_shift: float = 0.0, y_pixel_shift: float = 0.0) -> tuple[float, float]:
    """
    Compute pixels from coordinates and custom pixel shifts.
    """
    return (
        Dimension.TILE_DIMENSION * (x + 0.5) + x_pixel_shift,
        Dimension.TILE_DIMENSION * (y + 0.5) + y_pixel_shift,
    )


def msleep(widget: tk.Misc, time: int) -> None:
    """
    Sleep for time milliseconds.
    """
    flag = tk.BooleanVar()
    widget.after(time, flag.set, True)
    widget.wait_variable(flag)
