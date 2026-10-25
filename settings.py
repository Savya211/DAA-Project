"""
settings.py - Global configuration for the Traffic Signal Optimization Simulation.

All tuneable constants live here so they can be adjusted without touching game logic.
"""

import pygame

# ─── Window ───────────────────────────────────────────────────────────────────
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SIM_AREA_WIDTH = 850          # pixels reserved for the simulation view
PANEL_WIDTH = SCREEN_WIDTH - SIM_AREA_WIDTH  # right-side control panel
FPS = 60
TITLE = "Traffic Signal Optimization – DAA Mini Project"

# ─── Colours (RGB) ────────────────────────────────────────────────────────────
BLACK       = (0, 0, 0)
WHITE       = (255, 255, 255)
DARK_GREY   = (50, 50, 50)
GREY        = (100, 100, 100)
LIGHT_GREY  = (180, 180, 180)
GREEN_GRASS = (34, 139, 34)
SIDEWALK    = (160, 160, 140)
RED         = (220, 30, 30)
YELLOW      = (240, 200, 30)
GREEN       = (30, 180, 30)
DARK_GREEN  = (20, 100, 20)
SIGNAL_HOUSING = (30, 30, 30)
PANEL_BG    = (40, 44, 52)
PANEL_TEXT  = (220, 220, 220)
BUTTON_BG   = (70, 80, 100)
BUTTON_HOVER = (90, 105, 130)
BUTTON_TEXT  = (240, 240, 240)
SLIDER_BG   = (80, 85, 95)
SLIDER_FG   = (100, 160, 240)

# Car colour palette – used round-robin when spawning
CAR_COLOURS = [
    (0, 100, 200),    # Blue
    (200, 50, 50),    # Red
    (50, 180, 50),    # Green
    (200, 200, 50),   # Yellow
    (180, 80, 200),   # Purple
    (50, 200, 200),   # Cyan
    (230, 130, 50),   # Orange
    (200, 200, 200),  # Silver
]

# ─── Road geometry (pixels, relative to SIM_AREA centre) ─────────────────────
ROAD_WIDTH = 120              # total road width (both directions)
LANE_WIDTH = ROAD_WIDTH // 2  # each direction has one lane
LANE_MARK_WIDTH = 2
STOP_LINE_OFFSET = 8          # distance from the intersection edge to the stop line

# Intersection centre (in simulation-area coordinates)
CENTER_X = SIM_AREA_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2

# Bounding box of the intersection square
INTERSECTION_LEFT   = CENTER_X - ROAD_WIDTH // 2
INTERSECTION_RIGHT  = CENTER_X + ROAD_WIDTH // 2
INTERSECTION_TOP    = CENTER_Y - ROAD_WIDTH // 2
INTERSECTION_BOTTOM = CENTER_Y + ROAD_WIDTH // 2

# ─── Vehicle ──────────────────────────────────────────────────────────────────
CAR_LENGTH = 30      # along direction of travel
CAR_WIDTH  = 20      # perpendicular to travel
CAR_SPEED  = 120     # pixels per second (base speed)
SAFE_GAP   = 10      # minimum gap between vehicles (pixels)
STOP_LINE_GAP = 4    # gap between front of car and stop line

# ─── Traffic generation ───────────────────────────────────────────────────────
DEFAULT_SPAWN_PROB = 0.02     # probability of spawning per frame per road
MIN_SPAWN_PROB = 0.005
MAX_SPAWN_PROB = 0.08

# ─── Signal timing (seconds) ─────────────────────────────────────────────────
DEFAULT_GREEN_TIME  = 10.0
DEFAULT_YELLOW_TIME = 3.0
ALL_RED_TIME        = 1.0
MIN_GREEN_TIME      = 5.0
MAX_GREEN_TIME      = 30.0

# ─── Directions ───────────────────────────────────────────────────────────────
NORTH = "North"
SOUTH = "South"
EAST  = "East"
WEST  = "West"
DIRECTIONS = [NORTH, SOUTH, EAST, WEST]

# Direction → unit velocity (dx, dy)  — positive y is downward in Pygame
DIR_VECTORS = {
    NORTH: (0, -1),   # moving upward
    SOUTH: (0,  1),   # moving downward
    EAST:  (1,  0),   # moving rightward
    WEST:  (-1, 0),   # moving leftward
}

# ─── Signal controller modes ─────────────────────────────────────────────────
MODE_FIXED = "Fixed-Time"
MODE_GREEDY = "Greedy"
MODES = [MODE_FIXED, MODE_GREEDY]

# ─── Greedy formula weights ──────────────────────────────────────────────────
GREEDY_VEHICLE_WEIGHT = 1.0
GREEDY_WAIT_WEIGHT    = 2.0     # weight for average waiting time (seconds)
GREEDY_MIN_GREEN      = 5.0
GREEDY_MAX_GREEN      = 25.0

# ─── Simulation speed multiplier range ────────────────────────────────────────
SIM_SPEED_MIN = 0.5
SIM_SPEED_MAX = 3.0
SIM_SPEED_DEFAULT = 1.0
