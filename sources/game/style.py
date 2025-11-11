import tkinter as tk
from tkinter import ttk

from game.configurations import Color
from game.images import Image
from game.utilities import get_dpi


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
            background=[(Color.BLUE,)],
        )
        style.map(
            "CustomGray.TButton",
            background=[(Color.GRAY,)],
        )
        style.map(
            "CustomRed.TButton",
            background=[(Color.RED,)],
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
            bordercolor="Red",
            borderwidth=0,
            pbarrelief=tk.FLAT,
            thickness=5,
            troughcolor="Red",
        )
        style.element_create("Green_Red.Horizontal.Progressbar.trough", "from", "clam")
        style.layout(
            "Green_Red.Horizontal.TProgressbar",
            [
                (
                    "Green_Red.Horizontal.Progressbar.trough",
                    {
                        "children": [
                            (
                                "Green_Red.Horizontal.Progressbar.pbar",
                                {"side": tk.LEFT, "sticky": tk.NS},
                            ),
                        ],
                        "sticky": tk.NSEW,
                    },
                ),
            ],
        )

    @classmethod
    def _normalize_font_size(cls, font_size: int) -> int:
        if cls._dpi is None:
            cls._dpi = get_dpi()

        return int(font_size * 96 / cls._dpi)
