import heapq
import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from game.base import GameObject, GameObjectModel, GameObjectView
from game.buildings.base import Building, BuildingModel
from game.highlights import AttackRangeHighlight, MovementHighlight
from game.miscellaneous import Configuration as C
from game.miscellaneous import Environment as E
from game.miscellaneous import Image, get_pixels, msleep


class SoldierModel(GameObjectModel):

    attack = 30.0
    attack_multipliers: dict[str, float] = {}
    attack_range = 1

    defense = 0.15
    health = 100.0

    mobility = 2

    cost = 10

    def __init__(self, x: int, y: int, color: str, level: int = 1) -> None:
        super().__init__(x, y)
        self.color = color
        self.level = level
        self.experience = 0
        self.moved_this_turn = False
        self.attacked_this_turn = False

        self._register()

    def destroy(self) -> None:
        self._unregister()

    def _register(self) -> None:
        GameObjectModel.occupied_coordinates.add((self.x, self.y))

    def _unregister(self) -> None:
        GameObjectModel.occupied_coordinates.remove((self.x, self.y))

    # GET
    def get_data(self) -> dict:
        data = {
            "name": type(self).__name__.removesuffix("Model"),
            **super().get_data(),
            "color": self.color,
            "level": self.level,
            "experience": self.experience,
            "attack": self.attack,
            "attack_multipliers": self.attack_multipliers,
            "attack_range": self.attack_range,
            "defense": self.defense,
            "health": self.health,
            "max_health": type(self).health,
            "mobility": self.mobility,
            "cost": self.cost,
            "moved_this_turn": self.moved_this_turn,
            "attacked_this_turn": self.attacked_this_turn,
        }
        return data

    def get_approaching_path(self, other: "SoldierModel | BuildingModel") -> tuple[tuple[int, int]]:
        """
        Use the A* pathfinding algorithm to compute the shortest path for self
        to move toward other until other is within self's attack range.
        Trim the path so that it ends at the furthest coordinate self can reach
        this turn and return it.
        """
        start = (self.x, self.y)
        frontier = []
        heapq.heappush(frontier, (0, start))
        cost_table = {start: 0}
        parent_table = {start: None}

        while frontier:
            current = heapq.heappop(frontier)[1]

            if other.get_distance_to(current) <= self.attack_range:
                path = []
                while current:
                    path.append(current)
                    current = parent_table[current]
                path.reverse()
                return tuple(path[: self.mobility + 1])

            new_cost = cost_table[current] + 1
            for dx, dy in {(1, 0), (0, 1), (-1, 0), (0, -1)}:
                x, y = current[0] + dx, current[1] + dy
                if (
                    0 <= x < C.HORIZONTAL_LAND_TILE_COUNT
                    and 0 <= y < C.VERTICAL_TILE_COUNT
                    and (x, y) not in GameObjectModel.occupied_coordinates
                    and ((x, y) not in cost_table or new_cost < cost_table[(x, y)])
                ):
                    heapq.heappush(frontier, (new_cost + other.get_distance_to((x, y)), (x, y)))
                    cost_table[(x, y)] = new_cost
                    parent_table[(x, y)] = current

        # TODO: When other is surrounded by obstacles, self should try to approach it.
        return (start,)

    def get_damage_output_against(self, other: "SoldierModel | BuildingModel") -> float:
        multiplier = self.attack_multipliers.get(type(other).__name__, 1.0)
        return self.attack * multiplier * (1.0 - other.defense)

    # SET
    def move_to(self, x: int, y: int) -> None:
        """
        Move self to the new coordinate.
        """
        self._unregister()
        self.x = x
        self.y = y
        self._register()
        self.moved_this_turn = True

    def assault(self, other: "SoldierModel | BuildingModel") -> None:
        """
        Make self attack other.
        """
        other.health -= self.get_damage_output_against(other)
        self._learn()
        self.attacked_this_turn = True

    def restore_health_by(self, amount: float) -> None:
        """
        Restore self's health by amount (cannot exceed the maximum value).
        """
        self.health = min(self.health + amount, type(self).health)

    def _learn(self, experience: int = 1) -> None:
        self.experience += experience

        LEVEL_UP_EXPERIENCE_BY_LEVEL = {1: 4, 2: 8, 3: 16, 4: 32, 5: 65535}
        while self.experience >= LEVEL_UP_EXPERIENCE_BY_LEVEL[self.level]:
            self.experience -= LEVEL_UP_EXPERIENCE_BY_LEVEL[self.level]
            self.level += 1
            self.attack *= 1.2
            self.defense += 0.05


