# Traffic Signal Optimization Simulation
### A 2D Simulation of Fixed-Time and Greedy Adaptive Traffic Signal Control

## 1. Project Overview

The **Traffic Signal Optimization Simulation** is a two-dimensional, top-down traffic intersection simulation developed using Python 3 and Pygame-CE. It is designed as a Design and Analysis of Algorithms (DAA) mini-project to demonstrate and compare two traffic signal control strategies: Fixed-Time Round-Robin Scheduling and Greedy Adaptive Optimization.

The simulation models a four-way intersection with dynamically generated vehicles, realistic vehicle-following behavior, traffic signal transitions, and a graphical control panel. Users can observe how different signal scheduling strategies affect traffic queues, vehicle waiting times, and traffic flow under varying traffic conditions.

The primary objective is to demonstrate how algorithmic decision-making can improve traffic management when vehicle arrivals are uneven across different roads.

## 2. Key Features

### 2.1 Realistic 2D Intersection

- Four-way intersection with North, South, East, and West approaches.
- Dark asphalt roads, lane dividers, stop lines, sidewalks, and surrounding terrain.
- Traffic lights with red, yellow, and green states.
- Vehicles rendered using Pygame drawing primitives, without external graphical assets.

### 2.2 Vehicle Movement and Collision Avoidance

- Smooth vehicle movement using delta-time-based updates.
- Vehicle-following logic that maintains safe distances between consecutive vehicles.
- Automatic deceleration and stopping at red signals.
- Intersection exit detection and clearance handling.
- Entry checks to prevent conflicting traffic movements from entering an occupied intersection.

### 2.3 Dynamic Traffic Generation

- Independent vehicle generation for all four approaches.
- Adjustable vehicle arrival probability to simulate light and heavy traffic.
- Asymmetric traffic distributions, allowing one road to receive more traffic than another.
- Spawn-position clearance checks to prevent vehicles from overlapping when they appear.

### 2.4 Two Traffic Signal Control Algorithms

**Algorithm A: Fixed-Time Round-Robin**

The controller rotates through a predefined sequence:

North → South → East → West → North

Each approach receives a predetermined green duration, followed by yellow and all-red clearance intervals. This method is simple and predictable but does not respond to differences in traffic demand.

**Algorithm B: Greedy Adaptive Optimization**

The controller evaluates the traffic conditions at phase transitions and selects the next approach using a priority score:

Priority(d) = 1.0 × C(d) + 2.0 × W(d)

Where:

- C(d) is the number of vehicles waiting on approach d.
- W(d) is the average waiting time of the queued vehicles, measured in seconds.
- 1.0 and 2.0 are configurable weighting factors.

The controller favors approaches with longer queues and greater waiting times. Green duration is adjusted according to queue size, while waiting-time accumulation helps prevent approaches from being repeatedly overlooked.

### 2.5 Interactive Graphical User Interface

The control panel provides:

- Start, Pause/Resume, and Reset controls.
- Runtime selection between Fixed-Time and Greedy modes.
- Adjustable vehicle spawn rate.
- Adjustable baseline green duration.
- Simulation speed control.
- Live queue counts for all four approaches.
- Traffic light countdown timers.
- Waiting-time and starvation-related telemetry.

## 3. Software and Hardware Requirements

### Software Requirements

| Component | Requirement |
|---|---|
| Programming language | Python 3.9 or later |
| Graphics library | Pygame-CE 2.5.0 or later |
| Operating system | Windows, Linux, or macOS |
| Code editor | VS Code, PyCharm, or another Python IDE |
| Package manager | pip |

### Recommended Hardware

- Dual-core processor or better.
- At least 4 GB RAM.
- Standard display capable of rendering a 2D graphical application.

## 4. Installation and Execution

Open PowerShell or Command Prompt in the project directory.

```powershell
cd "C:\Users\DELL\OneDrive\Desktop\DAA Project\traffic_signal_simulation"
```

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install the dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the application:

```powershell
python main.py
```

If `pip` is unavailable, repair the Python installation or run:

```powershell
python -m ensurepip --upgrade
```

The project should start with the graphical intersection and its control panel.

## 5. GUI Controls

