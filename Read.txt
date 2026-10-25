# Traffic Signal Optimization Simulation

A 2D top-down traffic intersection simulation built with **Python 3** and **Pygame-CE**. This project serves as a comprehensive **Design and Analysis of Algorithms (DAA)** college mini-project demonstrating and comparing **Fixed-Time Round-Robin Control** and **Greedy Adaptive Optimization** for four-way traffic flow.

---

## 1. Features

- **Realistic 4-Way Intersection:** Dark asphalt roads, dashed lane dividers, stop lines, sidewalks, and surrounding terrain rendered purely via Pygame drawing primitives (zero external graphical assets).
- **Smooth Kinematic Car-Following Model:** Continuous delta-time ($\Delta t$) vehicle motion, safe following headways, deceleration to stop lines, and intersection exit clearance without mid-box stalling.
- **Dynamic Asymmetric Traffic Generation:** Independent Bernoulli arrival distributions per approach with anti-overlap safety checks.
- **Two Signal-Control Paradigms:**
  - **Fixed-Time Control:** Deterministic cyclic phase scheduling (Round-Robin).
  - **Greedy Optimization:** Real-time heuristic priority selection based on queue length and accumulated delay:
    > **Priority Formula:** `Priority(d) = 1.0 × Queue_Count(d) + 2.0 × Average_Wait_Time(d)`
- **Integrated Countdown Timers:**
  - Real-time digital LED timer attached beside each physical traffic signal.
  - GUI control panel with live decimal countdowns to next phase changes and starvation metrics.
- **Interactive Control Panel:** Start, Pause/Resume, Reset buttons, Mode selector, Live Sliders (Spawn Rate, Green Duration, Simulation Speed), and queue telemetry.

---

## 2. Requirements

- **Python:** 3.9 or later (tested up to Python 3.14)
- **Library:** `pygame-ce >= 2.5.0` (Community Edition drop-in replacement with multi-platform prebuilt binaries)

---

## 3. Installation & Execution (Windows)

Open PowerShell or Command Prompt inside the project directory:

```powershell
# 1. Navigate to the project directory
cd "C:\Users\DELL\OneDrive\Desktop\DAA Project\traffic_signal_simulation"

# 2. (Optional) Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the simulation
python main.py
```

---

## 4. GUI Controls & Keybindings

| Control | Type | Description |
|---|---|---|
| **Start** | Button | Initializes and launches the simulation clock and vehicle updates. |
| **Pause / Resume** | Button | Freezes all simulation physics and timers without clearing state. |
| **Reset** | Button | Clears all vehicles from all approaches and re-initializes signals to North. |
| **Mode Selector** | Dropdown | Toggles between **Fixed-Time** and **Greedy** optimization on-the-fly. |
| **Spawn Rate** | Slider | Tunes Bernoulli arrival probability per frame ($p \in [0.005, 0.08]$). |
| **Green Time** | Slider | Sets baseline green phase duration ($t_g \in [5.0\text{ s}, 30.0\text{ s}]$). |
| **Sim Speed** | Slider | Adjusts simulation clock multiplier ($1.0\times$ to $3.0\times$). |

---

## 5. Project Architecture

```
traffic_signal_simulation/
│
├── main.py              # Application entry point, main loop, GUI panel & rendering
├── settings.py          # Global constants, coordinates, timings, and color palette
├── vehicle.py           # Vehicle kinematics, bounding rects, headway & stop-line logic
├── traffic_light.py     # Signal states, transition rendering & attached digital timers
├── intersection.py      # Vector drawing of asphalt, lanes, curbs, and stop lines
├── traffic_generator.py # Stochastic arrival process and spatial clearance validation
├── signal_controller.py # Fixed-Time Round-Robin and Greedy Optimization engines
├── requirements.txt     # Python package requirements
├── Read.txt             # Plaintext version of project analysis
└── README.md            # Comprehensive project & DAA theoretical analysis documentation
```

---

## 6. Comprehensive DAA Algorithm Analysis

### 6.1 Algorithmic Paradigms Implemented

#### Paradigm A: Static Cyclic Permutation (Fixed-Time Round-Robin)
- **Concept:** Rotates green permission through a fixed, invariant sequence:
  > `North → South → East → West → North ...`
- **Transitions:** Each phase allocates a constant duration $T_{\text{green}}$, followed by yellow clearance ($T_{\text{yellow}} = 3.0\text{ s}$) and all-red safety clearance ($T_{\text{all-red}} = 1.0\text{ s}$).
- **Characteristics:** Predictable, deterministic, zero decision overhead, but suffers from high idle delay under asymmetric traffic distributions.

