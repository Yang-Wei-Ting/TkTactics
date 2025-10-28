import heapq
import tkinter as tk
from collections.abc import Callable
from enum import IntEnum, auto
from tkinter import ttk
from typing import TYPE_CHECKING

from game.base import GameObject, GameObjectModel, GameObjectView
from game.configurations import Color, Dimension
from game.highlights import AttackRangeHighlight, MovementHighlight
from game.images import Image
from game.states import Environment, GameState
from game.utilities import get_pixels, msleep

if TYPE_CHECKING:
    from game.buildings.base import Building, BuildingModel


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
        self.max_health = self.health
        self.moved_this_turn = False
        self.attacked_this_turn = False

        if self.color == Color.BLUE:
            self._boundaries = (1, Dimension.HORIZONTAL_FIELD_TILE_COUNT - 2, 1, Dimension.VERTICAL_TILE_COUNT - 2)
            self._friendly_coordinates = GameState.blue_unit_by_coordinate
            self._hostile_coordinates = GameState.red_unit_by_coordinate
        else:
            self._boundaries = (0, Dimension.HORIZONTAL_FIELD_TILE_COUNT - 1, 0, Dimension.VERTICAL_TILE_COUNT - 1)
            self._friendly_coordinates = GameState.red_unit_by_coordinate
            self._hostile_coordinates = GameState.blue_unit_by_coordinate

    # GET
    def get_data(self) -> dict:
        data = {
            "class": "soldier",
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
            "max_health": self.max_health,
            "mobility": self.mobility,
            "cost": self.cost,
            "moved_this_turn": self.moved_this_turn,
            "attacked_this_turn": self.attacked_this_turn,
        }
        return data

    def get_reachable_coordinates(self) -> set[tuple[int, int]]:
        x_min, x_max, y_min, y_max = self._boundaries

        # Dijkstra
        start = (self.x, self.y)
        frontier = [(0, start)]
        cost_table = {start: 0}
        reachables = set()

        while frontier:
            cost_so_far, current = heapq.heappop(frontier)

            if cost_so_far <= self.mobility and current not in self._friendly_coordinates:
                reachables.add(current)

            if cost_so_far >= self.mobility:
                continue

            for dx, dy in {(1, 0), (0, 1), (-1, 0), (0, -1)}:
                neighbor = x, y = current[0] + dx, current[1] + dy

                if (
                    x_min <= x <= x_max
                    and y_min <= y <= y_max
                    and neighbor not in self._hostile_coordinates
                ):
                    step_cost = GameState.cost_by_coordinate[neighbor]
                    if step_cost == -1:
                        step_cost = self.mobility

                    new_cost = cost_so_far + step_cost

                    if neighbor not in cost_table or new_cost < cost_table[neighbor]:
                        heapq.heappush(frontier, (new_cost, neighbor))
                        cost_table[neighbor] = new_cost

        return reachables

    def get_attackable_coordinates(self) -> set[tuple[int, int]]:
        attackables = set()

        for offset in range(self.attack_range + 1):
            for i in range(-offset, offset + 1):
                j = offset - abs(i)
                attackables.add((self.x + i, self.y + j))
                if j != 0:
                    attackables.add((self.x + i, self.y - j))

        return attackables

    def get_approaching_path(self, hostile_unit: "SoldierModel | BuildingModel") -> tuple[tuple[int, int]]:
        """
        Use the A* pathfinding algorithm to compute the cheapest path for self to
        move toward hostile_unit until hostile_unit is within self's attack range.
        Trim the path so that it ends at the furthest coordinate self can reach
        this turn and return it.
        """
        x_min, x_max, y_min, y_max = self._boundaries

        start = (self.x, self.y)
        frontier = [(0, start)]
        cost_table = {start: 0}
        parent_table = {start: None}

        optimal_path_this_turn = [start]
        optimal_goal_cost = 65535

        while frontier:
            _, current = heapq.heappop(frontier)

            if hostile_unit.get_distance_to(current) <= self.attack_range:
                c = current

                goal_path = []
                while c:
                    goal_path.append(c)
                    c = parent_table[c]
                goal_path.reverse()

                path_this_turn = [goal_path[0]]
                cost_this_turn = 0
                for step in goal_path[1:]:
                    step_cost = GameState.cost_by_coordinate[step]
                    if step_cost == -1:
                        step_cost = self.mobility

                    if cost_this_turn + step_cost > self.mobility:
                        break

                    path_this_turn.append(step)
                    cost_this_turn += step_cost

                if (
                    cost_table[current] < optimal_goal_cost
                    and path_this_turn[-1] not in self._friendly_coordinates
                ):
                    optimal_path_this_turn = path_this_turn
                    optimal_goal_cost = cost_table[current]

                continue

            for dx, dy in {(1, 0), (0, 1), (-1, 0), (0, -1)}:
                neighbor = x, y = current[0] + dx, current[1] + dy

                if (
                    x_min <= x <= x_max
                    and y_min <= y <= y_max
                    and neighbor not in self._hostile_coordinates
                ):
                    step_cost = GameState.cost_by_coordinate[neighbor]
                    if step_cost == -1:
                        step_cost = self.mobility

                    new_cost = cost_table[current] + step_cost

                    if neighbor not in cost_table or new_cost < cost_table[neighbor]:
                        heapq.heappush(
                            frontier,
                            (new_cost + hostile_unit.get_distance_to(neighbor), neighbor),
                        )
                        cost_table[neighbor] = new_cost
                        parent_table[neighbor] = current

        # TODO: When hostile_unit is surrounded by obstacles, self should try to approach it.
        return tuple(optimal_path_this_turn)

    def get_damage_output_against(self, hostile_unit: "SoldierModel | BuildingModel") -> float:
        multiplier = self.attack_multipliers.get(type(hostile_unit).__name__, 1.0)
        return min(self.attack * multiplier * (1.0 - hostile_unit.defense), hostile_unit.health)

    # SET
    def move_to(self, x: int, y: int) -> None:
        """
        Move self to the new coordinate.
        """
        self.x = x
        self.y = y
        self.moved_this_turn = True

    def assault(self, hostile_unit: "SoldierModel | BuildingModel") -> None:
        """
        Make self attack hostile_unit.
        """
        hostile_unit.health -= self.get_damage_output_against(hostile_unit)
        self._learn()
        self.attacked_this_turn = True

    def restore_health_by(self, amount: float) -> None:
        """
        Restore self's health by amount (cannot exceed the maximum value).
        """
        self.health = min(self.health + amount, self.max_health)

    def _learn(self, experience: int = 1) -> None:
        self.experience += experience

        LEVEL_UP_EXPERIENCE_BY_LEVEL = {1: 5, 2: 7, 3: 9, 4: 11, 5: 65535}
        while self.experience >= LEVEL_UP_EXPERIENCE_BY_LEVEL[self.level]:
            self.experience -= LEVEL_UP_EXPERIENCE_BY_LEVEL[self.level]
            self.level += 1
            self.attack *= 1.2
            self.defense += 0.05
            self.health += self.max_health * 0.1
            self.max_health *= 1.1