| Control | Function |
|---|---|
| Start | Starts vehicle movement and the simulation clock. |
| Pause/Resume | Freezes or resumes vehicle movement, signal timers, and simulation time. |
| Reset | Clears vehicles and restores the initial signal state. |
| Mode Selector | Switches between Fixed-Time and Greedy Adaptive control. |
| Spawn Rate | Controls the probability of vehicle arrivals. |
| Green Duration | Sets the baseline green duration. |
| Simulation Speed | Changes the simulation clock multiplier. |
| Queue Telemetry | Displays the number of waiting vehicles on each approach. |
| Countdown Timer | Displays the remaining time in the current signal phase. |

## 6. Project Architecture

```text
traffic_signal_simulation/
│
├── main.py
│   └── Main loop, GUI, event handling, and rendering
│
├── settings.py
│   └── Constants, dimensions, timings, and colors
│
├── vehicle.py
│   └── Vehicle movement, stopping, and following logic
│
├── traffic_light.py
│   └── Signal states and countdown display
│
├── intersection.py
│   └── Roads, lane markings, sidewalks, and stop lines
│
├── traffic_generator.py
│   └── Random vehicle arrivals and spawn safety checks
│
├── signal_controller.py
│   └── Fixed-Time and Greedy Adaptive algorithms
│
├── requirements.txt
│   └── Python package dependencies
│
├── Read.txt
│   └── Project notes and algorithm analysis
│
└── README.md
    └── Documentation and DAA analysis
```

## 7. Design and Analysis of Algorithms

### 7.1 Fixed-Time Round-Robin Scheduling

The Fixed-Time controller allocates a predetermined green interval to each approach in a cyclic order.

For four approaches, the sequence is:

North → South → East → West → North

Let:

- K be the number of approaches.
- Tgreen be the configured green duration.
- Tyellow be the yellow clearance duration.
- Tall-red be the all-red clearance duration.

The duration of a complete four-approach cycle is:

Tcycle = K × (Tgreen + Tyellow + Tall-red)

For K = 4, Tyellow = 3 seconds, and Tall-red = 1 second:

Tcycle = 4 × (Tgreen + 4)

The controller does not need to inspect queue lengths to choose its next approach. Therefore, its phase-selection time complexity is O(1), and its controller state requires O(1) auxiliary space for a fixed number of approaches.

**Advantages**

- Simple to implement and understand.
- Predictable signal scheduling.
- Low decision-making overhead.
- Provides a cyclic opportunity for every approach.

**Limitations**

- Allocates green time even when an approach has little or no traffic.
- Cannot respond directly to traffic imbalance.
- Can increase average waiting time under highly asymmetric arrivals.

### 7.2 Greedy Adaptive Optimization

The Greedy controller selects the next approach using a local priority calculation at each eligible phase transition.

Priority(d) = αC(d) + βW(d)

Where α = 1 and β = 2 in the default configuration.

The queue length represents immediate demand, while waiting time represents accumulated service delay. The waiting-time weight encourages the controller to serve approaches that have waited longer.

The controller selects the approach with the highest priority score. Ties are resolved deterministically using accumulated waiting time and a fixed direction order.

#### Adaptive Green Duration

The green duration is calculated using the queue length C:

- If C ≤ 2, green duration is 5 seconds.
- If C ≥ 8, green duration is 25 seconds.
- If 2 < C < 8, the duration is interpolated between 5 and 25 seconds.

For intermediate queues:

Tgreen = 5 + ((C − 2) / 6) × 20 seconds

This produces a bounded green duration between 5 and 25 seconds.

#### Starvation Prevention

The controller tracks waiting time for approaches that are denied service. This encourages the selection of neglected approaches even when other roads have larger queues.

A starvation metric should measure the elapsed time since an approach last received service, or the waiting time of its oldest queued vehicle. These measurements should be distinguished from the average waiting time used in the priority formula.

**Important:** A waiting-time score alone does not guarantee starvation freedom if queue counts are unbounded or if the controller continually resets waiting-time values before service. A strict guarantee requires explicit assumptions and a scheduling rule that ensures every continuously waiting approach receives service within a finite bound.

### 7.3 Complexity Analysis

Let:

- K = number of approaches.
- N = total number of active vehicles.
- Nd = number of vehicles on approach d.
- N = Σ Nd across all approaches.

#### A. Fixed-Time Phase Selection

The next phase is obtained through a cyclic index update:

```python
next_idx = (current_idx + 1) % K
```

| Case | Time Complexity |
|---|---|
| Best | O(1) |
| Average | O(1) |
| Worst | O(1) |

Auxiliary space: O(1).

#### B. Greedy Phase Selection