class SoldierView(GameObjectView):

    def _create_widgets(self) -> None:
        self._widgets["main"] = ttk.Label(self.canvas)
        self._widgets["health_bar"] = ttk.Progressbar(
            self.canvas,
            length=C.HEALTH_BAR_LENGTH,
            mode="determinate",
            orient=tk.HORIZONTAL,
            style="Green_Red.Horizontal.TProgressbar",
        )

    def attach_widgets(self, data: dict) -> None:
        self._ids["main"] = self.canvas.create_window(
            *get_pixels(data["x"], data["y"], y_pixel_shift=5.0),
            window=self._widgets["main"],
        )
        self._ids["health_bar"] = self.canvas.create_window(
            *get_pixels(data["x"], data["y"], y_pixel_shift=-22.5),
            window=self._widgets["health_bar"],
        )

    def refresh(self, data: dict, event_handlers: dict[str, Callable]) -> None:
        if data["color"] == C.BLUE and data["moved_this_turn"] and data["attacked_this_turn"]:
            cursor = "arrow"
            hex_triplet = C.GRAY
            self._widgets["main"].unbind("<ButtonPress-1>")
        else:
            cursor = "hand2"
            hex_triplet = data["color"]
            self._widgets["main"].bind("<ButtonPress-1>", event_handlers["press"])

        color_name = C.COLOR_NAME_BY_HEX_TRIPLET[hex_triplet]
        soldier_name = type(self).__name__.removesuffix("View").lower()

        self._widgets["main"].configure(
            cursor=cursor,
            image=getattr(Image, f"{color_name}_{soldier_name}_{data["level"]}"),
            style=f"Custom{color_name.capitalize()}.TButton",
        )
        self._widgets["health_bar"].configure(maximum=data["max_health"], value=data["health"])

        if self._ids:
            self.canvas.coords(
                self._ids["main"],
                *get_pixels(data["x"], data["y"], y_pixel_shift=5.0),
            )
            self.canvas.coords(
                self._ids["health_bar"],
                *get_pixels(data["x"], data["y"], y_pixel_shift=-22.5),
            )

    def grab_and_bind(self, handler_by_event: dict[str, Callable]) -> None:
        self._widgets["main"].grab_set()
        for event, handler in handler_by_event.items():
            self._widgets["main"].bind(event, handler)

    def unbind_and_release(self, events: tuple[str]) -> None:
        for event in events:
            self._widgets["main"].unbind(event)
        self._widgets["main"].grab_release()

    def move_by(self, dx: int, dy: int) -> None:
        for widget in self._widgets.values():
            widget.place(x=widget.winfo_x() + dx, y=widget.winfo_y() + dy)