#### Paradigm B: Greedy Heuristic Optimization
- **Concept:** At every phase expiration, an optimal next phase is selected locally by evaluating a heuristic evaluation function:
  > **Formula:** `Priority(d) = 1.0 × C(d) + 2.0 × W(d)`

  Where:
  - `C(d)`: Queue length (number of vehicles waiting behind the stop line on approach $d$).
  - `W(d)`: Mean delay in seconds experienced by stopped vehicles on approach $d$.
  - Weights `1.0` and `2.0`: Balancing weights penalizing driver wait time twice as heavily as raw vehicle count.
- **Tie-Breaking Rule:** Lexicographical order on:  
  `(Priority Score ↓, Accumulated Inaction Delay ↓, Direction ID ↑)`
- **Adaptive Green Allocation:** Green duration is dynamically scaled proportional to queue size:
  - For light queues ($C \le 2$): $T_g = 5.0\text{ s}$
  - For heavy queues ($C \ge 8$): $T_g = 25.0\text{ s}$
  - For intermediate queues ($2 < C < 8$): $T_g = 5.0 + \left(\frac{C - 2}{6}\right) \times 20.0\text{ s}$
- **Starvation Prevention:** A global accumulator `wait_accum[d]` increments every frame approach $d$ is denied green, guaranteeing that as $t \to \infty$, $W(d) \to \infty$, strictly forcing the greedy score to overtake any competing queue.

---

### 6.2 Time Complexity Analysis

Let:
- $K$: Number of intersection approaches ($K = 4$ for a 4-way intersection).
- $N$: Total number of active vehicles currently simulated across all approaches ($N = \sum_{d=1}^K N_d$).
- $N_d$: Number of vehicles present on road $d$ ($N_d \le N$).

#### 1. Signal Controller Phase Decision (`signal_controller._choose_next_phase`)
- **Fixed-Time Mode:**
  - Direct cyclic index advance: `next_idx = (current_idx + 1) % 4`
  - **Best, Average, Worst Case Time Complexity:** $\mathcal{O}(1)$
- **Greedy Optimization Mode:**
  - Evaluates heuristic formula for all $K = 4$ directions: $\mathcal{O}(K)$
  - Multi-key sorting/selection of $K$ elements: $\mathcal{O}(K \log K)$
  - Since $K = 4$ is a constant, this computation runs in bounded time $\mathcal{O}(1)$ relative to vehicle count $N$.
  - **General Form (for $K$ approaches):** $\mathcal{O}(K \log K)$
  - **Best Case:** $\Omega(K)$ (with linear max-heap selection).
  - **Worst Case:** $\mathcal{O}(K \log K)$.
  - **Average Case:** $\Theta(K \log K)$.

#### 2. Signal Countdown Calculation (`signal_controller.get_time_remaining`)
- Computes modular distance $(d_{\text{target}} - d_{\text{next}}) \bmod K$ and scalar arithmetic.
- Evaluated for all $K$ signals per frame.
- **Best, Average, Worst Case:** $\mathcal{O}(1)$ per signal, $\mathcal{O}(K)$ total per frame.

#### 3. Vehicle Sorting per Lane (`main.py: lane.sort`)
- Vehicles in each approach are sorted along their travel axis so the leader is at index $0$.
- Uses Python's **Timsort** (adaptive mergesort/insertionsort hybrid).
- **Best Case:** $\Omega(N_d)$ when the vehicle queue is already in sorted spatial order (common case across consecutive frames).
- **Worst Case:** $\mathcal{O}(N_d \log N_d)$ if spawning causes random reordering.
- **Average Case:** $\Theta(N_d \log N_d)$.
- **Total across all $K$ approaches:**
  - Best Case: $\Omega(N)$
  - Worst Case: $\mathcal{O}\left(\sum_{d=1}^K N_d \log N_d\right) \le \mathcal{O}\left(N \log\frac{N}{K}\right)$

#### 4. Kinematic Motion & Car-Following Update (`vehicle.update`)
- Single vehicle headway comparison: $\mathcal{O}(1)$ scalar arithmetic with front car and stop line.
- Evaluated once per vehicle per frame across $N$ vehicles.
- **Best, Average, Worst Case:** $\Theta(N)$

#### 5. Cross-Traffic Intersection Clearance Verification (`main.py`)
- For each direction $d$, queries whether any perpendicular approach vehicle occupies the central junction bounding box $B$:
  - For North / South traffic: checks vehicles on East and West roads ($N_{\text{perp}} = N_{\text{East}} + N_{\text{West}}$)
  - For East / West traffic: checks vehicles on North and South roads ($N_{\text{perp}} = N_{\text{North}} + N_{\text{South}}$)