The controller calculates priority values for K approaches and selects the highest-ranked candidate.

If all approaches are sorted by priority, the complexity is:

| Case | Time Complexity |
|---|---|
| Best | O(K) with linear maximum selection |
| Average | O(K log K) if sorting is used |
| Worst | O(K log K) if sorting is used |

If K = 4, the selection overhead is effectively constant with respect to the number of vehicles N.

Auxiliary space is O(K) if priority values are stored in a temporary collection.

#### C. Countdown Calculation

Calculating the remaining time for one signal using arithmetic takes O(1). Calculating it for every approach takes O(K).

For four approaches, this is O(1) with respect to N.

#### D. Vehicle Sorting

Vehicles are sorted within each approach so that the leading vehicle can be processed first.

Using Python's Timsort:

- Best case: O(Nd) for an already ordered lane.
- Average case: typically O(Nd log Nd).
- Worst case: O(Nd log Nd).

Across all approaches, the upper bound is O(N log N) for K = 4.

More generally, if K is variable and vehicles are distributed evenly, the sorting cost is approximately O(N log(N/K)) across all lanes, excluding the case of empty lanes.

#### E. Vehicle Movement

Each vehicle performs a bounded amount of movement, speed, and headway calculation per frame.

Total time complexity: O(N).

#### F. Intersection Clearance Checks

If a vehicle checks every vehicle on perpendicular approaches to determine whether the intersection is occupied, the worst-case cost can be O(N).

A spatial grid or dedicated intersection-occupancy flag can reduce repeated clearance checks, depending on the implementation.

#### G. Vehicle Generation

Random arrival trials take O(K). If each attempted spawn checks all vehicles on the corresponding approach, clearance validation costs O(Nd) per attempted spawn.

The worst-case cost is O(K + ΣNd) = O(N + K) when each approach has at most one spawn attempt per frame.

#### H. Overall Per-Frame Complexity

Assuming the implementation sorts vehicle lists every frame and uses linear intersection clearance checks:

Tframe = O(N log N + N + K log K)

For a fixed four-way intersection:

**Worst-case time complexity: O(N log N).**

If vehicles are already ordered, the sorting cost may be closer to linear, giving O(N) per frame under the stated assumptions.

These bounds describe computational work per frame, not the number of frames required to clear traffic.

### 7.4 Space Complexity

The primary data structures include vehicle objects, lane lists, traffic-light objects, and controller state.

| Structure | Space Complexity |
|---|---|
| Vehicle storage | O(N) |
| Vehicle attributes | O(1) per vehicle |
| Traffic lights | O(K) |
| Waiting-time accumulators | O(K) |
| Temporary sorting storage | O(N) upper bound |
| Queue aggregation | O(N) if temporary lists are created |

Overall working space is:

S(N, K) = O(N + K)

For a fixed four-way intersection, this simplifies to **O(N)**.

## 8. Safety Properties and Algorithmic Invariants

### 8.1 Signal Exclusivity

At most one conflicting approach should be permitted to enter the intersection at any given time.

The controller must enforce the following transition sequence:

1. Terminate the current green phase.
2. Display yellow for the configured clearance interval.
3. Set all approaches to red during the all-red interval.
4. Activate the next green phase only after the clearance conditions are satisfied.

The all-red interval must be long enough for vehicles already inside the intersection to clear safely. A fixed interval alone is not a universal safety guarantee; the actual required time depends on vehicle speed, vehicle length, intersection geometry, and turning paths.

### 8.2 Intersection Clearance

Vehicles that have entered the intersection should be allowed to finish their movement safely, even if their approach subsequently changes from green to yellow or red.

Vehicles waiting at the stop line must not enter while a conflicting vehicle occupies the intersection.

For a simplified straight-through vehicle model, a lower-bound clearance estimate is:

Tclear ≥ (Wroad + Lcar) / v

Where Wroad is the intersection traversal distance, Lcar is vehicle length, and v is the vehicle's traversal speed.

For example, with Wroad = 120 pixels, Lcar = 30 pixels, and v = 120 pixels/second:

Tclear ≥ (120 + 30) / 120 = 1.25 seconds

This estimate applies only to the stated geometry and constant-speed assumptions. Turning movements, acceleration, and additional clearance margins may require more time.

### 8.3 Deadlock Prevention

To prevent vehicles from remaining permanently blocked inside the intersection:

