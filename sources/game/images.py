import tkinter as tk
from pathlib import Path


class Image:

    @classmethod
    def initialize(cls) -> None:
        """
        Hook all images onto cls.
        """
        for path in Path("images").rglob("*.gif"):
            setattr(cls, path.stem, tk.PhotoImage(file=str(path)))
