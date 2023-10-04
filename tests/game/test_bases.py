import tkinter as tk
from unittest import TestCase, mock

from game.states import GameState
from play import Program


class NonBlockingTk(tk.Tk):

    def mainloop(self, n=0):
        while self.dooneevent(tk._tkinter.ALL_EVENTS | tk._tkinter.DONT_WAIT):
            pass


class BaseTest(TestCase):

    @classmethod
    def setUpClass(cls):
        with (
            mock.patch("play.tk.Tk", new=NonBlockingTk),
            mock.patch.object(Program, "_create_landscape"),
            mock.patch.object(Program, "_create_initial_buildings"),
            mock.patch.object(Program, "_create_initial_blue_soldiers"),
        ):
            cls.program = Program()

    def setUp(self):
        self.program._create_landscape()

    def tearDown(self):
        # Transient
        self.assertIsNone(GameState.highlights["attack_range"])
        self.assertEqual(GameState.highlights["movement"], set())

        # Outcome
        if obj := GameState.controls["display_outcome"]:
            obj.destroy()
        self.assertIsNone(GameState.controls["display_outcome"])

        # Selected
        for obj in GameState.selected_game_objects[::-1]:
            obj.handle_click_event()
        self.assertEqual(GameState.selected_game_objects, [])
        self.assertEqual(GameState.recruitments["barrack"], set())
        self.assertEqual(GameState.highlights["placement"], set())

        # Pressed
        if GameState.selected_unit:
            GameState.selected_unit = None

        # Soldiers and buildings
        for attr in ["buildings", "soldiers"]:
            for objs in getattr(GameState, attr).values():
                for obj in set(objs):
                    obj.destroy()
                self.assertEqual(objs, set())
        self.assertEqual(GameState.blue_unit_by_coordinate, {})
        self.assertEqual(GameState.red_unit_by_coordinate, {})

        # Landscape
        GameState.cost_by_coordinate.clear()
        for image_id in GameState.image_id_by_coordinate.values():
            self.program._canvas.delete(image_id)
        GameState.image_id_by_coordinate.clear()

        # Side panel
        GameState.wave = 0
        GameState.displays["day"].model.day = 1
        GameState.displays["coin"].model.coin = 10
        GameState.controls["end_turn"].destroy()
        self.program._create_controls()

    @classmethod
    def tearDownClass(cls):
        cls.program._canvas.destroy()
        cls.program._window.destroy()

    def process_events(self):
        while self.program._window.dooneevent(tk._tkinter.ALL_EVENTS | tk._tkinter.DONT_WAIT):
            pass
