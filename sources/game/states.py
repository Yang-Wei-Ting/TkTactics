from game.base import GameObject


class GameState:

    # A cost of -1 consumes all mobility points.
    cost_by_coordinate: dict[tuple[int, int], int] = {}
    image_id_by_coordinate: dict[tuple[int, int], int] = {}
    blue_unit_by_coordinate: dict[tuple[int, int], "GameObject"] = {}
    red_unit_by_coordinate: dict[tuple[int, int], "GameObject"] = {}

    wave = 0
