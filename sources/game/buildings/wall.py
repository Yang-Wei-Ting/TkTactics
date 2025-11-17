from game.buildings.base import Building, BuildingModel, BuildingView
from game.states import GameState


class WallModel(BuildingModel):

    defense = 0.5
    health = 100.0


class WallView(BuildingView):
    pass


class Wall(Building):

    def _register(self) -> None:
        super()._register()
        GameState.buildings["noncritical"].add(self)

    def _unregister(self) -> None:
        super()._unregister()
        GameState.buildings["noncritical"].remove(self)
