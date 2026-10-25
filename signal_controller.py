"""
signal_controller.py - Fixed-Time and Greedy signal-control strategies.

Both controllers manage the phase cycle (which direction gets green)
while respecting yellow and all-red clearance intervals.
"""

from settings import (
    DIRECTIONS, NORTH, SOUTH, EAST, WEST,
    DEFAULT_GREEN_TIME, DEFAULT_YELLOW_TIME, ALL_RED_TIME,
    MODE_FIXED, MODE_GREEDY,
    GREEDY_VEHICLE_WEIGHT, GREEDY_WAIT_WEIGHT,
    GREEDY_MIN_GREEN, GREEDY_MAX_GREEN,
)
from traffic_light import TrafficLight, STATE_RED, STATE_YELLOW, STATE_GREEN


# Phase definitions – each phase allows one pair of non-conflicting directions.
# For simplicity we use single-direction phases (only one road green at a time).
PHASE_ORDER = [NORTH, SOUTH, EAST, WEST]


class SignalController:
    """Manages traffic-light phasing using a selectable control mode."""

    def __init__(self, lights: dict[str, TrafficLight]):
        """
        Parameters
        ----------
        lights : dict mapping direction string → TrafficLight instance.
        """
        self.lights = lights
        self.mode = MODE_FIXED
        self.green_time = DEFAULT_GREEN_TIME
        self.yellow_time = DEFAULT_YELLOW_TIME
        self.all_red_time = ALL_RED_TIME

        # Phase tracking
        self.current_phase_index = 0           # index into PHASE_ORDER
        self.phase_state = "GREEN"             # GREEN / YELLOW / ALL_RED
        self.phase_timer = 0.0                 # seconds remaining in current sub-phase
        self.green_direction = PHASE_ORDER[0]  # direction currently (or most recently) green

        # Waiting-time accumulators (seconds each direction has waited since last green)
        self.wait_accum = {d: 0.0 for d in DIRECTIONS}

        # Start with the first phase green
        self._apply_phase()

    # ── Public API ────────────────────────────────────────────────────────
    def set_mode(self, mode: str):
        self.mode = mode

    def set_green_time(self, t: float):
        self.green_time = max(3.0, t)

    def reset(self):
        """Reset signal state to initial conditions."""
        self.current_phase_index = 0
        self.phase_state = "GREEN"
        self.phase_timer = 0.0
        self.green_direction = PHASE_ORDER[0]
        self.wait_accum = {d: 0.0 for d in DIRECTIONS}
        self._apply_phase()

    def update(self, dt: float, vehicle_counts: dict[str, int],
               avg_wait_times: dict[str, float]):
        """
        Advance the signal controller by *dt* seconds.

        Parameters
        ----------
        dt             : elapsed simulation time in seconds.
        vehicle_counts : {direction: number of queued vehicles}.
        avg_wait_times : {direction: average waiting time in seconds}.
        """
        self.phase_timer -= dt

        # Accumulate waiting time for non-green directions
        for d in DIRECTIONS:
            if d != self.green_direction or self.phase_state != "GREEN":
                self.wait_accum[d] += dt

        if self.phase_timer <= 0:
            self._advance_phase(vehicle_counts, avg_wait_times)

    def get_phase_info(self) -> str:
        """Return a human-readable description of the current phase."""
        return f"{self.green_direction} {self.phase_state}"

    def get_current_phase_timer(self) -> float:
        """Return the seconds remaining in the current phase state."""
        return max(0.0, self.phase_timer)

    def get_time_remaining(self, direction: str) -> float:
        """
        Return the seconds remaining until the signal for `direction` changes state.

        - GREEN light: seconds until it turns YELLOW.
        - YELLOW light: seconds until it turns RED.
        - RED light: seconds until it turns GREEN.
        """
        cur_timer = max(0.0, self.phase_timer)

        # If this direction is currently active:
        if direction == self.green_direction:
            if self.phase_state in ("GREEN", "YELLOW"):
                return cur_timer

        # For directions that are RED:
        # Calculate time until current active phase finishes its clearance
        if self.phase_state == "GREEN":
            time_to_phase_end = cur_timer + self.yellow_time + self.all_red_time
        elif self.phase_state == "YELLOW":
            time_to_phase_end = cur_timer + self.all_red_time
        else:  # ALL_RED
            time_to_phase_end = cur_timer

        if self.mode == MODE_FIXED:
            target_idx = PHASE_ORDER.index(direction)
            next_idx = (self.current_phase_index + 1) % len(PHASE_ORDER)
            phases_away = (target_idx - next_idx) % len(PHASE_ORDER)
            full_phase_dur = self.green_time + self.yellow_time + self.all_red_time
            return time_to_phase_end + phases_away * full_phase_dur
        else:
            # In Greedy mode: next green is chosen when current phase ends
            return time_to_phase_end

    def get_greedy_scores(self, vehicle_counts: dict[str, int], avg_wait_times: dict[str, float]) -> dict[str, float]:
        """Compute live greedy heuristic scores: score = count + 2 * wait_time."""
        scores = {}
        for d in DIRECTIONS:
            vc = vehicle_counts.get(d, 0)
            wt = avg_wait_times.get(d, 0.0)
            scores[d] = GREEDY_VEHICLE_WEIGHT * vc + GREEDY_WAIT_WEIGHT * wt
        return scores

    # ── Internal phase machine ────────────────────────────────────────────
    def _advance_phase(self, vehicle_counts, avg_wait_times):
        """Transition to the next sub-phase (GREEN → YELLOW → ALL_RED → next GREEN)."""
        if self.phase_state == "GREEN":
            # Transition to yellow
            self.phase_state = "YELLOW"
            self.phase_timer = self.yellow_time
            self.lights[self.green_direction].set_state(STATE_YELLOW)

        elif self.phase_state == "YELLOW":
            # Transition to all-red clearance
            self.phase_state = "ALL_RED"
            self.phase_timer = self.all_red_time
            for light in self.lights.values():
                light.set_state(STATE_RED)

        elif self.phase_state == "ALL_RED":
            # Choose next green phase
            next_dir, green_dur = self._choose_next_phase(vehicle_counts, avg_wait_times)
            self.green_direction = next_dir
            self.current_phase_index = PHASE_ORDER.index(next_dir)
            self.phase_state = "GREEN"
            self.phase_timer = green_dur
            self.wait_accum[next_dir] = 0.0
            self._apply_phase()

    def _choose_next_phase(self, vehicle_counts, avg_wait_times) -> tuple[str, float]:
        """Select which direction gets the next green and for how long."""
        if self.mode == MODE_FIXED:
            # Simple round-robin
            next_idx = (self.current_phase_index + 1) % len(PHASE_ORDER)
            return PHASE_ORDER[next_idx], self.green_time

        else:  # MODE_GREEDY
            return self._greedy_select(vehicle_counts, avg_wait_times)

    def _greedy_select(self, vehicle_counts, avg_wait_times) -> tuple[str, float]:
        """
        Greedy Optimization:
            priority = vehicle_count * w_v  +  waiting_time * w_t

        The direction with the highest priority score gets green.
        Tie-break: the direction that has waited the longest overall (wait_accum).
        If still tied, use a fixed ordering (N, S, E, W).

        Green duration is scaled proportionally between GREEDY_MIN_GREEN and
        GREEDY_MAX_GREEN based on the queue length.
        """
        scores = {}
        for d in DIRECTIONS:
            vc = vehicle_counts.get(d, 0)
            wt = avg_wait_times.get(d, 0.0)
            scores[d] = GREEDY_VEHICLE_WEIGHT * vc + GREEDY_WAIT_WEIGHT * wt

        # Sort by (score DESC, wait_accum DESC, fixed order ASC)
        order = sorted(DIRECTIONS,
                       key=lambda d: (-scores[d], -self.wait_accum[d], PHASE_ORDER.index(d)))
        best = order[0]

        # Adaptive green duration
        vc = vehicle_counts.get(best, 0)
        if vc <= 2:
            green_dur = GREEDY_MIN_GREEN
        elif vc >= 8:
            green_dur = GREEDY_MAX_GREEN
        else:
            ratio = (vc - 2) / 6.0
            green_dur = GREEDY_MIN_GREEN + ratio * (GREEDY_MAX_GREEN - GREEDY_MIN_GREEN)

        return best, green_dur

    def _apply_phase(self):
        """Set light states according to the current green direction."""
        for d, light in self.lights.items():
            if d == self.green_direction:
                light.set_state(STATE_GREEN)
            else:
                light.set_state(STATE_RED)
