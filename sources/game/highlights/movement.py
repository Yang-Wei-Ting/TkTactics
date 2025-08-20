from game.base import GameObject, GameObjectModel, GameObjectView
from game.miscellaneous import get_pixels


class MovementHighlightModel(GameObjectModel):
    pass


class MovementHighlightView(GameObjectView):

    def _create_widgets(self) -> None:
        pass

    def _destroy_widgets(self) -> None:
        pass

    def attach_widgets(self, data: dict) -> None:
        x, y = get_pixels(data["x"], data["y"])
        self._ids["main"] = self.canvas.create_rectangle(
            x - 6, y - 6, x + 7, y + 7,
            fill="RoyalBlue1",
            width=0,
        )


class MovementHighlight(GameObject):

    def _register(self) -> None:
        GameObject.unordered_collections["movement_highlight"].add(self)

    def _unregister(self) -> None:
        GameObject.unordered_collections["movement_highlight"].remove(self)