- Vehicles must not enter when their exit path is blocked.
- Vehicles already inside must retain movement priority.
- The controller must avoid granting conflicting movements simultaneously.
- Entry checks must not prevent an already-entered vehicle from completing its movement.

Under these assumptions, a vehicle with an unobstructed exit path and positive forward speed can leave the intersection in finite time.

This is a conditional safety argument, not a universal proof of deadlock freedom for every possible traffic configuration.

### 8.4 Starvation-Freedom Considerations

Fixed-Time Round-Robin provides a bounded opportunity for every approach, provided that phase transitions continue and each phase has a finite duration.

The Greedy controller uses queue length and waiting time to prioritize demand. However, a strict starvation-freedom theorem requires a bounded scheduling policy or an explicit aging rule with suitable bounds on competing demand.

A robust implementation can impose a maximum waiting-time threshold: if an approach exceeds the threshold, it must be selected at the next eligible transition, subject to safe clearance.

This guarantees a bounded opportunity for service when the controller continues operating and the clearance protocol terminates.

## 9. Performance Comparison

| Metric | Fixed-Time Round-Robin | Greedy Adaptive |
|---|---|---|
| Scheduling strategy | Cyclic | Priority-based |
| Phase selection | O(1) | O(K) with linear maximum selection |
| Queue awareness | No | Yes |
| Adaptive green duration | No | Yes |
| Predictability | High | Depends on traffic demand |
| Response to asymmetric traffic | Limited | Better suited to uneven queues |
| Starvation handling | Cyclic service opportunity | Requires a validated aging or maximum-wait rule |
| Controller state | O(1) | O(K) |
| Vehicle simulation cost | Shared by both modes | Shared by both modes |

The Greedy approach is expected to perform better when traffic demand is uneven, but this is a hypothesis to be evaluated experimentally rather than a guaranteed outcome for every traffic pattern.

## 10. Experimental Evaluation

To compare both algorithms fairly, run each mode with the same simulation duration, initial conditions, and traffic arrival settings.

Record the following metrics:

1. Average vehicle waiting time.
2. Maximum waiting time.
3. Average and maximum queue length per approach.
4. Total vehicles that successfully exit the intersection.
5. Throughput, measured as vehicles exiting per unit of simulation time.
6. Number of vehicles still waiting at the end of the run.
7. Maximum time an approach remains without service.

Perform experiments under at least three traffic conditions:

- Uniform traffic: similar arrival rates on all approaches.
- Asymmetric traffic: one approach receives significantly more vehicles.
- Burst traffic: one or more approaches experience temporary arrival spikes.

Use multiple runs with different random seeds where possible. Report averages and variability instead of drawing conclusions from a single simulation run.

## 11. Limitations and Future Enhancements

### Current Scope

- Simplified four-way intersection geometry.
- Straight-through vehicle movements unless turning logic is implemented.
- Stochastic traffic arrivals.
- Heuristic-based adaptive signal control.
- Simulated rather than real-world traffic conditions.

### Future Enhancements

- Support for left and right turns.
- Emergency vehicle priority.
- Pedestrian crossing signals.
- More advanced scheduling algorithms, such as Max-Pressure control.
- CSV export of performance metrics.
- Side-by-side experimental comparison of both controllers.
- Improved collision detection and lane-change behavior.
- Adaptive control calibrated against measured traffic data.

## 12. Academic Project Metadata

**Project Title:** Traffic Signal Optimization Simulation

**Course:** Design and Analysis of Algorithms (DAA)

**Project Domain:** Traffic Flow Simulation, Scheduling, Greedy Algorithms, and Algorithm Analysis

**Programming Language:** Python 3

**Graphics Framework:** Pygame-CE

**Architecture:** Modular, object-oriented design

**Project Type:** College Mini-Project

**License:** Educational and Academic Use

## Conclusion

The Traffic Signal Optimization Simulation demonstrates how different scheduling strategies influence traffic movement at a four-way intersection. Fixed-Time Round-Robin provides a simple and predictable scheduling baseline, while Greedy Adaptive Optimization uses queue length and waiting time to respond to changing traffic demand.

By comparing these approaches under controlled traffic conditions, the project illustrates algorithm selection, complexity analysis, simulation design, and the importance of evaluating practical performance alongside theoretical efficiency.

The project also highlights an important engineering principle: a traffic controller must balance efficiency, fairness, and safety. Adaptive scheduling is useful only when its decisions are evaluated alongside starvation prevention, intersection clearance, and vehicle movement constraints.
