import sys
from collections.abc import Callable
from tkinter import ttk

from game.base import GameObject, GameObjectModel, GameObjectView
from game.configurations import Color, Dimension
from game.highlights import PlacementHighlight
from game.images import Image
from game.soldiers.base import Soldier
from game.states import GameState


class SoldierRecruitmentModel(GameObjectModel):
    pass


class SoldierRecruitmentView(GameObjectView):

    def _create_widgets(self) -> None:
        self._widgets["main"] = ttk.Button(self.canvas, takefocus=False)

    def refresh(self, data: dict, event_handlers: dict[str, Callable]) -> None:
        if data["coin_reserve"] >= data["recruit_cost"]:
            color = Color.BLUE
            command = event_handlers["click"]
        else:
            color = Color.GRAY
            command = lambda: None

        color_name = Color.COLOR_NAME_BY_HEX_TRIPLET[color]
        soldier_name = data["recruit_name"]

        self._widgets["main"].configure(
            command=command,
            cursor="hand2",
            image=getattr(Image, f"{color_name}_{soldier_name}"),
            style=f"Custom{color_name.capitalize()}.TButton",
        )


class SoldierRecruitment(GameObject):

    @property
    def target(self) -> type[Soldier]:
        module = sys.modules["game.soldiers"]
        return getattr(module, type(self).__name__.removesuffix("Recruitment"))

    def refresh(self) -> None:
        data = {
            "coin_reserve": GameState.displays["coin"].model.coin,
            "recruit_name": self.target.__name__.lower(),
            "recruit_cost": self.target.get_model_class().cost,
        }
        self.view.refresh(data, self.event_handlers)

    def _register(self) -> None:
        GameState.recruitments["barrack"].add(self)

    def _unregister(self) -> None:
        GameState.recruitments["barrack"].remove(self)

    @property
    def event_handlers(self) -> dict[str, Callable]:
        return {"click": self.handle_click_event}

    def handle_click_event(self) -> None:
        match GameState.selected_game_objects:
            case [_]:
                self._handle_selection()
                GameState.selected_game_objects.append(self)
            case [_, SoldierRecruitment() as recruitment]:
                if recruitment is self:
                    GameState.selected_game_objects.pop()
                    self._handle_deselection()
                else:
                    recruitment.handle_click_event()
                    self.handle_click_event()
            case [*rest]:
                raise NotImplementedError(rest)

    def _handle_selection(self) -> None:
        [building] = GameState.selected_game_objects
        for dx, dy in {
            (1, 0), (1, 1), (0, 1), (-1, 1),
            (-1, 0), (-1, -1), (0, -1), (1, -1),
        }:
            x, y = building.model.x + dx, building.model.y + dy
            if (
                0 < x < Dimension.HORIZONTAL_FIELD_TILE_COUNT - 1
                and 0 < y < Dimension.VERTICAL_TILE_COUNT - 1
                and (x, y) not in (GameState.blue_unit_by_coordinate | GameState.red_unit_by_coordinate)
            ):
                PlacementHighlight.create({"x": x, "y": y}, {"canvas": self.view.canvas})

        if control := GameState.controls["display_outcome"]:
            control.view.lift_widgets()

    def _handle_deselection(self) -> None:
        for highlight in set(GameState.highlights["placement"]):
            highlight.destroy()
