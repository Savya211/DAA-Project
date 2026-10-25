"""
vehicle.py - Vehicle class for the traffic simulation.

Each vehicle knows its direction of travel, its lane position, colour,
and how to draw itself as a top-down car using Pygame shapes.
"""

import pygame
from settings import (
    CAR_LENGTH, CAR_WIDTH, CAR_SPEED, SAFE_GAP, STOP_LINE_GAP,
    NORTH, SOUTH, EAST, WEST,
    DIR_VECTORS,
    CENTER_X, CENTER_Y, LANE_WIDTH, ROAD_WIDTH,
    INTERSECTION_LEFT, INTERSECTION_RIGHT,
    INTERSECTION_TOP, INTERSECTION_BOTTOM,
    SIM_AREA_WIDTH, SCREEN_HEIGHT,
    BLACK, WHITE, DARK_GREY,
)


class Vehicle:
    """Represents a single car moving through the intersection."""

    _next_id = 0

    def __init__(self, direction: str, colour: tuple):
        Vehicle._next_id += 1
        self.id = Vehicle._next_id
        self.direction = direction
        self.colour = colour
        self.speed = CAR_SPEED
        self.stopped = False
        self.passed_stop_line = False # True once front crosses stop line into intersection
        self.crossed = False          # True once the car has fully crossed the intersection
        self.spawn_time = 0.0         # set by generator (simulation clock)
        self.waiting_since = None     # set when car first stops

        # Position is the centre of the car
        self.x, self.y = self._start_position()

    # ── Spawn positions ───────────────────────────────────────────────────
    def _start_position(self) -> tuple[float, float]:
        """Return the spawn (x, y) just off-screen for the given direction."""
        if self.direction == NORTH:
            # Travelling upward → spawns at the bottom, in the LEFT half-lane
            # (approaching lane is the left half of the road from the car's perspective,
            #  which is the RIGHT half on screen since the car faces up)
            x = CENTER_X + LANE_WIDTH // 2
            y = SCREEN_HEIGHT + CAR_LENGTH
        elif self.direction == SOUTH:
            x = CENTER_X - LANE_WIDTH // 2
            y = -CAR_LENGTH
        elif self.direction == EAST:
            x = -CAR_LENGTH
            y = CENTER_Y + LANE_WIDTH // 2
        else:  # WEST
            x = SIM_AREA_WIDTH + CAR_LENGTH
            y = CENTER_Y - LANE_WIDTH // 2
        return float(x), float(y)

    # ── Geometry helpers ──────────────────────────────────────────────────
    def front(self):
        """Return the (x, y) of the front edge of this car."""
        dx, dy = DIR_VECTORS[self.direction]
        return (self.x + dx * CAR_LENGTH / 2,
                self.y + dy * CAR_LENGTH / 2)

    def back(self):
        """Return the (x, y) of the back edge of this car."""
        dx, dy = DIR_VECTORS[self.direction]
        return (self.x - dx * CAR_LENGTH / 2,
                self.y - dy * CAR_LENGTH / 2)

    def rect(self):
        """Axis-aligned bounding rectangle of the car."""
        if self.direction in (NORTH, SOUTH):
            return pygame.Rect(self.x - CAR_WIDTH / 2,
                               self.y - CAR_LENGTH / 2,
                               CAR_WIDTH, CAR_LENGTH)
        else:
            return pygame.Rect(self.x - CAR_LENGTH / 2,
                               self.y - CAR_WIDTH / 2,
                               CAR_LENGTH, CAR_WIDTH)

    # ── Stop-line positions ───────────────────────────────────────────────
    def stop_line_pos(self) -> float:
        """Return the coordinate value where this car's front should stop."""
        if self.direction == NORTH:
            return float(INTERSECTION_BOTTOM + STOP_LINE_GAP)
        elif self.direction == SOUTH:
            return float(INTERSECTION_TOP - STOP_LINE_GAP)
        elif self.direction == EAST:
            return float(INTERSECTION_LEFT - STOP_LINE_GAP)
        else:  # WEST
            return float(INTERSECTION_RIGHT + STOP_LINE_GAP)

    def has_reached_stop_line(self) -> bool:
        """True if the front of the car is at or past the stop line."""
        fx, fy = self.front()
        stop = self.stop_line_pos()
        if self.direction == NORTH:
            return fy <= stop
        elif self.direction == SOUTH:
            return fy >= stop
        elif self.direction == EAST:
            return fx >= stop
        else:  # WEST
            return fx <= stop

    def has_passed_stop_line(self) -> bool:
        """True if the front of the car has moved beyond the stop line."""
        fx, fy = self.front()
        stop = self.stop_line_pos()
        if self.direction == NORTH:
            return fy < stop
        elif self.direction == SOUTH:
            return fy > stop
        elif self.direction == EAST:
            return fx > stop
        else:  # WEST
            return fx < stop

    def is_in_intersection(self) -> bool:
        """True if any part of the car touches the intersection square."""
        box = pygame.Rect(INTERSECTION_LEFT, INTERSECTION_TOP, ROAD_WIDTH, ROAD_WIDTH)
        return self.rect().colliderect(box)

    def is_past_intersection(self) -> bool:
        """True if the car has completely exited the intersection box."""
        bx, by = self.back()
        if self.direction == NORTH:
            return by < INTERSECTION_TOP
        elif self.direction == SOUTH:
            return by > INTERSECTION_BOTTOM
        elif self.direction == EAST:
            return bx > INTERSECTION_RIGHT
        else:  # WEST
            return bx < INTERSECTION_LEFT

    def is_off_screen(self) -> bool:
        """True if the entire car is outside the visible simulation area."""
        bx, by = self.back()
        if self.direction == NORTH:
            return by < -CAR_LENGTH
        elif self.direction == SOUTH:
            return by > SCREEN_HEIGHT + CAR_LENGTH
        elif self.direction == EAST:
            return bx > SIM_AREA_WIDTH + CAR_LENGTH
        else:  # WEST
            return bx < -CAR_LENGTH

    # ── Movement ──────────────────────────────────────────────────────────
    def update(self, dt: float, can_go: bool, vehicles_ahead: list, intersection_clear: bool = True):
        """
        Move the vehicle forward by *dt* seconds.

        Parameters
        ----------
        dt : float          – elapsed time in seconds (already scaled by sim speed).
        can_go : bool       – True if the signal allows this car to proceed.
        vehicles_ahead : list[Vehicle]
            Other vehicles in the same lane that are ahead of this car
            (sorted closest-first).
        intersection_clear : bool
            True if the intersection box is not blocked by cross-traffic.
        """
        dx, dy = DIR_VECTORS[self.direction]
        desired_move = self.speed * dt

        # --- Check following distance to the car directly ahead -----------
        if vehicles_ahead:
            ahead = vehicles_ahead[0]
            gap = self._gap_to(ahead)
            max_move = max(0.0, gap - SAFE_GAP)
            desired_move = min(desired_move, max_move)
            if gap <= SAFE_GAP + 1:
                self.stopped = True
                return

        # --- Check stop line & intersection entry ---
        # Stop at the stop line if:
        #   1. Light is not green (red or yellow), OR
        #   2. Crossing traffic is still clearing the intersection box.
        # BUT: once a car has crossed the stop line / entered the intersection,
        # it MUST NEVER stop for the signal - it must proceed through to clear the road!
        must_stop_at_line = (not can_go or not intersection_clear) and not self.passed_stop_line and not self.crossed

        if must_stop_at_line:
            if self.has_reached_stop_line():
                self.stopped = True
                return
            # Don't overshoot the stop line
            fx, fy = self.front()
            stop = self.stop_line_pos()
            if self.direction == NORTH:
                remaining = fy - stop
            elif self.direction == SOUTH:
                remaining = stop - fy
            elif self.direction == EAST:
                remaining = stop - fx
            else:  # WEST
                remaining = fx - stop

            if remaining >= 0:
                desired_move = min(desired_move, remaining)

        self.stopped = desired_move < 0.5
        self.x += dx * desired_move
        self.y += dy * desired_move

        # Check if the car has entered the intersection
        if not self.passed_stop_line:
            if self.has_passed_stop_line() or self.is_in_intersection():
                self.passed_stop_line = True

        # Mark as crossed once past the intersection
        if not self.crossed and self.is_past_intersection():
            self.crossed = True

    def _gap_to(self, other: 'Vehicle') -> float:
        """Pixel distance from this car's front to *other*'s back (along travel axis)."""
        fx, fy = self.front()
        bx, by = other.back()
        if self.direction == NORTH:
            return fy - by
        elif self.direction == SOUTH:
            return by - fy
        elif self.direction == EAST:
            return bx - fx
        else:  # WEST
            return fx - bx

    # ── Drawing ───────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        """Draw the car as a coloured rectangle with windshield and tail-lights."""
        rect = self.rect()
        # Car body
        pygame.draw.rect(surface, self.colour, rect, border_radius=4)
        # Outline
        pygame.draw.rect(surface, BLACK, rect, width=1, border_radius=4)

        # Windshield (a darker rectangle near the front)
        ws_colour = (30, 30, 60)
        if self.direction == NORTH:
            ws = pygame.Rect(rect.x + 3, rect.y + 2, rect.width - 6, 7)
        elif self.direction == SOUTH:
            ws = pygame.Rect(rect.x + 3, rect.bottom - 9, rect.width - 6, 7)
        elif self.direction == EAST:
            ws = pygame.Rect(rect.right - 9, rect.y + 3, 7, rect.height - 6)
        else:  # WEST
            ws = pygame.Rect(rect.x + 2, rect.y + 3, 7, rect.height - 6)
        pygame.draw.rect(surface, ws_colour, ws, border_radius=2)

        # Tail-lights (two small red squares at the back)
        tl_colour = (200, 0, 0)
        tl_size = 3
        if self.direction == NORTH:
            pygame.draw.rect(surface, tl_colour,
                             (rect.x + 2, rect.bottom - tl_size - 1, tl_size, tl_size))
            pygame.draw.rect(surface, tl_colour,
                             (rect.right - tl_size - 2, rect.bottom - tl_size - 1, tl_size, tl_size))
        elif self.direction == SOUTH:
            pygame.draw.rect(surface, tl_colour,
                             (rect.x + 2, rect.y + 1, tl_size, tl_size))
            pygame.draw.rect(surface, tl_colour,
                             (rect.right - tl_size - 2, rect.y + 1, tl_size, tl_size))
        elif self.direction == EAST:
            pygame.draw.rect(surface, tl_colour,
                             (rect.x + 1, rect.y + 2, tl_size, tl_size))
            pygame.draw.rect(surface, tl_colour,
                             (rect.x + 1, rect.bottom - tl_size - 2, tl_size, tl_size))
        else:  # WEST
            pygame.draw.rect(surface, tl_colour,
                             (rect.right - tl_size - 1, rect.y + 2, tl_size, tl_size))
            pygame.draw.rect(surface, tl_colour,
                             (rect.right - tl_size - 1, rect.bottom - tl_size - 2, tl_size, tl_size))
