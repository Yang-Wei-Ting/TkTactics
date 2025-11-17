from typing import Optional


class Environment:

    screen_height: Optional[int] = None
    screen_width: Optional[int] = None
    tcl_tk_version: Optional[str] = None
    windowing_system: Optional[str] = None


class GameState:

    buildings = {
        "critical": set(),
        "noncritical": set(),
    }
    controls = {
        "display_outcome": None,
        "end_turn": None,
    }
    displays = {
        "coin": None,
        "day": None,
        "production": None,
        "stat": None,
    }
    highlights = {
        "attack_range": None,
        "movement": set(),
        "placement": set(),
    }
    recruitments = {
        "barrack": set(),
    }
    soldiers = {
        "blue": set(),
        "red": set(),
    }

    selected_game_objects = []
    selected_unit = None

    blue_unit_by_coordinate = {}
    red_unit_by_coordinate = {}
    cost_by_coordinate = {}
    image_id_by_coordinate = {}

    wave = 0
