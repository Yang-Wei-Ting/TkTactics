from game.base import GameObject


class GameState:

    # A cost of -1 consumes all mobility points.
    cost_by_coordinate: dict[tuple[int, int], int] = {}
    image_id_by_coordinate: dict[tuple[int, int], int] = {}
    unit_by_coordinate: dict[tuple[int, int], "GameObject"] = {}

    wave = 0
