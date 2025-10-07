class GameState:

    # A cost of -1 consumes all mobility points.
    cost_by_coordinate: dict[tuple[int, int], int] = {}
    image_id_by_coordinate: dict[tuple[int, int], int] = {}
    occupied_coordinates: set[tuple[int, int]] = set()

    wave = 0
