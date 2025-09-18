from collections.abc import Callable
from textwrap import dedent
from tkinter import ttk

from game.base import GameObject
from game.displays.base import Display, DisplayModel, DisplayView


class StatDisplayModel(DisplayModel):
    pass


class StatDisplayView(DisplayView):

    def _create_widgets(self) -> None:
        self._widgets["main"] = ttk.Label(
            self.canvas,
            cursor="arrow",
            style="LargePanelBox.Black_CustomWood.TButton",
        )

    def refresh(self, data: dict, event_handlers: dict[str, Callable]) -> None:
        match data:
            case {"class": cls}:
                text = getattr(self, f"_generate_{cls}_stat")(data)
            case _:
                text = ""

        self._widgets["main"].configure(text=text)

    def _generate_building_stat(self, data: dict) -> str:
        data = data.copy()

        data["defense"] = int(data["defense"] * 100.0)
        data["health"] = int(data["health"])

        return dedent(
            """\
            {name}

            DEF: {defense:4d}
            HP:  {health:4d}







            """
        ).format(**data)

    def _generate_soldier_stat(self, data: dict) -> str:
        data = data.copy()

        data["attack"] = int(data["attack"])
        data["defense"] = int(data["defense"] * 100.0)
        data["health"] = int(data["health"])

        return dedent(
            """\
            {name}

            LVL: {level:4d}
            EXP: {experience:4d}

            ATK: {attack:4d}
            RNG: {attack_range:4d}

            DEF: {defense:4d}
            HP:  {health:4d}

            MOV: {mobility:4d}"""
        ).format(**data)


class StatDisplay(Display):

    def refresh(self) -> None:
        if obj := GameObject.singletons.get("pressed_game_object"):
            data = obj.model.get_data()
        else:
            data = {}

        self.view.refresh(data, self.event_handlers)

    def _register(self) -> None:
        GameObject.singletons["stat_display"] = self

    def _unregister(self) -> None:
        del GameObject.singletons["stat_display"]
