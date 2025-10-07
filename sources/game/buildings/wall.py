from game.base import GameObject
from game.buildings.base import Building, BuildingModel, BuildingView


class WallModel(BuildingModel):

    defense = 0.5
    health = 100.0


class WallView(BuildingView):
    pass


class Wall(Building):

    def _register(self) -> None:
        super()._register()
        GameObject.unordered_collections["noncritical_building"].add(self)

    def _unregister(self) -> None:
        super()._unregister()
        GameObject.unordered_collections["noncritical_building"].remove(self)
