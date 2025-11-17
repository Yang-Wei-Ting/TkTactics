from game.base import GameObject, GameObjectModel, GameObjectView
from game.images import Image
from game.states import GameState
from game.utilities import get_pixels


class AttackRangeHighlightModel(GameObjectModel):

    def __init__(self, x: int, y: int, half_diagonal: int) -> None:
        super().__init__(x, y)
        self.half_diagonal = half_diagonal

    def get_data(self) -> dict:
        data = {
            **super().get_data(),
            "half_diagonal": self.half_diagonal,
        }
        return data


class AttackRangeHighlightView(GameObjectView):

    def _create_widgets(self) -> None:
        pass

    def _destroy_widgets(self) -> None:
        pass

    def attach_widgets(self, data: dict) -> None:
        self._ids["main"] = self.canvas.create_image(
            *get_pixels(data["x"], data["y"]),
            image=getattr(Image, "red_diamond_{0}x{0}".format(data["half_diagonal"] * 120)),
        )


class AttackRangeHighlight(GameObject):

    def _register(self) -> None:
        GameState.highlights["attack_range"] = self

    def _unregister(self) -> None:
        GameState.highlights["attack_range"] = None
