"""
intersection.py - Drawing the roads, lanes, stop lines, and background.

All rendering is done with Pygame drawing primitives (no external images).
"""

import pygame
from settings import (
    SIM_AREA_WIDTH, SCREEN_HEIGHT,
    CENTER_X, CENTER_Y, ROAD_WIDTH, LANE_WIDTH,
    LANE_MARK_WIDTH, STOP_LINE_OFFSET,
    INTERSECTION_LEFT, INTERSECTION_RIGHT,
    INTERSECTION_TOP, INTERSECTION_BOTTOM,
    DARK_GREY, WHITE, GREEN_GRASS, SIDEWALK, LIGHT_GREY, BLACK,
)


def draw_intersection(surface: pygame.Surface):
    """Draw the complete four-way intersection onto *surface*."""

    # 1. Background grass
    surface.fill(GREEN_GRASS)

    # 2. Sidewalks (slightly wider strips beside each road)
    sw = 10  # sidewalk width
    # Vertical road sidewalks
    pygame.draw.rect(surface, SIDEWALK,
                     (CENTER_X - ROAD_WIDTH // 2 - sw, 0,
                      sw, SCREEN_HEIGHT))
    pygame.draw.rect(surface, SIDEWALK,
                     (CENTER_X + ROAD_WIDTH // 2, 0,
                      sw, SCREEN_HEIGHT))
    # Horizontal road sidewalks
    pygame.draw.rect(surface, SIDEWALK,
                     (0, CENTER_Y - ROAD_WIDTH // 2 - sw,
                      SIM_AREA_WIDTH, sw))
    pygame.draw.rect(surface, SIDEWALK,
                     (0, CENTER_Y + ROAD_WIDTH // 2,
                      SIM_AREA_WIDTH, sw))

    # 3. Roads (dark grey asphalt)
    # Vertical road (North-South)
    pygame.draw.rect(surface, DARK_GREY,
                     (INTERSECTION_LEFT, 0, ROAD_WIDTH, SCREEN_HEIGHT))
    # Horizontal road (East-West)
    pygame.draw.rect(surface, DARK_GREY,
                     (0, INTERSECTION_TOP, SIM_AREA_WIDTH, ROAD_WIDTH))

    # 4. Intersection square (ensure it's filled)
    pygame.draw.rect(surface, DARK_GREY,
                     (INTERSECTION_LEFT, INTERSECTION_TOP,
                      ROAD_WIDTH, ROAD_WIDTH))

    # 5. Lane markings — dashed centre lines
    dash_len = 20
    gap_len = 15

    # Vertical centre line (above intersection)
    y = 0
    while y < INTERSECTION_TOP:
        pygame.draw.line(surface, WHITE,
                         (CENTER_X, y), (CENTER_X, min(y + dash_len, INTERSECTION_TOP)),
                         LANE_MARK_WIDTH)
        y += dash_len + gap_len

    # Vertical centre line (below intersection)
    y = INTERSECTION_BOTTOM
    while y < SCREEN_HEIGHT:
        pygame.draw.line(surface, WHITE,
                         (CENTER_X, y), (CENTER_X, min(y + dash_len, SCREEN_HEIGHT)),
                         LANE_MARK_WIDTH)
        y += dash_len + gap_len

    # Horizontal centre line (left of intersection)
    x = 0
    while x < INTERSECTION_LEFT:
        pygame.draw.line(surface, WHITE,
                         (x, CENTER_Y), (min(x + dash_len, INTERSECTION_LEFT), CENTER_Y),
                         LANE_MARK_WIDTH)
        x += dash_len + gap_len

    # Horizontal centre line (right of intersection)
    x = INTERSECTION_RIGHT
    while x < SIM_AREA_WIDTH:
        pygame.draw.line(surface, WHITE,
                         (x, CENTER_Y), (min(x + dash_len, SIM_AREA_WIDTH), CENTER_Y),
                         LANE_MARK_WIDTH)
        x += dash_len + gap_len

    # 6. Stop lines (solid white bars before the intersection)
    sl_thickness = 3

    # North approach (vehicles heading up) → stop line below the intersection
    pygame.draw.line(surface, WHITE,
                     (CENTER_X, INTERSECTION_BOTTOM + STOP_LINE_OFFSET),
                     (INTERSECTION_RIGHT, INTERSECTION_BOTTOM + STOP_LINE_OFFSET),
                     sl_thickness)
    # South approach (vehicles heading down) → stop line above the intersection
    pygame.draw.line(surface, WHITE,
                     (INTERSECTION_LEFT, INTERSECTION_TOP - STOP_LINE_OFFSET),
                     (CENTER_X, INTERSECTION_TOP - STOP_LINE_OFFSET),
                     sl_thickness)
    # East approach (vehicles heading right) → stop line left of intersection
    pygame.draw.line(surface, WHITE,
                     (INTERSECTION_LEFT - STOP_LINE_OFFSET, CENTER_Y),
                     (INTERSECTION_LEFT - STOP_LINE_OFFSET, INTERSECTION_BOTTOM),
                     sl_thickness)
    # West approach (vehicles heading left) → stop line right of intersection
    pygame.draw.line(surface, WHITE,
                     (INTERSECTION_RIGHT + STOP_LINE_OFFSET, INTERSECTION_TOP),
                     (INTERSECTION_RIGHT + STOP_LINE_OFFSET, CENTER_Y),
                     sl_thickness)

    # 7. Road edge lines (thin solid lines on both sides of each road)
    edge_w = 1
    # Vertical road edges
    pygame.draw.line(surface, LIGHT_GREY,
                     (INTERSECTION_LEFT, 0), (INTERSECTION_LEFT, SCREEN_HEIGHT), edge_w)
    pygame.draw.line(surface, LIGHT_GREY,
                     (INTERSECTION_RIGHT, 0), (INTERSECTION_RIGHT, SCREEN_HEIGHT), edge_w)
    # Horizontal road edges
    pygame.draw.line(surface, LIGHT_GREY,
                     (0, INTERSECTION_TOP), (SIM_AREA_WIDTH, INTERSECTION_TOP), edge_w)
    pygame.draw.line(surface, LIGHT_GREY,
                     (0, INTERSECTION_BOTTOM), (SIM_AREA_WIDTH, INTERSECTION_BOTTOM), edge_w)
