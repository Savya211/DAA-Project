"""
main.py - Entry point for the Traffic Signal Optimization Simulation.

Manages the Pygame window, game loop, GUI control panel, and ties
together the intersection, vehicles, traffic lights, generator,
and signal controller.
"""

import sys
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SIM_AREA_WIDTH, PANEL_WIDTH, FPS, TITLE,
    DIRECTIONS, NORTH, SOUTH, EAST, WEST,
    ROAD_WIDTH, INTERSECTION_LEFT, INTERSECTION_TOP,
    PANEL_BG, PANEL_TEXT, BUTTON_BG, BUTTON_HOVER, BUTTON_TEXT,
    SLIDER_BG, SLIDER_FG, WHITE, BLACK, GREEN, RED, YELLOW,
    MODE_FIXED, MODE_GREEDY, MODES,
    SIM_SPEED_MIN, SIM_SPEED_MAX, SIM_SPEED_DEFAULT,
    DEFAULT_SPAWN_PROB, MIN_SPAWN_PROB, MAX_SPAWN_PROB,
    DEFAULT_GREEN_TIME, MIN_GREEN_TIME, MAX_GREEN_TIME,
    CAR_SPEED,
)
from intersection import draw_intersection
from traffic_light import TrafficLight
from vehicle import Vehicle
from traffic_generator import TrafficGenerator
from signal_controller import SignalController


# ══════════════════════════════════════════════════════════════════════════════
#  GUI Helper Classes
# ══════════════════════════════════════════════════════════════════════════════