- Each AABB (Axis-Aligned Bounding Box) intersection test is $\mathcal{O}(1)$.
- **Best Case:** $\Omega(1)$ (first vehicle tested occupies the box, triggering early exit).
- **Worst Case:** $\mathcal{O}(N_{\text{perp}})$ (no collision found after testing all perpendicular vehicles).
- **Average Case:** $\Theta(N_{\text{perp}})$.

#### 6. Dynamic Traffic Generation (`traffic_generator.try_spawn`)
- Performs pseudo-random Bernoulli trial per approach: $\mathcal{O}(K)$.
- Checks safe distance clearance at the road entry against existing vehicles on that road: $\mathcal{O}(N_d)$.
- **Best Case:** $\Omega(1)$ (probability check fails, no spawn attempted).
- **Worst Case:** $\mathcal{O}(K \cdot N_d)$ (validates spawn point across all vehicles on the approach).
- **Average Case:** $\Theta(K)$.

#### 7. Per-Frame Main Loop Overall Time Complexity
Combining all operations for one simulation tick ($\Delta t$):

```
T_frame = O(Spawn) + O(Sort) + O(Clearance Check) + O(Vehicle Updates) + O(Signal Logic)
        = O(N) + O(N log(N/K)) + O(N) + O(N) + O(K log K)
```

- **Best Case Frame Complexity:** $\Omega(N)$ (queues already sorted, no spawns).
- **Worst Case Frame Complexity:** $\mathcal{O}(N \log N)$ (dominated by Timsort when $N \gg K$).
- **Average Case Frame Complexity:** $\Theta\left(N \log\frac{N}{K}\right)$.

---

### 6.3 Space Complexity Analysis

Let:
- $N$: Number of active `Vehicle` instances currently allocated in memory.
- $K$: Number of approaches ($K = 4$).

#### 1. Primary Data Structures
- **Vehicle Store (`dict[str, list[Vehicle]]`):**
  - Stores references to all active cars: $\Theta(N)$ space.
  - Each `Vehicle` object stores 10 scalar attributes ($x, y, v, \text{id}, \text{direction}, \dots$): $\mathcal{O}(1)$ space per vehicle.
- **Traffic Light Store (`dict[str, TrafficLight]`):**
  - $K$ instances containing state, coordinates, and cached timers: $\Theta(K)$ space.
- **Signal Controller State:**
  - Delay accumulators `wait_accum` $\in \mathbb{R}^K$: $\Theta(K)$ space.
  - Constants and phase indices: $\mathcal{O}(1)$ space.

#### 2. Auxiliary (Temporary) Memory
- **Timsort Auxiliary Memory:** Requires at most $\mathcal{O}(N_d)$ temporary pointer buffer during merge passes. Across all lanes, temporary auxiliary space is bounded by $\mathcal{O}(N)$.
- **Queue Count & Wait Aggregations:** Temporary comprehension lists for waiting vehicles: $\mathcal{O}(N)$ temporary memory during `_update`.
- **Cross-traffic Query Buffer:** $\mathcal{O}(1)$ auxiliary space (boolean generator evaluation).

#### 3. Overall Space Complexity Summary
- **Total Auxiliary Space:** $\mathcal{O}(N)$
- **Total Working Space Complexity:** $\Theta(N + K) \equiv \Theta(N)$ (Linear with respect to active traffic density).

---

## 7. Comparative Algorithm Complexity Matrix

| Metric / Dimension | Fixed-Time Control | Greedy Optimization Control |
|---|---|---|
| **Algorithmic Category** | Static Cyclic Permutation | Dynamic Heuristic Greedy Search |
| **Phase Selection Time Complexity (Best Case)** | $\Omega(1)$ | $\Omega(K)$ |
| **Phase Selection Time Complexity (Worst Case)** | $\mathcal{O}(1)$ | $\mathcal{O}(K \log K)$ |
| **Phase Selection Time Complexity (Average Case)** | $\Theta(1)$ | $\Theta(K \log K)$ |
| **Decision Frequency** | At transition boundaries ($T_{\text{fixed}}$) | At transition boundaries ($T_{\text{adaptive}}$) |
| **State Space Complexity** | $\mathcal{O}(1)$ | $\mathcal{O}(K)$ |
| **Adaptability to Traffic Asymmetry** | Poor (Zero responsiveness to empty lanes) | High (Allocates time dynamically based on load) |
| **Starvation Prevention Mechanism** | Inherent via cyclic round-robin guarantee | Enforced via cumulative delay weight ($2 \times W$) |
| **Queue Dissipation Efficiency** | $\mathcal{O}(1)$ static throughput | Adaptive throughput up to $T_{\max} / T_{\min} = 5\times$ |
| **Average Vehicle Waiting Time** | High under burst/skewed arrivals | Low (Minimizes cumulative intersection delay) |