class SoldierView(GameObjectView):

    def _create_widgets(self) -> None:
        self._widgets["main"] = ttk.Label(self.canvas)
        self._widgets["level"] = ttk.Label(self.canvas)
        self._widgets["health_bar"] = ttk.Progressbar(
            self.canvas,
            length=Dimension.HEALTH_BAR_LENGTH,
            mode="determinate",
            orient=tk.HORIZONTAL,
            style="Green_Red.Horizontal.TProgressbar",
        )

    def attach_widgets(self, data: dict) -> None:
        self._ids["main"] = self.canvas.create_window(
            *get_pixels(data["x"], data["y"], y_pixel_shift=5.0),
            window=self._widgets["main"],
        )
        self._ids["level"] = self.canvas.create_window(
            *get_pixels(data["x"], data["y"], x_pixel_shift=-15.0, y_pixel_shift=-10.0),
            window=self._widgets["level"],
        )
        self._ids["health_bar"] = self.canvas.create_window(
            *get_pixels(data["x"], data["y"], y_pixel_shift=-22.5),
            window=self._widgets["health_bar"],
        )

    def refresh(self, data: dict, event_handlers: dict[str, Callable]) -> None:
        if data["color"] == Color.BLUE and data["moved_this_turn"] and data["attacked_this_turn"]:
            cursor = "arrow"
            hex_triplet = Color.GRAY
            self._widgets["main"].unbind("<ButtonPress-1>")
        else:
            cursor = "hand2"
            hex_triplet = data["color"]
            self._widgets["main"].bind("<ButtonPress-1>", event_handlers["press"])

        color_name = Color.COLOR_NAME_BY_HEX_TRIPLET[hex_triplet]
        soldier_name = type(self).__name__.removesuffix("View").lower()

        self._widgets["main"].configure(
            cursor=cursor,
            image=getattr(Image, f"{color_name}_{soldier_name}"),
            style=f"Custom{color_name.capitalize()}.TButton",
        )
        self._widgets["level"].configure(
            cursor="arrow",
            image=getattr(Image, f"{color_name}_level_{data["level"]}"),
            style=f"Flat.Custom{color_name.capitalize()}.TButton",
        )
        self._widgets["health_bar"].configure(
            maximum=round(data["max_health"], 2),
            value=round(data["health"], 2),
        )

        if self._ids:
            self.canvas.coords(
                self._ids["main"],
                *get_pixels(data["x"], data["y"], y_pixel_shift=5.0),
            )
            self.canvas.coords(
                self._ids["level"],
                *get_pixels(data["x"], data["y"], x_pixel_shift=-15.0, y_pixel_shift=-10.0),
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
        if self.model.color == Color.BLUE:
            self._friendly_unit_by_coordinate = GameState.blue_unit_by_coordinate
            self._hostile_unit_by_coordinate = GameState.red_unit_by_coordinate
            self._friendly_soldiers = GameState.soldiers["blue"]
        else:
            self._friendly_unit_by_coordinate = GameState.red_unit_by_coordinate
            self._hostile_unit_by_coordinate = GameState.blue_unit_by_coordinate
            self._friendly_soldiers = GameState.soldiers["red"]

        self._friendly_unit_by_coordinate[(self.model.x, self.model.y)] = self
        self._friendly_soldiers.add(self)

    def _unregister(self) -> None:
        del self._friendly_unit_by_coordinate[(self.model.x, self.model.y)]
        self._friendly_soldiers.remove(self)

    def move_to(self, x: int, y: int) -> None:
        del self._friendly_unit_by_coordinate[(self.model.x, self.model.y)]
        self.model.move_to(x, y)
        self._friendly_unit_by_coordinate[(self.model.x, self.model.y)] = self
        self.refresh()

    def assault(self, hostile_unit: "Soldier | Building") -> None:
        self.model.assault(hostile_unit.model)
        self.refresh()

        if hostile_unit.model.health:
            # Blink a unit's image when it is being attacked
            hostile_unit.view._widgets["main"].configure(image=Image.transparent_40x40)
            if "level" in hostile_unit.view._widgets:
                hostile_unit.view._widgets["level"].configure(image=Image.transparent_10x10)

            msleep(hostile_unit.view.canvas.master, 100)

            hostile_unit.refresh()
            hostile_unit_destroyed = False
        else:
            hostile_unit.destroy()
            hostile_unit_destroyed = True

        if GameState.selected_unit:
            if GameState.selected_unit is self:
                self._refresh_stat_display()
            elif GameState.selected_unit is hostile_unit:
                if hostile_unit_destroyed:
                    GameState.selected_unit = None
                self._refresh_stat_display()

    def restore_health_by(self, amount: float) -> None:
        self.model.restore_health_by(amount)
        self.refresh()

        if GameState.selected_unit is self:
            self._refresh_stat_display()

    def hunt(self) -> None:
        """
        Identify the optimal hostile unit then move toward and potentially attack it.
        """

        class Action(IntEnum):
            MOVE_THEN_KILL = auto()
            MOVE_THEN_HIT = auto()
            MOVE = auto()

        priority_queue = []

        for i, hostile_unit in enumerate(self._hostile_unit_by_coordinate.values()):
            path = self.model.get_approaching_path(hostile_unit.model)
            distance = hostile_unit.model.get_distance_to(path[-1])
            damage = self.model.get_damage_output_against(hostile_unit.model)

            if distance > self.model.attack_range:
                action = Action.MOVE
                order_by = [distance, -damage, hostile_unit.model.health]
            elif damage < hostile_unit.model.health:
                action = Action.MOVE_THEN_HIT
                order_by = [-damage, hostile_unit.model.health, -distance]
            else:
                action = Action.MOVE_THEN_KILL
                order_by = [-damage, -distance]

            heapq.heappush(priority_queue, (action, *order_by, i, path, hostile_unit))

        action, *_, path, hostile_unit = heapq.heappop(priority_queue)

        self.move_to(*path[-1])

        # Display trail
        highlights = [
            MovementHighlight.create({"x": x, "y": y}, {"canvas": self.view.canvas})
            for x, y in path[:-1]
        ]

        msleep(self.view.canvas.master, 200)

        for highlight in highlights:
            highlight.destroy()

        msleep(self.view.canvas.master, 200)

        if action in {Action.MOVE_THEN_HIT, Action.MOVE_THEN_KILL}:
            self.assault(hostile_unit)

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

        for obj in GameState.selected_game_objects[::-1]:
            obj.handle_click_event()

        GameState.selected_unit = self
        self._refresh_stat_display()

        self._movement_target_by_id = {}
        self._attack_target_by_id = {}

        if self.model.color == Color.BLUE:
            # On X11, clean up highlights in case the mouse button was released outside the window.
            if Environment.windowing_system == "x11":
                self._destroy_highlights()

            prepare_drop = True

            if not self.model.moved_this_turn:
                self._create_movement_highlights(prepare_drop)

            if not self.model.attacked_this_turn:
                self._create_attack_range_highlight(prepare_drop)
        else:
            prepare_drop = False

            self._create_movement_highlights(prepare_drop)
            self._create_attack_range_highlight(prepare_drop)

        self.view.lift_widgets()

        if control := GameState.controls["display_outcome"]:
            control.view.lift_widgets()

    def _handle_drag_event(self, event: tk.Event) -> None:
        if self.model.color == Color.BLUE:
            self.view.move_by(event.x - self._pressed_x, event.y - self._pressed_y)

    def _handle_release_event(self, event: tk.Event) -> None:
        self.view.unbind_and_release(("<ButtonRelease-1>", "<Motion>"))

        if self.model.color == Color.BLUE:
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
                    hostile_unit = self._attack_target_by_id[target_ids.pop()]
                    self.assault(hostile_unit)

            self.view.detach_widgets()
            self.view.attach_widgets(self.model.get_data())

        self._destroy_highlights()

    def _refresh_stat_display(self) -> None:
        if display := GameState.displays["stat"]:
            display.refresh()

    def _create_movement_highlights(self, prepare_drop: bool) -> None:
        for x, y in self.model.get_reachable_coordinates():
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
            coordinates = self.model.get_attackable_coordinates()
            for unit in self._hostile_unit_by_coordinate.values():
                if (unit.model.x, unit.model.y) in coordinates:
                    self._attack_target_by_id[unit.view._ids["main"]] = unit

    def _destroy_highlights(self) -> None:
        for highlight in set(GameState.highlights["movement"]):
            highlight.destroy()

        if highlight := GameState.highlights["attack_range"]:
            highlight.destroy()