class Soldier(GameObject):

    def _register(self) -> None:
        if self.model.color == C.BLUE:
            self._friends = GameObject.unordered_collections["allied_soldier"]
            self._foes = GameObject.unordered_collections["enemy_soldier"]
        else:
            self._friends = GameObject.unordered_collections["enemy_soldier"]
            self._foes = GameObject.unordered_collections["allied_soldier"]

        self._friends.add(self)

    def _unregister(self) -> None:
        self._friends.remove(self)

    def move_to(self, x: int, y: int) -> None:
        self.model.move_to(x, y)
        self.refresh()

    def assault(self, other: "Soldier | Building") -> None:
        self.model.assault(other.model)
        self.refresh()

        if other.model.health > 0.0:
            other.refresh()
        else:
            other.destroy()

    def restore_health_by(self, amount: float) -> None:
        self.model.restore_health_by(amount)
        self.refresh()

    def hunt(self) -> None:
        """
        Identify the optimal rival unit then move toward and potentially attack it.
        """
        MOVE_THEN_KILL = 1
        MOVE_THEN_HIT = 2
        MOVE = 3

        heap = []

        for i, other in enumerate(
            self._foes | GameObject.unordered_collections["critical_building"]
        ):
            path = self.model.get_approaching_path(other.model)
            distance = other.model.get_distance_to(path[-1])
            damage = self.model.get_damage_output_against(other.model)

            if distance > self.model.attack_range:
                action = MOVE
                order_by = [distance, -damage, other.model.health]
            elif damage < other.model.health:
                action = MOVE_THEN_HIT
                order_by = [-damage, other.model.health, distance]
            else:
                action = MOVE_THEN_KILL
                order_by = [-damage, distance]

            heapq.heappush(heap, (action, *order_by, i, path, other))

        action, *_, path, other = heapq.heappop(heap)

        self.move_to(*path[-1])

        if action in {MOVE_THEN_HIT, MOVE_THEN_KILL}:
            self.assault(other)

        # Display trail
        highlights = [
            MovementHighlight.create({"x": x, "y": y}, {"canvas": self.view.canvas})
            for x, y in path[:-1]
        ]

        msleep(self.view.canvas.master, 200)

        for highlight in highlights:
            highlight.destroy()

        msleep(self.view.canvas.master, 200)

    @property
    def event_handlers(self) -> dict[str, Callable]:
        return {
            "press": self._handle_press_event,
            "drag": self._handle_drag_event,
            "release": self._handle_release_event,
        }

    def _handle_press_event(self, event: tk.Event) -> None:
        self.view.grab_and_bind(
            {
                "<Motion>": self.event_handlers["drag"],
                "<ButtonRelease-1>": self.event_handlers["release"],
            }
        )

        self._pressed_x = event.x
        self._pressed_y = event.y

        for obj in GameObject.ordered_collections["selected_game_object"][::-1]:
            obj.handle_click_event()

        GameObject.singletons["pressed_game_object"] = self
        self._refresh_stat_display()

        self._movement_target_by_id = {}
        self._attack_target_by_id = {}

        if self.model.color == C.BLUE:
            # On X11, clean up highlights in case the mouse button was released outside the window.
            if E.WINDOWING_SYSTEM == "x11":
                self._destroy_highlights()

            boundaries = (1, C.HORIZONTAL_LAND_TILE_COUNT - 2, 1, C.VERTICAL_TILE_COUNT - 2)
            prepare_drop = True

            if not self.model.moved_this_turn:
                self._create_movement_highlights(boundaries, prepare_drop)

            if not self.model.attacked_this_turn:
                self._create_attack_range_highlight(prepare_drop)
        else:
            boundaries = (0, C.HORIZONTAL_LAND_TILE_COUNT - 1, 0, C.VERTICAL_TILE_COUNT - 1)
            prepare_drop = False

            self._create_movement_highlights(boundaries, prepare_drop)
            self._create_attack_range_highlight(prepare_drop)

        self.view.lift_widgets()

        if control := GameObject.singletons.get("display_outcome_control"):
            control.view.lift_widgets()

    def _handle_drag_event(self, event: tk.Event) -> None:
        if self.model.color == C.BLUE:
            self.view.move_by(event.x - self._pressed_x, event.y - self._pressed_y)

    def _handle_release_event(self, event: tk.Event) -> None:
        self.view.unbind_and_release(("<ButtonRelease-1>", "<Motion>"))

        del GameObject.singletons["pressed_game_object"]
        self._refresh_stat_display()

        if self.model.color == C.BLUE:
            widget = self.view._widgets["main"]
            x = widget.winfo_x()
            y = widget.winfo_y()

            overlapping_ids = set(self.view.canvas.find_overlapping(x, y, x + 40, y + 40))

            if target_ids := overlapping_ids & set(self._movement_target_by_id):
                if len(target_ids) == 1:
                    highlight = self._movement_target_by_id[target_ids.pop()]
                    self.move_to(highlight.model.x, highlight.model.y)
            elif target_ids := overlapping_ids & set(self._attack_target_by_id):
                if len(target_ids) == 1:
                    soldier = self._attack_target_by_id[target_ids.pop()]
                    self.assault(soldier)

            self.view.detach_widgets()
            self.view.attach_widgets(self.model.get_data())

        self._destroy_highlights()

    def _refresh_stat_display(self) -> None:
        if display := GameObject.singletons.get("stat_display"):
            display.refresh()

    def _create_movement_highlights(self, boundaries: tuple[int, int, int, int], prepare_drop: bool) -> None:
        for x, y in self._get_reachable_coordinates(boundaries):
            highlight = MovementHighlight.create({"x": x, "y": y}, {"canvas": self.view.canvas})
            if prepare_drop:
                self._movement_target_by_id[highlight.view._ids["main"]] = highlight

    def _create_attack_range_highlight(self, prepare_drop: bool) -> None:
        AttackRangeHighlight.create(
            {
                "x": self.model.x,
                "y": self.model.y,
                "half_diagonal": self.model.attack_range,
            },
            {
                "canvas": self.view.canvas,
            },
        )

        if prepare_drop:
            coordinates = self._get_attackable_coordinates()
            for soldier in self._foes:
                if (soldier.model.x, soldier.model.y) in coordinates:
                    self._attack_target_by_id[soldier.view._ids["main"]] = soldier

    def _destroy_highlights(self) -> None:
        for highlight in set(GameObject.unordered_collections["movement_highlight"]):
            highlight.destroy()

        if highlight := GameObject.singletons.get("attack_range_highlight"):
            highlight.destroy()

    def _get_reachable_coordinates(self, boundaries: tuple[int, int, int, int]) -> set[tuple[int, int]]:
        x_min, x_max, y_min, y_max = boundaries

        start = (self.model.x, self.model.y)
        frontier = {start}
        cost_table = {start: 0}
        reachables = set()

        while frontier:
            current = frontier.pop()

            if cost_table[current] == self.model.mobility:
                continue

            for dx, dy in {(1, 0), (0, 1), (-1, 0), (0, -1)}:
                x, y = current[0] + dx, current[1] + dy

                if (
                    x_min <= x <= x_max
                    and y_min <= y <= y_max
                    and (x, y) not in GameObjectModel.occupied_coordinates
                    and (x, y) not in cost_table
                ):
                    frontier.add((x, y))
                    cost_table[(x, y)] = cost_table[current] + 1
                    reachables.add((x, y))

        return reachables

    def _get_attackable_coordinates(self) -> set[tuple[int, int]]:
        coordinates = set()

        for offset in range(self.model.attack_range + 1):
            for i in range(-offset, offset + 1):
                j = offset - abs(i)
                coordinates.add((self.model.x + i, self.model.y + j))
                if j != 0:
                    coordinates.add((self.model.x + i, self.model.y - j))

        return coordinates