---

## 8. Theoretical Proofs & Invariants

### 8.1 Starvation-Freedom Theorem (Greedy Controller)

> **Theorem:** Under the Greedy Heuristic score `Priority(d) = 1.0 × C(d) + 2.0 × W(d)`, no approach $d$ with waiting vehicles can be starved of a green signal indefinitely.

**Proof Sketch:**
1. Suppose approach $d_0$ has at least one vehicle waiting ($C(d_0) \ge 1$) at time $t_0$.
2. For every elapsed second where approach $d_0$ is denied a green phase, the controller updates:  
   `wait_accum[d_0] = wait_accum[d_0] + Δt`
3. Therefore, average wait time $W(d_0)$ is a strictly monotonically increasing function of time:  
   $W(d_0) \to \infty$ as $t \to \infty$.
4. Since all competing approaches $d \ne d_0$ receive green phases of bounded maximum duration $T_{\max} \le 25.0\text{ s}$, and their wait timers reset to zero upon receiving green (`wait_accum[d] = 0`), their heuristic scores are bounded from above:  
   $P(d) \le (1.0 \times C_{\max}) + (2.0 \times 25.0) < \infty$.
5. Because $P(d_0)$ grows unbounded as time progresses while competing scores remain bounded, there exists a finite time $t' > t_0$ such that:  
   $P(d_0)(t') > P(d)(t')$ for all competing approaches $d \ne d_0$.
6. By the Greedy Choice Rule, approach $d_0$ is guaranteed selection at the next transition point. $\blacksquare$

---

### 8.2 Deadlock-Freedom & Mutual Exclusion Theorem

> **Theorem:** Vehicles never deadlock inside the intersection, and conflicting traffic movements never enter the intersection simultaneously.

**Proof Sketch:**
1. **Critical Section Definition:** The intersection square $I = [X_{\text{left}}, X_{\text{right}}] \times [Y_{\text{top}}, Y_{\text{bottom}}]$ constitutes a shared resource (critical section).
2. **Phase Mutual Exclusion:** In both Fixed-Time and Greedy modes, only one approach $d \in \text{DIRECTIONS}$ is assigned `STATE_GREEN` at any instant. All remaining approaches are assigned `STATE_RED`.
3. **Transition Clearance Invariant:** Between any two green phases for conflicting directions $d_i$ and $d_j$ ($i \ne j$), the controller enforces:  
   $T_{\text{clearance}} = T_{\text{yellow}} + T_{\text{all-red}} = 3.0\text{ s} + 1.0\text{ s} = 4.0\text{ s}$  
   Given road width $W_{\text{road}} = 120\text{ px}$ and base vehicle speed $v = 120\text{ px/s}$, the maximum clearance time required is:  
   $t_{\text{clear}} = \frac{W_{\text{road}} + L_{\text{car}}}{v} = \frac{120 + 30}{120} = 1.25\text{ s} < 4.0\text{ s}$
4. **Active Clearance Priority:** Vehicles that have crossed the stop line (`passed_stop_line = True`) ignore red transitions and retain movement priority until `is_past_intersection() = True`.
5. **Entry Guard:** Approaching vehicles check `is_intersection_clear()` prior to entry; if a crossing vehicle occupies $I$, approaching vehicles hold behind the stop line.
6. Since vehicles inside $I$ have zero conflicting obstacles ahead and move monotonically forward ($\Delta x \cdot \text{dx} > 0$ or $\Delta y \cdot \text{dy} > 0$), they must exit in finite time $\le 1.25\text{ s}$, clearing $I$ and releasing waiting vehicles. Hence, circular wait is impossible and the intersection is guaranteed **deadlock-free**. $\blacksquare$

---

## 9. Academic Project Metadata

- **Course:** Design and Analysis of Algorithms (DAA)
- **Project Domain:** Traffic Flow Modeling, Simulation, Heuristic Optimization & Scheduling
- **Programming Language:** Python 3 (Object-Oriented, modular architecture)
- **Visualization:** Pygame-CE (Canvas rasterization without pre-rendered assets)
- **Authors:** College DAA Mini-Project Team
- **License:** Educational & Academic Open Source
