"""
traffic_light.py - Traffic light state management and rendering.

Each TrafficLight belongs to one approach direction and displays
Red / Yellow / Green using Pygame-drawn circles inside a dark housing.
"""

import pygame
from settings import (
    RED, YELLOW, GREEN, DARK_GREY, SIGNAL_HOUSING, BLACK, WHITE,
    CENTER_X, CENTER_Y, ROAD_WIDTH,
    INTERSECTION_LEFT, INTERSECTION_RIGHT,
    INTERSECTION_TOP, INTERSECTION_BOTTOM,
    NORTH, SOUTH, EAST, WEST,
)

# Light states
STATE_RED    = "RED"
STATE_YELLOW = "YELLOW"
STATE_GREEN  = "GREEN"


class TrafficLight:
    """Visual traffic signal for one approach direction."""

    LIGHT_RADIUS = 8
    HOUSING_W = 26
    HOUSING_H = 70
    PADDING = 4

    def __init__(self, direction: str):
        self.direction = direction
        self.state = STATE_RED
        self.x, self.y = self._default_position()
        self.time_remaining = 0.0
        self.timer_font = None

    # ── Position next to the intersection ─────────────────────────────────
    def _default_position(self) -> tuple[int, int]:
        """Place the signal housing beside its approach road, just outside the intersection."""
        offset = 20  # gap between intersection edge and the signal
        if self.direction == NORTH:
            # Cars come from below heading up → signal on the right side of incoming lane
            return INTERSECTION_RIGHT + offset, INTERSECTION_BOTTOM + offset
        elif self.direction == SOUTH:
            return INTERSECTION_LEFT - offset - self.HOUSING_W, INTERSECTION_TOP - offset - self.HOUSING_H
        elif self.direction == EAST:
            return INTERSECTION_LEFT - offset - self.HOUSING_H, INTERSECTION_BOTTOM + offset
        else:  # WEST
            return INTERSECTION_RIGHT + offset, INTERSECTION_TOP - offset - self.HOUSING_W

    # ── State helpers ─────────────────────────────────────────────────────
    def set_state(self, state: str):
        self.state = state

    def is_green(self):
        return self.state == STATE_GREEN

    def is_yellow(self):
        return self.state == STATE_YELLOW

    def is_red(self):
        return self.state == STATE_RED

    def allows_go(self):
        """Return True if vehicles may enter the intersection."""
        return self.state == STATE_GREEN

    def set_timer(self, seconds: float):
        """Update the countdown seconds for this signal."""
        self.time_remaining = max(0.0, seconds)

    # ── Drawing ───────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        """Draw the three-circle traffic light housing and digital countdown."""
        if self.direction in (NORTH, SOUTH):
            self._draw_vertical(surface)
        else:
            self._draw_horizontal(surface)

    def _draw_timer(self, surface: pygame.Surface, tx: int, ty: int, tw: int = 34, th: int = 24):
        """Draw an LED digital countdown timer display box."""
        box = pygame.Rect(tx, ty, tw, th)
        # Dark display background
        pygame.draw.rect(surface, (18, 18, 24), box, border_radius=4)

        # Border color & text color based on state
        if self.state == STATE_GREEN:
            border_col = (30, 200, 60)
            text_col = (50, 255, 80)
        elif self.state == STATE_YELLOW:
            border_col = (230, 190, 20)
            text_col = (255, 230, 40)
        else:  # STATE_RED
            border_col = (200, 40, 40)
            text_col = (255, 80, 80)

        pygame.draw.rect(surface, border_col, box, width=1, border_radius=4)

        secs = max(0, int(self.time_remaining + 0.99))
        txt = f"{secs}s"
        if self.timer_font is None:
            self.timer_font = pygame.font.SysFont("Consolas", 12, bold=True)
        lbl = self.timer_font.render(txt, True, text_col)
        surface.blit(lbl, (box.centerx - lbl.get_width() // 2,
                           box.centery - lbl.get_height() // 2))

    def _draw_vertical(self, surface):
        """Draw a vertical signal (for N/S approaches)."""
        rect = pygame.Rect(self.x, self.y, self.HOUSING_W, self.HOUSING_H)
        pygame.draw.rect(surface, SIGNAL_HOUSING, rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, rect, width=1, border_radius=5)

        cx = self.x + self.HOUSING_W // 2
        spacing = self.HOUSING_H // 4

        positions = [
            (cx, self.y + spacing, RED),
            (cx, self.y + 2 * spacing, YELLOW),
            (cx, self.y + 3 * spacing, GREEN),
        ]
        for px, py, colour in positions:
            if self._colour_active(colour):
                pygame.draw.circle(surface, colour, (px, py), self.LIGHT_RADIUS)
            else:
                dim = tuple(c // 4 for c in colour)
                pygame.draw.circle(surface, dim, (px, py), self.LIGHT_RADIUS)
            pygame.draw.circle(surface, BLACK, (px, py), self.LIGHT_RADIUS, width=1)

        # Direction label below
        font = pygame.font.SysFont("Arial", 11, bold=True)
        label = font.render(self.direction[0], True, WHITE)
        surface.blit(label, (cx - label.get_width() // 2, self.y + self.HOUSING_H + 2))

        # Attached digital countdown timer
        if self.direction == NORTH:
            # Beside North housing on the right
            self._draw_timer(surface, self.x + self.HOUSING_W + 5, self.y + 20)
        else:  # SOUTH
            # Beside South housing on the left
            self._draw_timer(surface, self.x - 34 - 5, self.y + 20)

    def _draw_horizontal(self, surface):
        """Draw a horizontal signal (for E/W approaches)."""
        rect = pygame.Rect(self.x, self.y, self.HOUSING_H, self.HOUSING_W)
        pygame.draw.rect(surface, SIGNAL_HOUSING, rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, rect, width=1, border_radius=5)

        cy = self.y + self.HOUSING_W // 2
        spacing = self.HOUSING_H // 4

        positions = [
            (self.x + spacing, cy, RED),
            (self.x + 2 * spacing, cy, YELLOW),
            (self.x + 3 * spacing, cy, GREEN),
        ]
        for px, py, colour in positions:
            if self._colour_active(colour):
                pygame.draw.circle(surface, colour, (px, py), self.LIGHT_RADIUS)
            else:
                dim = tuple(c // 4 for c in colour)
                pygame.draw.circle(surface, dim, (px, py), self.LIGHT_RADIUS)
            pygame.draw.circle(surface, BLACK, (px, py), self.LIGHT_RADIUS, width=1)

        font = pygame.font.SysFont("Arial", 11, bold=True)
        label = font.render(self.direction[0], True, WHITE)
        surface.blit(label, (self.x + self.HOUSING_H + 4, cy - label.get_height() // 2))

        # Attached digital countdown timer
        if self.direction == EAST:
            # Below East housing on grass
            self._draw_timer(surface, self.x + 18, self.y + self.HOUSING_W + 5)
        else:  # WEST
            # Above West housing on grass
            self._draw_timer(surface, self.x + 18, self.y - 24 - 5)

    def _colour_active(self, colour):
        """Check if the given RGB colour matches the current state."""
        if colour == RED and self.state == STATE_RED:
            return True
        if colour == YELLOW and self.state == STATE_YELLOW:
            return True
        if colour == GREEN and self.state == STATE_GREEN:
            return True
        return False
