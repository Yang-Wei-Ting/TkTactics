from enum import Enum, auto
from unittest import main

from game.configurations import Color as C
from game.configurations import Dimension as D
from game.soldiers import Archer, Cavalry, Hero, Infantry
from game.test_bases import BaseTest


class SoldierControlTest(BaseTest):

    def test_click_a_blue_soldier(self):
        pass

    def test_drag_a_blue_soldier_onto_one_of_its_available_movements(self):
        pass

    def test_drag_a_blue_soldier_onto_a_red_soldier_within_its_attack_range(self):
        pass

    def test_click_a_red_soldier(self):
        pass

    def test_drag_a_blue_soldier_onto_a_blue_building_within_its_attack_range(self):
        pass

    def test_drag_a_blue_soldier_onto_a_blue_soldier_within_its_attack_range(self):
        pass

    def test_drag_a_blue_soldier_onto_a_red_soldier_outside_its_attack_range(self):
        pass

    def test_drag_a_blue_soldier_onto_nothing(self):
        pass


class SoldierMatchupTest(BaseTest):

    class Outcome(Enum):
        ATTACKER_WON = auto()
        DEFENDER_WON = auto()

    def fight(self, attacker_cls, defender_cls):
        attacker = attacker_cls.create(
            {"x": D.HORIZONTAL_FIELD_TILE_COUNT // 2, "y": D.VERTICAL_TILE_COUNT // 2 + 2, "color": C.BLUE},
            {"canvas": self.program._canvas},
        )
        defender = defender_cls.create(
            {"x": D.HORIZONTAL_FIELD_TILE_COUNT // 2, "y": D.VERTICAL_TILE_COUNT // 2 - 2, "color": C.RED},
            {"canvas": self.program._canvas},
        )
        self.process_events()

        while True:
            if attacker.model is None:
                return self.Outcome.DEFENDER_WON

            attacker.hunt()
            self.process_events()

            if defender.model is None:
                return self.Outcome.ATTACKER_WON

            defender.hunt()
            self.process_events()

    def test_archer_vs_cavalry(self):
        self.assertEqual(self.fight(Archer, Cavalry), self.Outcome.DEFENDER_WON)

    def test_archer_vs_hero(self):
        self.assertEqual(self.fight(Archer, Hero), self.Outcome.DEFENDER_WON)

    def test_archer_vs_infantry(self):
        self.assertEqual(self.fight(Archer, Infantry), self.Outcome.ATTACKER_WON)

    def test_cavalry_vs_archer(self):
        self.assertEqual(self.fight(Cavalry, Archer), self.Outcome.ATTACKER_WON)

    def test_cavalry_vs_hero(self):
        self.assertEqual(self.fight(Cavalry, Hero), self.Outcome.DEFENDER_WON)

    def test_cavalry_vs_infantry(self):
        self.assertEqual(self.fight(Cavalry, Infantry), self.Outcome.DEFENDER_WON)

    def test_hero_vs_archer(self):
        self.assertEqual(self.fight(Hero, Archer), self.Outcome.ATTACKER_WON)

    def test_hero_vs_cavalry(self):
        self.assertEqual(self.fight(Hero, Cavalry), self.Outcome.ATTACKER_WON)

    def test_hero_vs_infantry(self):
        self.assertEqual(self.fight(Hero, Infantry), self.Outcome.ATTACKER_WON)

    def test_infantry_vs_archer(self):
        self.assertEqual(self.fight(Infantry, Archer), self.Outcome.DEFENDER_WON)

    def test_infantry_vs_cavalry(self):
        self.assertEqual(self.fight(Infantry, Cavalry), self.Outcome.ATTACKER_WON)

    def test_infantry_vs_hero(self):
        self.assertEqual(self.fight(Infantry, Hero), self.Outcome.DEFENDER_WON)


class SoldierPathfindingTest(BaseTest):

    def test_friendly_building_can_be_bypassed(self):
        pass

    def test_friendly_soldier_can_be_bypassed(self):
        pass

    def test_hostile_building_cannot_be_bypassed(self):
        pass

    def test_hostile_soldier_cannot_be_bypassed(self):
        pass

    def test_terrain_costs_are_considered(self):
        pass

    def test_attack_range_is_considered(self):
        pass


class SoldierTargetSelectionTest(BaseTest):

    def test_killable_target_should_be_preferred_over_hittable_or_untouchable_targets(self):
        pass

    def test_hittable_target_should_be_preferred_over_untouchable_target(self):
        pass

    def test_when_multiple_targets_are_killable_then_the_one_with_the_highiest_health_should_be_preferred(self):
        pass

    def test_when_multiple_targets_are_killable_and_have_the_same_health_then_the_closer_one_should_be_preferred(self):
        pass

    def test_when_multiple_targets_are_hittable_then_the_one_that_can_be_dealt_the_highest_damage_should_be_preferred(self):
        pass

    def test_when_multiple_targets_are_hittable_and_can_be_dealt_the_same_ammount_of_damage_then_the_one_with_the_least_amount_of_health_should_be_preferred(self):
        pass

    def test_when_multiple_targets_are_hittable_and_can_be_dealt_the_same_ammount_of_damage_and_have_the_same_amount_of_health_then_the_closer_one_should_be_preferred(self):
        pass

    def test_when_multiple_targets_are_untouchable_then_the_closer_one_should_be_preferred(self):
        pass

    def test_when_multiple_targets_are_untouchable_and_are_equally_far_away_then_the_one_that_can_be_dealt_the_highest_damage_should_be_preferred(self):
        pass

    def test_when_multiple_targets_are_untouchable_and_are_equally_far_away_and_can_be_dealt_the_same_ammount_of_damage_then_the_one_with_the_least_amount_of_health_should_be_preferred(self):
        pass



"""
• · · · · · · · · · ·
· · · · · · · · · · ·
· · · · · · · · · · ·
· · · · · · · · · · ·
· · · · · · · · · · ·
· · · · · · · · · · ·
· · · · A A · · · · ·
· · · · · A · · · · ·
· · · e · · · · · · ·
· · E e · · · · · · ·
· · · · · · · · · · ·
· · · · · · · · · · ·
"""


if __name__ == "__main__":
    main()
