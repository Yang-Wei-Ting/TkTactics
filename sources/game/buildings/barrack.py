from game.buildings.base import Building, BuildingModel, BuildingView
from game.configurations import Dimension
from game.recruitments import ArcherRecruitment, CavalryRecruitment, InfantryRecruitment
from game.states import GameState


class BarrackModel(BuildingModel):
    pass


class BarrackView(BuildingView):
    pass


class Barrack(Building):

    def _register(self) -> None:
        super()._register()
        GameState.buildings["critical"].add(self)

    def _unregister(self) -> None:
        super()._unregister()
        GameState.buildings["critical"].remove(self)

    def _handle_selection(self) -> None:
        super()._handle_selection()
        self._create_recruitments()

    def _handle_deselection(self) -> None:
        super()._handle_deselection()
        self._destroy_recruitments()

    def _create_recruitments(self) -> None:
        x = Dimension.HORIZONTAL_FIELD_TILE_COUNT + 1
        InfantryRecruitment.create({"x": x, "y": 8.41}, {"canvas": self.view.canvas})
        ArcherRecruitment.create({"x": x, "y": 9.41}, {"canvas": self.view.canvas})
        CavalryRecruitment.create({"x": x, "y": 10.41}, {"canvas": self.view.canvas})

    def _destroy_recruitments(self) -> None:
        for recruitment in set(GameState.recruitments["barrack"]):
            recruitment.destroy()