class Button:
    """A simple clickable button."""

    def __init__(self, x, y, w, h, text, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.hovered = False

    def draw(self, surface):
        colour = BUTTON_HOVER if self.hovered else BUTTON_BG
        pygame.draw.rect(surface, colour, self.rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.rect, width=1, border_radius=5)
        label = self.font.render(self.text, True, BUTTON_TEXT)
        surface.blit(label, (self.rect.centerx - label.get_width() // 2,
                             self.rect.centery - label.get_height() // 2))

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class Slider:
    """A horizontal slider with a label and value readout."""

    def __init__(self, x, y, w, label, min_val, max_val, value, font, fmt="{:.2f}"):
        self.x = x
        self.y = y
        self.w = w
        self.h = 16
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.font = font
        self.fmt = fmt
        self.dragging = False
        self.track_rect = pygame.Rect(x, y + 18, w, self.h)

    def draw(self, surface):
        # Label + value
        txt = f"{self.label}: {self.fmt.format(self.value)}"
        lbl = self.font.render(txt, True, PANEL_TEXT)
        surface.blit(lbl, (self.x, self.y))

        # Track
        pygame.draw.rect(surface, SLIDER_BG, self.track_rect, border_radius=4)

        # Filled portion
        ratio = (self.value - self.min_val) / max(0.001, self.max_val - self.min_val)
        fill_w = int(self.w * ratio)
        fill_rect = pygame.Rect(self.x, self.y + 18, fill_w, self.h)
        pygame.draw.rect(surface, SLIDER_FG, fill_rect, border_radius=4)

        # Handle
        hx = self.x + fill_w
        pygame.draw.circle(surface, WHITE, (hx, self.y + 18 + self.h // 2), 8)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.track_rect.inflate(10, 10).collidepoint(event.pos):
                self.dragging = True
                self._update_value(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value(event.pos[0])

    def _update_value(self, mx):
        ratio = (mx - self.x) / max(1, self.w)
        ratio = max(0.0, min(1.0, ratio))
        self.value = self.min_val + ratio * (self.max_val - self.min_val)


class ModeDropdown:
    """A simple two-option dropdown (click to toggle)."""

    def __init__(self, x, y, w, h, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.index = 0

    @property
    def value(self):
        return MODES[self.index]

    def draw(self, surface):
        pygame.draw.rect(surface, BUTTON_BG, self.rect, border_radius=4)
        pygame.draw.rect(surface, WHITE, self.rect, width=1, border_radius=4)
        label = self.font.render(self.value, True, BUTTON_TEXT)
        surface.blit(label, (self.rect.x + 6,
                             self.rect.centery - label.get_height() // 2))
        # Small triangle
        tri_x = self.rect.right - 18
        tri_y = self.rect.centery
        pygame.draw.polygon(surface, WHITE, [
            (tri_x, tri_y - 4), (tri_x + 8, tri_y - 4), (tri_x + 4, tri_y + 4)
        ])

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.index = (self.index + 1) % len(MODES)
                return True
        return False


# ══════════════════════════════════════════════════════════════════════════════
#  Main Application
# ══════════════════════════════════════════════════════════════════════════════

class Simulation:
    """Top-level simulation manager."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_sm = pygame.font.SysFont("Arial", 13)
        self.font_md = pygame.font.SysFont("Arial", 15, bold=True)
        self.font_lg = pygame.font.SysFont("Arial", 18, bold=True)

        # Simulation surface (left portion of the window)
        self.sim_surface = pygame.Surface((SIM_AREA_WIDTH, SCREEN_HEIGHT))

        # Traffic lights
        self.lights = {d: TrafficLight(d) for d in DIRECTIONS}

        # Signal controller
        self.controller = SignalController(self.lights)

        # Traffic generator
        self.generator = TrafficGenerator()

        # Vehicles organised by direction
        self.vehicles: dict[str, list[Vehicle]] = {d: [] for d in DIRECTIONS}

        # State
        self.running = True
        self.started = False
        self.paused = False
        self.sim_time = 0.0        # accumulated simulation seconds
        self.sim_speed = SIM_SPEED_DEFAULT
        self.total_crossed = 0

        # Build GUI
        self._build_gui()

    # ── GUI construction ──────────────────────────────────────────────────
    def _build_gui(self):
        px = SIM_AREA_WIDTH + 15   # panel x start
        pw = PANEL_WIDTH - 30      # usable panel width
        self.btn_start  = Button(px, 15, pw, 30, "Start",  self.font_md)
        self.btn_pause  = Button(px, 52, pw, 30, "Pause",  self.font_md)
        self.btn_reset  = Button(px, 89, pw, 30, "Reset",  self.font_md)
        self.mode_dd    = ModeDropdown(px, 130, pw, 28, self.font_sm)
        self.slider_spawn = Slider(px, 170, pw, "Spawn Rate",
                                   MIN_SPAWN_PROB, MAX_SPAWN_PROB,
                                   DEFAULT_SPAWN_PROB, self.font_sm, "{:.3f}")
        self.slider_green = Slider(px, 215, pw, "Green Time (s)",
                                   MIN_GREEN_TIME, MAX_GREEN_TIME,
                                   DEFAULT_GREEN_TIME, self.font_sm, "{:.1f}")
        self.slider_speed = Slider(px, 260, pw, "Sim Speed",
                                   SIM_SPEED_MIN, SIM_SPEED_MAX,
                                   SIM_SPEED_DEFAULT, self.font_sm, "{:.1f}")

    # ── Main loop ─────────────────────────────────────────────────────────
    def run(self):
        while self.running:
            raw_dt = self.clock.tick(FPS) / 1000.0  # seconds since last frame
            self._handle_events()
            if self.started and not self.paused:
                dt = raw_dt * self.sim_speed
                self._update(dt)
            self._draw()
        pygame.quit()
        sys.exit()

    # ── Event handling ────────────────────────────────────────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # Buttons
            if self.btn_start.handle_event(event):
                self.started = True
                self.paused = False
                self.btn_start.text = "Start"

            if self.btn_pause.handle_event(event):
                if self.started:
                    self.paused = not self.paused
                    self.btn_pause.text = "Resume" if self.paused else "Pause"

            if self.btn_reset.handle_event(event):
                self._reset()

            if self.mode_dd.handle_event(event):
                self.controller.set_mode(self.mode_dd.value)

            # Sliders
            self.slider_spawn.handle_event(event)
            self.slider_green.handle_event(event)
            self.slider_speed.handle_event(event)

            # Apply slider values
            self.generator.set_spawn_probability(self.slider_spawn.value)
            self.controller.set_green_time(self.slider_green.value)
            self.sim_speed = self.slider_speed.value

    # ── Update ────────────────────────────────────────────────────────────
    def _update(self, dt: float):
        self.sim_time += dt

        # 1. Spawn new vehicles
        new = self.generator.try_spawn(self.vehicles)
        for v in new:
            v.spawn_time = self.sim_time
            self.vehicles[v.direction].append(v)

        # 2. Compute vehicle counts & average wait times for the controller
        counts = {}
        avg_waits = {}
        for d in DIRECTIONS:
            waiting = [v for v in self.vehicles[d] if not v.crossed and not v.passed_stop_line]
            counts[d] = len(waiting)
            if waiting:
                total_wait = sum(
                    (self.sim_time - v.spawn_time) for v in waiting if v.stopped
                )
                avg_waits[d] = total_wait / len(waiting)
            else:
                avg_waits[d] = 0.0

        # 3. Update signal controller
        self.controller.update(dt, counts, avg_waits)

        # 4. Update countdown timer on each traffic light
        for d in DIRECTIONS:
            self.lights[d].set_timer(self.controller.get_time_remaining(d))

        # 5. Update vehicles
        intersection_box = pygame.Rect(INTERSECTION_LEFT, INTERSECTION_TOP, ROAD_WIDTH, ROAD_WIDTH)

        for d in DIRECTIONS:
            lane = self.vehicles[d]
            can_go = self.lights[d].allows_go()

            # Check if any perpendicular vehicle is inside the intersection box
            perp_dirs = [EAST, WEST] if d in (NORTH, SOUTH) else [NORTH, SOUTH]
            cross_traffic_present = any(
                v.rect().colliderect(intersection_box)
                for pd in perp_dirs
                for v in self.vehicles[pd]
            )
            intersection_clear = not cross_traffic_present

            # Sort so that the vehicle closest to the intersection is first
            lane.sort(key=lambda v: self._sort_key(v))

            for i, v in enumerate(lane):
                ahead = lane[:i]
                closest = [ahead[-1]] if ahead else []
                # Vehicles that have entered/crossed the intersection are not blocked by the light
                v_can_go = can_go or v.passed_stop_line or v.crossed
                v.update(dt, v_can_go, closest, intersection_clear)

            # Remove vehicles that have left the screen
            before = len(lane)
            self.vehicles[d] = [v for v in lane if not v.is_off_screen()]
            self.total_crossed += before - len(self.vehicles[d])

    def _sort_key(self, v: Vehicle) -> float:
        """Sort vehicles so the one nearest the intersection centre comes first."""
        if v.direction == NORTH:
            return v.y    # smaller y = closer to top = closer to/past intersection
        elif v.direction == SOUTH:
            return -v.y
        elif v.direction == EAST:
            return -v.x
        else:  # WEST
            return v.x

    # ── Reset ─────────────────────────────────────────────────────────────
    def _reset(self):
        self.vehicles = {d: [] for d in DIRECTIONS}
        self.controller.reset()
        self.sim_time = 0.0
        self.total_crossed = 0
        self.started = False
        self.paused = False
        self.btn_pause.text = "Pause"
        self.btn_start.text = "Start"

    # ── Drawing ───────────────────────────────────────────────────────────
    def _draw(self):
        # --- Simulation area ---
        draw_intersection(self.sim_surface)

        # Traffic lights
        for light in self.lights.values():
            light.draw(self.sim_surface)

        # Vehicles
        for d in DIRECTIONS:
            for v in self.vehicles[d]:
                v.draw(self.sim_surface)

        self.screen.blit(self.sim_surface, (0, 0))

        # --- Control panel ---
        panel_rect = pygame.Rect(SIM_AREA_WIDTH, 0, PANEL_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, PANEL_BG, panel_rect)
        pygame.draw.line(self.screen, WHITE, (SIM_AREA_WIDTH, 0),
                         (SIM_AREA_WIDTH, SCREEN_HEIGHT), 2)

        # Buttons & controls
        self.btn_start.draw(self.screen)
        self.btn_pause.draw(self.screen)
        self.btn_reset.draw(self.screen)

        # Mode selector label
        lbl = self.font_sm.render("Mode (click to toggle):", True, PANEL_TEXT)
        self.screen.blit(lbl, (SIM_AREA_WIDTH + 15, 115))
        self.mode_dd.draw(self.screen)

        # Sliders
        self.slider_spawn.draw(self.screen)
        self.slider_green.draw(self.screen)
        self.slider_speed.draw(self.screen)

        # ── Info section ──────────────────────────────────────────────────
        info_y = 308
        px = SIM_AREA_WIDTH + 15

        # Current phase
        phase_txt = self.controller.get_phase_info()
        self._draw_label(px, info_y, "Signal Phase", phase_txt)
        info_y += 26

        # Phase Timer (time until current phase changes)
        phase_rem = self.controller.get_current_phase_timer()
        p_state = self.controller.phase_state
        if p_state == "GREEN":
            p_desc = f"{phase_rem:.1f}s to Yellow"
            p_col = GREEN
        elif p_state == "YELLOW":
            p_desc = f"{phase_rem:.1f}s to All-Red"
            p_col = YELLOW
        else:
            p_desc = f"{phase_rem:.1f}s to Next Green"
            p_col = RED
        lbl_p = self.font_sm.render("Phase Timer:", True, PANEL_TEXT)
        val_p = self.font_md.render(f" {p_desc}", True, p_col)
        self.screen.blit(lbl_p, (px, info_y))
        self.screen.blit(val_p, (px + lbl_p.get_width(), info_y))
        info_y += 28

        # Simulation time
        mins = int(self.sim_time) // 60
        secs = int(self.sim_time) % 60
        self._draw_label(px, info_y, "Sim Time", f"{mins:02d}:{secs:02d}")
        info_y += 26

        # Total crossed
        self._draw_label(px, info_y, "Total Crossed", f"{self.total_crossed} cars")
        info_y += 30

        # Per-direction vehicle counts and countdown timers
        header = self.font_md.render("── Approach Queues & Timers ──", True, (160, 200, 255))
        self.screen.blit(header, (px, info_y))
        info_y += 22

        for d in DIRECTIONS:
            waiting = len([v for v in self.vehicles[d] if not v.crossed and not v.passed_stop_line])
            st = self.lights[d].state
            t_rem = self.controller.get_time_remaining(d)

            if st == "GREEN":
                st_col = GREEN
            elif st == "YELLOW":
                st_col = YELLOW
            else:
                st_col = RED

            dir_lbl = self.font_sm.render(f"{d[:5]:<5}:", True, PANEL_TEXT)
            cnt_lbl = self.font_sm.render(f"{waiting:2d} wait", True, WHITE)
            st_lbl  = self.font_sm.render(f"[{st[:3]}]", True, st_col)
            tm_lbl  = self.font_md.render(f"{t_rem:4.1f}s", True, st_col)

            self.screen.blit(dir_lbl, (px, info_y))
            self.screen.blit(cnt_lbl, (px + 52, info_y))
            self.screen.blit(st_lbl,  (px + 120, info_y))
            self.screen.blit(tm_lbl,  (px + 175, info_y))
            info_y += 22

        # If in Greedy Mode, display live heuristic scores
        if self.controller.mode == MODE_GREEDY:
            info_y += 6
            g_header = self.font_md.render("── Greedy Scores (Q + 2*W) ──", True, (255, 200, 100))
            self.screen.blit(g_header, (px, info_y))
            info_y += 20

            counts = {d: len([v for v in self.vehicles[d] if not v.crossed and not v.passed_stop_line]) for d in DIRECTIONS}
            avg_w = {}
            for d in DIRECTIONS:
                waiting_cars = [v for v in self.vehicles[d] if not v.crossed and not v.passed_stop_line]
                avg_w[d] = sum((self.sim_time - v.spawn_time) for v in waiting_cars if v.stopped) / len(waiting_cars) if waiting_cars else 0.0
            scores = self.controller.get_greedy_scores(counts, avg_w)
            max_d = max(scores, key=scores.get)

            for d in DIRECTIONS:
                sc = scores[d]
                is_max = (d == max_d and counts[d] > 0)
                sc_col = (100, 255, 100) if is_max else PANEL_TEXT
                extra = " [TOP PRIORITY]" if is_max else ""
                sc_txt = self.font_sm.render(f"  {d[:5]}: {sc:.1f}{extra}", True, sc_col)
                self.screen.blit(sc_txt, (px, info_y))
                info_y += 18

        # Status & Active Mode
        info_y = max(info_y + 10, 680)
        if not self.started:
            status = "Press Start"
            status_col = YELLOW
        elif self.paused:
            status = "PAUSED"
            status_col = (255, 120, 120)
        else:
            status = "Running"
            status_col = GREEN

        lbl = self.font_sm.render("Status:", True, PANEL_TEXT)
        val = self.font_md.render(f" {status}", True, status_col)
        self.screen.blit(lbl, (px, info_y))
        self.screen.blit(val, (px + lbl.get_width(), info_y))
        info_y += 26

        self._draw_label(px, info_y, "Active Mode", self.controller.mode)

        # Footer
        footer = self.font_sm.render("DAA Mini Project – Traffic Sim", True, (120, 130, 150))
        self.screen.blit(footer, (SIM_AREA_WIDTH + 15, SCREEN_HEIGHT - 25))

        pygame.display.flip()

    def _draw_label(self, x, y, label, value):
        lbl = self.font_sm.render(label + ":", True, PANEL_TEXT)
        val = self.font_md.render(f" {value}", True, WHITE)
        self.screen.blit(lbl, (x, y))
        self.screen.blit(val, (x + lbl.get_width(), y))


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    sim = Simulation()
    sim.run()
