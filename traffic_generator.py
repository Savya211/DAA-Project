"""
traffic_generator.py - Spawns new vehicles independently on all four approaches.

Vehicles are created with random colours at configurable arrival rates.
Safe spawn checks prevent placing a new car on top of an existing one.
"""

import random
from settings import (
    DIRECTIONS, NORTH, SOUTH, EAST, WEST,
    CAR_COLOURS, CAR_LENGTH, SAFE_GAP,
    DEFAULT_SPAWN_PROB,
    CENTER_X, CENTER_Y, LANE_WIDTH,
    SCREEN_HEIGHT, SIM_AREA_WIDTH,
)
from vehicle import Vehicle


class TrafficGenerator:
    """Creates vehicles on every approach each frame based on probability."""

    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)
        self.spawn_prob = DEFAULT_SPAWN_PROB
        self._colour_idx = 0

    def set_spawn_probability(self, p: float):
        self.spawn_prob = max(0.0, min(1.0, p))

    def try_spawn(self, existing_vehicles: dict[str, list]) -> list[Vehicle]:
        """
        Attempt to spawn one vehicle per direction per call.

        Parameters
        ----------
        existing_vehicles : dict mapping direction → list[Vehicle] already on that road.

        Returns
        -------
        List of newly created Vehicle objects (may be empty).
        """
        new_vehicles = []
        for direction in DIRECTIONS:
            if self.rng.random() < self.spawn_prob:
                if self._spawn_safe(direction, existing_vehicles.get(direction, [])):
                    colour = CAR_COLOURS[self._colour_idx % len(CAR_COLOURS)]
                    self._colour_idx += 1
                    v = Vehicle(direction, colour)
                    new_vehicles.append(v)
        return new_vehicles

    # ── Safety check ──────────────────────────────────────────────────────
    @staticmethod
    def _spawn_safe(direction: str, lane_vehicles: list) -> bool:
        """
        Return True if there is room to spawn a new vehicle at the edge
        of the given direction without overlapping an existing one.
        """
        if not lane_vehicles:
            return True

        for v in lane_vehicles:
            if direction == NORTH:
                # Spawn at bottom; check no vehicle is near the bottom edge
                if v.y >= SCREEN_HEIGHT - CAR_LENGTH - SAFE_GAP:
                    return False
            elif direction == SOUTH:
                # Spawn at top
                if v.y <= CAR_LENGTH + SAFE_GAP:
                    return False
            elif direction == EAST:
                # Spawn at left
                if v.x <= CAR_LENGTH + SAFE_GAP:
                    return False
            elif direction == WEST:
                # Spawn at right
                if v.x >= SIM_AREA_WIDTH - CAR_LENGTH - SAFE_GAP:
                    return False
        return True
