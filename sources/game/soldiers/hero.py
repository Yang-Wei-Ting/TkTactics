from game.soldiers.base import Soldier, SoldierModel, SoldierView


class HeroModel(SoldierModel):

    attack_multipliers = {
        "ArcherModel": 1.5,
        "CavalryModel": 1.5,
        "InfantryModel": 1.5,
    }
    attack_range = 2

    defense = 0.30

    mobility = 4

    cost = 65535


class HeroView(SoldierView):
    pass


class Hero(Soldier):
    pass
