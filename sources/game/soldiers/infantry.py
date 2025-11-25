from game.soldiers.base import Soldier, SoldierModel, SoldierView


class InfantryModel(SoldierModel):

    attack_multipliers = {
        "ArcherModel": 0.7,
        "CavalryModel": 1.5,
        "HeroModel": 0.7,
    }

    defense = 0.30


class InfantryView(SoldierView):
    pass


class Infantry(Soldier):
    pass
