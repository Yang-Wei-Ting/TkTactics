from game.base import GameObject
from game.buildings.base import Building, BuildingModel, BuildingView
from game.miscellaneous import Configuration as C
from game.recruitments import ArcherRecruitment, CavalryRecruitment, InfantryRecruitment


class BarrackModel(BuildingModel):
    pass


class BarrackView(BuildingView):
    pass


class Barrack(Building):

    def _register(self) -> None:
        super()._register()
        GameObject.unordered_collections["critical_building"].add(self)

    def _unregister(self) -> None:
        super()._unregister()
        GameObject.unordered_collections["critical_building"].remove(self)

    def _handle_selection(self) -> None:
        super()._handle_selection()

        x = C.HORIZONTAL_FIELD_TILE_COUNT + 1
        InfantryRecruitment.create({"x": x, "y": 8.41}, {"canvas": self.view.canvas})
        ArcherRecruitment.create({"x": x, "y": 9.41}, {"canvas": self.view.canvas})
        CavalryRecruitment.create({"x": x, "y": 10.41}, {"canvas": self.view.canvas})

    def _handle_deselection(self) -> None:
        super()._handle_deselection()

        for recruitment in set(GameObject.unordered_collections["barrack_recruitment"]):
            recruitment.destroy()
