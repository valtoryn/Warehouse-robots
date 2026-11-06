# R05 — Simulation, Digital Twins and the Reality Gap
> **Status:** Research document — proposed findings, nothing here is implemented.
> **Workstream:** R05 · **Last verified:** 2026-11-07 · **Evidence legend:** see below

## Evidence legend

- **[FACT]** established by a cited source (always followed by a source ID such as [R05-S01]).
- **[CALC]** derived by a shown calculation from cited or labelled inputs.
- **[EST]** engineering estimate or assumption (basis stated).
- **[REC]** Valtoryn recommendation or proposal (engineering judgement, not established fact).
- **[UNRESOLVED]** could not be established; what would resolve it is stated.

No Valtoryn software, simulator model, or hardware exists yet. Every statement about what Valtoryn "should" do is a proposal. No hardware was tested, and no simulator was run, by this research; all simulator statements below come from documentation, source repositories, or papers that were opened and read.

---

## 1. Scope and method

**Question.** How can the Valtoryn platform simulate real robot behaviour with defensible fidelity, what can a simulation legitimately claim, and what must be measured on hardware before a simulated result may be believed?

**Method.** Official documentation was read first (Gazebo Sim / SDFormat / gz-sensors API pages, ROS 2 control and Nav2 documentation, vendor repositories), then standards-body catalogue pages and public previews, then peer-reviewed or arXiv papers. Pages were fetched through web-fetch tools; where a fetch returned only part of a page, that is stated. Secondary summaries and search snippets were not cited. Several pages could not be read (see "Sources that could not be inspected"). Version-sensitive facts (Gazebo releases) were checked against the live Gazebo release page on the access date.

**Interpretation caveat.** Some pages were summarised by the fetch tool's extraction model rather than read verbatim. Parameter names, defaults and units reported below are as extracted from the official page; they should be re-checked against the pinned simulator version when Valtoryn adopts one.

**Not covered.** Safety certification content (R08), fleet orchestration (R-series fleet work), and hardware selection are referenced only where they constrain simulation claims.

---

## 2. Summary of key findings

1. Gazebo Sim loads DART by default; Bullet and Bullet-Featherstone are described as "preliminary support" in the current docs, and the docs state that DART supports every listed engine configuration option [FACT, R05-S01]. For the reference differential-drive AMR, DART is the lowest-risk starting point, but nothing read establishes its fidelity for wheeled contact.
2. Friction in the SDF specification is expressed as a **friction pyramid** with `mu`, `mu2`, `fdir1`, and force-dependent slip `slip1`/`slip2` (units m/s/N) [FACT, R05-S07]. ODE's own guide states that ODE approximates the friction cone for efficiency [FACT, R05-S14]. Whether DART honours these ODE/Bullet-labelled elements identically is not documented in the pages read [UNRESOLVED].
3. The Gazebo `WheelSlip` system is a slip-compliance wrapper around the friction model with a user-supplied constant `wheel_normal_force`; it assumes `fdir1` is parallel to the joint axis [FACT, R05-S02]. It is not a tyre model, and it does not obviously track payload-dependent normal force [UNRESOLVED / EST].
4. `gz_ros2_control` documents effort, velocity and position command interfaces only; it says nothing about motor dynamics, gearboxes or current limits, and warns that velocity commands applied instantly can cause wheel slip and odometry error [FACT, R05-S18]. Motor, drive, current-limit and backlash behaviour therefore must be added by Valtoryn [REC].
5. Gazebo's battery system is a constant-power-load model with optional linear open-circuit-voltage and internal resistance; its own known-issues list says consumption should depend on torque but does not [FACT, R05-S04].
6. Gazebo actors "do not physically interact" with the simulation; they are visible to cameras and detectable by GPU-based sensors only [FACT, R05-S29]. They cannot test contact, pushing, or collision-response behaviour.
7. An open Gazebo issue (opened 2026-02-24) reports run-to-run divergence of identical simulations at the metre scale in a gz-sim 9 build; no maintainer response was visible [FACT that it is reported; the underlying cause is UNRESOLVED] [R05-S31]. Bitwise reproducibility must not be assumed; statistical regression gates are safer [REC].
8. ISO 23247-1's definition of a digital twin requires **synchronisation** between the element and its digital representation, and "fit for purpose" fidelity [FACT, R05-S44]. A simulator without a synchronisation path is a simulation model, not a digital twin [REC].
9. NASA-STD-7009B provides a public, credible vocabulary for what "validated" means (referent data, domain of validation vs domain of operation, overlapping uncertainty intervals, levels 0 to 4) that maps naturally onto the evidence levels proposed in Section 7 [FACT, R05-S47].
10. The reality-gap literature found is dominated by manipulation and legged RL work, not warehouse AMRs; the transferable lessons are that actuator models, latency and parameter uncertainty dominate, and that randomisation alone can fail when the gap is large [FACT, R05-S51, R05-S53].

---

## 3. Findings

### 3.1 Release baseline and physics engines in Gazebo

**Release status (verified 2026-11-07).** The Gazebo release page lists Jetty (Sep 2025, LTS, end of life May 2031), Ionic (Sep 2024, end of life Dec 2026), Harmonic (Sep 2023, LTS, end of life May 2029), Fortress (LTS, end of life May 2027), release "M" (planned Mar 2027), and a rolling "Rotary" stream marked experimental [FACT, R05-S05]. Library APIs follow semantic versioning with ABI considered part of the interface [FACT, R05-S05].

**Engine availability.** Gazebo Sim selects the physics engine at runtime through the Gazebo Physics abstraction layer; DART is the default. The docs list the DART plugin as primary and "preliminary support" for Bullet and Bullet-Featherstone plugins [FACT, R05-S01]. The gz-physics README describes dartsim as the reference implementation and TPE as an engine focused on fast kinematics of large environments, but states no per-engine maturity level [FACT, R05-S11].

**DART options.** The documented SDF engine configuration is `//physics/dart/collision_detector` (ode default; bullet, fcl, dart) and `//physics/dart/solver/solver_type` (dantzig default; pgs). The docs state these options are available to all engines in principle but not all engines may support them, and that DART supports all of them [FACT, R05-S01].

**DART numerics.** DART's documentation describes use of generalised coordinates for articulated rigid bodies and Featherstone's Articulated Body Algorithm [FACT, R05-S42]. The site documents the DART 6 compatibility line (6.19.5 released 2026-10-04); which DART major version the pinned Gazebo release links against was not established [UNRESOLVED].

**Bullet-Featherstone.** The Ionic announcement (2024-09-30) lists improvements: nested models, off-diagonal inertia, enforced joint velocity and effort limits, configurable solver iterations, auto-deactivation, and convex-hull use for decomposed meshes [FACT, R05-S12]. The announcement states no remaining limitations; absence of a list is not evidence of absence [EST].

| Engine in Gazebo Sim | Status per docs read | Relevant documented options | Gap for Valtoryn |
|---|---|---|---|
| DART (default) | Primary; supports all documented options [R05-S01] | Collision detector: ode/bullet/fcl/dart; solver: dantzig/pgs [R05-S01] | Wheel-ground contact fidelity not documented [UNRESOLVED] |
| Bullet | "Preliminary support" [R05-S01] | None documented in pages read | Maturity unknown |
| Bullet-Featherstone | "Preliminary support" [R05-S01]; 2024 feature additions [R05-S12] | Joint effort/velocity limits enforced; solver iterations [R05-S12] | An open issue about a joint velocity controller not disengaging exists in search results but was not inspected |
| TPE | Kinematics-focused [R05-S11] | n/a | Not a dynamics engine for contact fidelity |

### 3.2 Contact, friction and wheel-ground interaction

**SDF friction model.** The collision `<surface><friction>` block provides, for ODE: `mu` and `mu2` (unitless, default 1, described as friction coefficients in the first and second friction-pyramid directions), `fdir1` (first pyramid direction in the collision frame), `slip1`/`slip2` (force-dependent slip, m/s/N, default 0). For Bullet: `friction`, `friction2`, `fdir1`, and `rolling_friction` (default 1, no unit stated). It also provides torsional friction (`coefficient`, `patch_radius`, `surface_radius`, ode `slip` in rad/s/(N m)) [FACT, R05-S07]. The page uses "friction pyramid" throughout and does not mention a cone.

**Contact stiffness parameters.** `<contact>` offers `max_vel`, `min_depth`, `soft_cfm`, `soft_erp`, `kp`, `kd` and similar, with defaults including `kp` 1e12 and `max_contacts` default 20 per entity pair at the world physics level [FACT, R05-S07, R05-S08]. No units are stated for several of these [FACT, R05-S07].

**Pyramid versus cone.** ODE's user guide states that ODE approximates the Coulomb friction cone for efficiency, offering a constant force limit mode (`mu` is an absolute tangential limit, independent of normal force) or a pyramid mode in which limits are `mu` times the normal force; the guide also states that ODE's integrator is first-order and inaccurate unless the step is small [FACT, R05-S14]. MuJoCo, by contrast, documents both elliptic and pyramidal cones as solver-dependent choices [FACT, R05-S41].

**Implication.** Friction anisotropy in simulation can be an artifact of pyramid discretisation and of `fdir1` alignment: ODE's guide warns that when `fdir1` is not set the orientation is computed automatically and is unpredictable [FACT, R05-S14]. A wheel with a rolling direction different from the pyramid axes can therefore see direction-dependent friction in simulation. [EST] This should be tested explicitly (Section 8, dimension F7).

**WheelSlip system.** The system updates slip parameters from linear wheel spin velocity (radius times spin rate). The documentation states that `fdir1` is assumed parallel to the joint axis and the link origin is assumed on the joint axis. `slip_compliance_lateral/longitudinal` are unitless slip-ratio to tangential-force-ratio parameters; at each step they are multiplied by wheel linear speed and divided by the configured `wheel_normal_force` to match slip units; the maximum force ratio is the friction coefficient [FACT, R05-S02]. The documentation's example uses constant per-wheel normal forces of 100 N and 80 N and a 0.1651 m radius [FACT, R05-S02].

[CALC] With the documentation's example compliance 0.1, normal force 100 N, radius 0.1651 m, and a hypothetical wheel speed of 10 rad/s: linear speed = 0.1651 × 10 = 1.651 m/s; slip = 0.1 × 1.651 / 100 = 0.001651 m/s/N. If the true normal force were 150 N but 100 N is configured, the slip response is scaled by 1.5 relative to the intended physical model (same formula, N in the denominator). Whether `wheel_normal_force` is updated dynamically from simulated load is not stated [UNRESOLVED; resolve by reading the system source in the pinned gz-sim version].

**Documented limits.** (a) WheelSlip depends on the `fdir1`/joint-axis alignment assumption [R05-S02]. (b) The SDF joint block exposes a single `friction` value ("static friction") and `damping`; there is no separate Coulomb/Stribeck/stiction curve and no backlash element [FACT, R05-S09]. (c) The `gz_ros2_control` page warns that velocity commands applied directly to wheel joints can cause slip and odometry error [FACT, R05-S18].

### 3.3 Wheel dynamics and motor models

**What Gazebo/ros2_control provides.** The `gz_ros2_control` plugin (`gz_ros2_control/GazeboSimSystem`) exposes effort, velocity and position command interfaces and effort/velocity/position state interfaces on joints. Effort is applied directly as joint force/torque; velocity is applied directly as joint velocity; position is realised as a velocity command equal to a proportional gain times position error times the controller-manager rate, which the page analyses as a discrete first-order system (gain should not exceed 2 for stability and 1 to avoid oscillation). The page documents no motor model, gearbox model, or current/torque-speed limit. A demo `GazeboCustomSimSystem` shows a configurable low-pass filter on a velocity command interface as an example of custom actuator dynamics [FACT, R05-S18]. The Gazebo `DiffDrive` system takes wheel separation (default 1.0 m), wheel radius (default 0.2 m) and optional velocity, acceleration and jerk limits, and publishes odometry at 50 Hz by default; the page does not describe odometry noise or slip [FACT, R05-S03].

**A permanent-magnet DC motor model (proposed plant for Valtoryn).** The standard lumped model is:

- Electrical: V = R·I + L·dI/dt + K_e·ω
- Torque: T_m = K_t·I
- Mechanical: J·dω/dt = T_m − T_load − b·ω − T_coulomb·sign(ω)
- Steady state: ω_no-load = V / K_e; T_stall = K_t·V / R

A Texas Instruments application report documents that torque and voltage constants take the same numerical value in SI units, models the back-EMF as ω times that constant, and treats the motor as an electromechanical transformer with rotor and load inertia J [FACT, R05-S57]. The remaining equations are textbook form and are labelled [CALC] derivations from that model, not independently sourced.

[CALC, hypothetical inputs, illustration only] For V = 24 V, K = 0.05 N·m/A, R = 0.5 Ω: T_stall = 0.05 × 24 / 0.5 = 2.4 N·m; ω_no-load = 24 / 0.05 = 480 rad/s ≈ 4584 rpm. These numbers are not Valtoryn parameters.

**Terms a Gazebo-only model omits (and Valtoryn would need) [REC]:**

| Effect | Where Gazebo/ros2_control stands (docs read) | Proposed handling |
|---|---|---|
| Supply voltage sag / bus limit | Battery system has optional internal resistance [R05-S04]; no documented link to motor voltage | Motor model reads simulated bus voltage |
| Current limit / torque limit | Joint `<limit><effort>` exists, not enforced if negative [R05-S09]; interface min/max shown in the control example but behaviour not explained [R05-S18] | Explicit current-limit in drive model, then torque = K_t·I |
| Gearbox efficiency, backlash | No backlash element in SDF joint [R05-S09] | Custom `SystemInterface` with backlash/efficiency parameters, identified from hardware |
| Drive control loop and quantisation | Not modelled | Emulate the drive's real velocity loop rate and encoder resolution |
| Thermal derating | Not mentioned | Out of scope until hardware thermal data exists |

**Wheel torque requirement.** The MiR100 battery study gives the vehicle motion-resistance decomposition F_res = F_A + F_G + F_R + F_I (air, gradient, rolling, inertial) and identifies mass, velocity and acceleration as the variables that couple payload into energy use [FACT, R05-S58]. [CALC] Per-driven-wheel torque follows T_wheel = F_res · r_wheel / n_driven (ignoring drivetrain losses), so required motor current scales with total mass: this is the mechanism by which payload enters both the motor model and the battery model.

### 3.4 Payload-dependent dynamics

SDF represents a link's inertial properties as mass, a centre-of-mass pose, and a six-component inertia tensor about the centre of mass; the page gives no units [FACT, R05-S10]. A payload that changes between missions changes at least: total mass, combined centre of mass, combined inertia, per-wheel normal force, rolling resistance, and braking distance [EST, derived from rigid-body mechanics]. Webots documents a comparable structure (mass, `centerOfMass`, `inertiaMatrix` with principal moments and products of inertia) [FACT, R05-S39]. Isaac Sim documents that unset mass is estimated from mesh volume at a default density of 1000 kg/m³ and recommends setting mass, centre of mass and inertia to real-world values [FACT, R05-S37].

[REC] Model payloads as separate rigid bodies rigidly (or compliantly) attached to the chassis, parameterised by mass, COM offset and inertia from a payload manifest, rather than editing the chassis inertia. Per-wheel normal force should be recomputed from payload COM and passed to any wheel-slip configuration. Load-dependent friction (tyre deflection, caster behaviour) has no documented Gazebo representation in the pages read and must be identified from hardware [UNRESOLVED].

Empirical hint for energy: in the MiR100 study (payload 0/50/100 kg, missions of 30/140/350 m, two NMC batteries of 39.6 Ah), the four effects retained in the final regression were turns, distance, state of charge, and state-of-charge × distance; the authors do not retain payload among those four [FACT, R05-S58]. This is one robot, one battery chemistry and two units; it must not be generalised to Valtoryn [EST].

### 3.5 Sensor models, noise and latency

**Noise models in gz-sensors / SDF.**

| Sensor | Documented noise | Source |
|---|---|---|
| Generic (pressure, air speed, altimeter, force-torque) | `type` none / gaussian / gaussian_quantized; mean, stddev, bias_mean, bias_stddev, dynamic_bias_stddev, dynamic_bias_correlation_time (typical value given as about 3600 s), precision (quantisation) | [R05-S06] |
| IMU | Per-axis noise on angular velocity and linear acceleration with the same parameter set (none/gaussian/gaussian_quantized, biases, dynamic bias) | [R05-S06] |
| Lidar | `type` gaussian only; mean and stddev; noise drawn independently per beam | [R05-S06] |
| Camera | gaussian only (per-pixel) | [R05-S06] |

The API reference shows a `Noise` base class with `Apply(value, dt)` and a hook to register a custom noise callback, and a `GaussianNoiseModel` exposing mean, standard deviation and bias [FACT, R05-S16, R05-S17]. The gz-sensors tutorial notes `update_rate`, that "not all the tags are supported for all sensors yet", and that the lidar example (`gpu_lidar`) requires the sensors system with a render engine (ogre2) [FACT, R05-S15].

**What the documentation does not show.** (a) No sensor latency or lag element was found in the first 200,000 of about 230,000 characters of the SDF sensor specification (the last 30,000 characters were not read) [FACT/limit, R05-S06]. (b) Correlated beam noise, range-dependent noise, reflectivity-dependent dropout and mixed-pixel effects are not described in the lidar section read [UNRESOLVED; resolve by reading the gz-sensors source for the pinned release]. (c) Timestamping semantics between sensor generation and bridge publication are not documented in the pages read [UNRESOLVED].

**Implication.** Documented lidar noise is an independent Gaussian per beam; real lidar error is typically structured by surface type, incidence angle and range [EST, general sensor knowledge; not sourced here]. A lidar-based localisation test passing in simulation under i.i.d. noise establishes little about performance with structured error [EST].

[REC] Treat latency as a first-class injected quantity outside the simulator: a configurable delay-and-jitter stage between sensor output and the autonomy stack, and between controller output and actuator input, with distributions measured on hardware. The Tan et al. quadruped paper explicitly lists an accurate actuator model and simulated latency among its simulator improvements [FACT, R05-S51].

### 3.6 Localisation uncertainty

Nav2's AMCL documents odometry-noise parameters alpha1 to alpha5 (all defaulting to 0.2; alpha5 for omni models only), laser model selection (`beam`, `likelihood_field` default, `likelihood_field_prob`) with mixture weights `z_hit` and `z_rand` (default 0.5 each), `sigma_hit` default 0.2, `max_beams` default 60, particle count 500 to 2000, and update thresholds `update_min_d` 0.25 and `update_min_a` 0.2 [FACT, R05-S19].

Two points follow. First, these are the filter's **assumed** noise parameters, not the simulator's true noise; if the simulator's odometry is noise-free (the DiffDrive page mentions no odometry noise [R05-S03]), AMCL may converge in simulation with tuning that would be over-confident on hardware [EST]. Second, tuning alpha and laser parameters in simulation and carrying them to hardware without re-measurement imports the simulator's error model into the estimator [EST].

[REC] Evaluate localisation with a consistency metric (e.g., normalised estimation error squared against ground truth) rather than only mean position error, and calibrate the simulator's odometry and lidar error to hardware logs before tuning the estimator.

### 3.7 Battery behaviour

**Gazebo battery system.** One battery per model is supported; on full drain all joints of the model are turned off (joint forces set to zero). The "perfect battery" has constant voltage and no internal resistance. Documented SDF parameters include `voltage`, `open_circuit_voltage_constant_coef`, `capacity` (Ah), `power_load` (W), `start_draining`, and, for a "more realistic" battery, `open_circuit_voltage_linear_coef`, `initial_charge`, `resistance` and `smooth_current_tau`. Recharging is optional (`enable_recharge`, `charging_time`, start/stop services). Other systems can be consumers through a `BatteryPowerLoad` component. A documented known issue: without `fix_issue_225` the battery drains 100 times faster; and under Known Issues, consumption should be affected by torque (uphill versus downhill) but is not [FACT, R05-S04]. The docs give the runtime formula capacity × voltage / power_load [FACT, R05-S04].

[CALC, hypothetical inputs] 40 Ah × 24 V / 240 W = 4 h; without the fix the same configuration would drain 100× faster, giving 4 h / 100 = 2.4 min [formula from R05-S04; inputs invented for illustration].

**Literature.** The MiR100 study measured full discharge cycles of 39.6 Ah lithium NMC packs (about 16 h per charge/discharge cycle, at least two cycles per configuration), fitted a multivariate regression, and reported adjusted R² above 0.95 for a four-effect model; about half of observations were predicted within 0.1 percentage points of capacity and under 2% of observations had residuals above 0.5 points; the authors note that two batteries are not enough to conclude ageing does not matter [FACT, R05-S58].

**Implication.** The Gazebo battery is adequate for exercising a low-battery behaviour path (return to dock, task rejection) but not for predicting runtime or voltage sag under realistic loads without Valtoryn-supplied power models [EST]. [REC] Drive the battery with a power-load computed from the motor/drive model (I·V) plus compute and sensor base loads, calibrate against measured discharge on hardware, and record state-of-charge-dependent behaviour separately from the mission-level energy model.

### 3.8 Communication failures and latency injection

**DDS QoS (ROS 2).** From the ROS 2 documentation source (rst, Jazzy branch): policies are history (keep last/all), depth, reliability (reliable/best effort), durability (transient local/volatile), deadline, lifespan, liveliness and lease duration. Defaults for ordinary publishers/subscribers are keep-last depth 10, reliable, volatile; sensor-data profile is best effort with a smaller queue; compatibility rules include that a best-effort publisher is incompatible with a reliable subscription and a volatile publisher is incompatible with a transient-local subscription [FACT, R05-S21]. An older design article (written Oct 2015, last modified May 2019, marked work in progress) describes the same core policies [FACT, R05-S22].

**Network emulation.** `tc-netem` (iproute2) is a Linux qdisc that can add delay (fixed, jitter, correlation, and uniform/normal/pareto/paretonormal distributions), packet loss (random, 4-state Markov, Gilbert-Elliot burst model), duplication, corruption, reordering and rate limiting. Documented limits: kernel timer granularity affects delay and rate accuracy; reordering requires delay larger than the inter-packet time; realistic TCP tests should place netem on the receiver ingress; combining with other qdiscs may not work; correlation is documented as an approximation, not true statistical correlation [FACT, R05-S20].

[REC] (1) Test each robot-to-fleet and inter-process QoS pair for compatibility under outage scenarios (best-effort versus reliable, deadline misses, liveliness loss) as scenario tests. (2) Build channel profiles (delay distribution, loss burst model, outage durations) from measured site Wi-Fi traces once hardware exists, and replay with netem. Until traces exist, any profile is an assumption and results are "simulated, unvalidated". (3) Whether tc/netem is available in Valtoryn's CI environments (including Windows-hosted developers) was not established [UNRESOLVED].

### 3.9 Dynamic obstacles and actors

Gazebo actors support skeleton animation (COLLADA, BVH) and scripted trajectories with waypoints, but are not subject to forces: no gravity, contact, or collision; they are visible to RGB cameras and detectable by GPU-based sensors [FACT, R05-S29]. They are therefore adequate for perception-side and path-planning avoidance tests (a pedestrian-like object crossing a lidar field) but cannot push a robot, trigger a contact sensor, or exercise collision response [FACT/inference, R05-S29].

The Open-RMF airport terminal demo provides an optional crowd simulation (`use_crowdsim:=1`) [FACT, R05-S26]; its fidelity to human behaviour was not assessed [UNRESOLVED].

[REC] Use actors for perception tests; use ordinary dynamic bodies driven by velocity controllers for any scenario in which physical contact is part of the pass/fail question; label the human-behaviour model (scripted, replayed from recorded trajectories, or stochastic) in the scenario definition.

### 3.10 Warehouse environments and licences

| Asset | What was verified | Licence evidence | Status / caution |
|---|---|---|---|
| AWS RoboMaker small warehouse world | Repo described as a Gazebo world for warehouse and logistics testing; archived and read-only; notice that AWS RoboMaker reached end of support on 2025-09-10, no maintainers, "Do not use this code in production", dependencies outdated and unpatched [R05-S23] | The `ros2`-branch LICENSE file begins with an Amazon copyright line and standard MIT-style wording; whether this is MIT or MIT-0 was not established from an inspected page [R05-S24] | Compatibility with current Gazebo Sim (gz) not established [UNRESOLVED]. Third-party asset licences within the world not addressed on the repo page [R05-S23] |
| Same package in ROS index | Package version 1.0.5 listed for humble, jazzy, kilted, lyrical, rolling; "Last Updated 2021-12-15" displayed; page itself does not state licence terms [R05-S25] | See above | The index page may be stale |
| Gazebo Fuel (model/world hosting) | Client defaults to fuel.gazebosim.org; `gz fuel list/download/upload/configure` documented [R05-S27]; Gazebo docs describe Fuel as hosting hundreds of models [R05-S28] | Neither page documents model licences; licence is evidently per model [UNRESOLVED] | Check licence of every Fuel asset individually before redistribution |
| Open-RMF demo worlds | Hotel, Office, Airport Terminal, Clinic, Campus, Manufacturing & Logistics, traffic-light scenarios; Apache-2.0 repo licence [R05-S26] | Repo licence Apache-2.0; asset licences inside worlds not checked | Tested on Gazebo Ionic with ROS 2 Kilted per README [R05-S26]; Ionic EOL is Dec 2026 [R05-S05]; compatibility with Jetty LTS [UNRESOLVED] |

[REC] Do not depend on third-party warehouse worlds for any claim stronger than "simulated, generic environment". Author a Valtoryn reference warehouse world from the intended deployment survey (aisle widths, rack geometry, floor markings, ramp/threshold geometry) under a licence Valtoryn controls, and treat third-party worlds as optional extras with their licence recorded per asset.

### 3.11 Multi-robot interaction, scalability and headless operation

**Run controls.** `gz sim -s` runs the server only (headless); `-r` starts running on launch; `--iterations N` bounds a run; `-z` sets update rate in Hz; `--seed` sets the random seed; `--initial-sim-time`; `--record`/`--playback` log and replay states; `--levels` and `--network-role primary|secondary` with `--network-secondaries N` support distributed simulation; `--physics-engine` selects the engine; `--headless-rendering` renders sensors without a display [FACT, R05-S30]. The Gazebo ROS 2 launch guidance documents `gz_server.launch.py` for server-only launch and states that publishing `/clock` and setting `use_sim_time` consistently is essential for the controller manager [FACT, R05-S34]. On Windows, the combined `gz sim` command is documented as not yet working; server and GUI must be run in separate processes [FACT, R05-S33].

**World stepping parameters.** SDF `<physics>` defaults: `max_step_size` 0.001 s, `real_time_factor` 1 (target), `real_time_update_rate` 1000 Hz, `max_contacts` 20 [FACT, R05-S08]. [CALC] At the defaults, 1/0.001 = 1000 physics steps per simulated second; with a real-time factor of 1 that is 1000 steps per wall-clock second, and this is the per-step budget (1 ms) that all systems and sensors must fit within to hold RTF=1 [EST for the budget interpretation].

**Measured scaling.** No measured real-time-factor versus robot-count data were found in the pages read. The Open-RMF README does not mention performance or hardware requirements [FACT, R05-S26], and the Gazebo tutorials index lists no performance or determinism tutorial [FACT, R05-S60]. A community report of crashes when running some RMF demos exists in search results but was not inspected. Scaling behaviour is therefore [UNRESOLVED] and must be measured in Valtoryn's own CI.

**Multi-robot interaction fidelity.** Open-RMF demos provide multi-fleet scenarios (for example, hotel with 3 fleets and 4 robots; office with two robots using full control and traffic-light modes) [FACT, R05-S26]. These demonstrate traffic management logic, not validated robot-robot physical interaction fidelity.

### 3.12 Determinism and reproducibility

- Gazebo Sim exposes `--seed` for the random number generator [FACT, R05-S30]. The Gazebo Classic tutorial states that without an explicit seed the generator is seeded from the process ID and that a seed yields a repeatable random sequence; that tutorial predates Gazebo Sim and does not say which components consume the generator [FACT, R05-S32]. Which sensor and plugin noise sources use this seed in the pinned release is [UNRESOLVED].
- Issue gz-sim #3349 (opened 2026-02-24, still open, labelled bug, status Inbox, no maintainer comments visible at read time) reports identical SDF, commands and step counts (a 1 kg box under a constant wrench, 4688 steps of 0.001 s) in separate `gz sim` processes giving final positions that differed by metres to tens of metres; a follow-up in September 2026 reported about 1 m variation across five runs and that pausing or disabling ASLR did not remove it. The build was gz-sim 9 from source with a coverage build type, and the physics engine was not named by the reporter [FACT as to the report; unverified independently, one reporter plus one follow-up] [R05-S31]. Treat as a warning, not a diagnosis.
- Isaac Sim documents that its full experience enables fixed-time-stepping by default so that scripted workflows "step the timeline deterministically" while GUI-oriented experiences default to variable stepping [FACT, R05-S37].

[REC] Define reproducibility as a measured property, not an assumption: run each regression scenario N times with a fixed seed and fixed step, and set pass/fail on distributional statistics (mean and spread of the metric of interest) rather than on a single run; separately track the run-to-run spread as a quality metric of the simulation stack (Section 8, dimension F1).

### 3.13 Alternative simulators (documented capability and licence only)

| Simulator | Licence (from repo page) | Physics (from docs read) | Sensors / ROS (from docs read) | Notes / unknowns |
|---|---|---|---|---|
| Gazebo Sim | Apache-2.0 (gz-sim, gz-physics) [R05-S33, R05-S11] | DART default; Bullet, Bullet-Featherstone preliminary [R05-S01] | Noise models Gaussian/bias/quantised [R05-S06]; ROS 2 via ros_gz [R05-S34] | Open determinism issue [R05-S31]; Windows combined launch not working [R05-S33] |
| NVIDIA Isaac Sim | Apache-2.0 per repo badge; first build prompts acceptance of Omniverse licensing terms [R05-S35] | Default PhysX backend, experimental Newton backend [R05-S36]; friction guidance: coefficient "should not exceed 1.0 in most cases", combine modes [R05-S37] | "RTX and physics-based sensors", ROS bridge [R05-S35] | README lists minimum GPU RTX 4080 for local workstation [R05-S35]; determinism doc: fixed stepping default for SimulationApp [R05-S37]; friction/solver detail not in pages read |
| Webots | Apache-2.0 [R05-S38] | ODE referenced in Physics node docs; contact properties via ContactProperties nodes; inertiaMatrix passed to ODE mass setter [R05-S39] | Lidar/camera visualisation noted in README [R05-S38] | Latest release not shown on page read |
| MuJoCo | Apache-2.0 code, CC BY 4.0 docs [R05-S40] | Soft constraints; elliptic or pyramidal friction cones; hard limit not allowed (R to 0) [R05-S41] | Physics library; no robot-sensor suite documented in README [R05-S40] | "Not an officially supported Google product" per README [R05-S40] |

[EST] MuJoCo's soft-contact formulation and Isaac Sim's GPU physics each trade strict physical exactness for stability or throughput; the MuJoCo authors explicitly argue their convex relaxation is a different approximation to reality rather than an LCP-exact one [FACT, R05-S41]. No published, controlled comparison on wheeled-robot ground contact was found among the sources read; the one comparison paper read concerns a manipulator arm with motion capture (Collins et al.) [FACT, R05-S52]; the user-feedback survey of dynamics simulators (Ivaldi et al.) notes that objective quantitative comparison is hard because most tools are not open source [FACT, R05-S55].

### 3.14 The digital twin concept

**Definitions from credible sources.**

- ISO 23247-1:2021 (Edition 1, published 2021-10, 12 pages, ISO/TC 184/SC 4) provides an overview and general principles of a digital twin framework for manufacturing, including terms and definitions and requirements [FACT, R05-S43]. The full text was not inspected. A publisher-hosted public preview of the terms was read; it defines a digital twin as a fit-for-purpose digital representation of an observable manufacturing element with synchronisation between the element and its representation, and lists observable manufacturing elements as including personnel, equipment, material, process, facility, environment, product and supporting document [FACT, R05-S44]. The preview's introduction says a digital twin monitors its element by constantly updating relevant operational and environmental data, and that the standard does not prescribe data formats or protocols [FACT, R05-S44]. Parts 2 to 4 cover reference architecture, information attributes, and information exchange [FACT, R05-S44].
- NIST describes a digital twin as a specialised computer model of a physical system with potential for high accuracy and precision and flexibility to represent different aspects of that system; its use cases include monitoring, anomaly detection, prediction, and virtual commissioning [FACT, R05-S45]. NIST's state-of-the-art page states that the lack of a single unified definition creates ambiguity and lists real-time bidirectional data exchange and lifecycle connection as distinguishing aspects [FACT, R05-S46].

**Interpretation for Valtoryn [REC].** ISO 23247 is a manufacturing framework; a warehouse AMR is "equipment" within its element taxonomy [EST]. Adopt the *vocabulary* (fit-for-purpose, synchronisation) without claiming conformance to a standard whose full text was not read. Use three staged terms in documentation:

| Term | Meaning | Minimum evidence |
|---|---|---|
| Simulation model | Parameterised plant and environment, not tied to a real unit | Verification (does it run as specified) |
| Calibrated model | Parameters identified and validated against hardware data for a specific platform | Validation vs hardware at stated levels (Section 7) |
| Digital twin | Calibrated model whose state is kept synchronised with a specific physical unit (or fleet) through a defined data path | Calibrated model plus defined synchronisation interface, latency, and drift monitoring |

**What a digital twin of a warehouse robot requires [REC].**

1. *System identification:* excitation experiments on the unit (velocity steps, chirps, in-place rotations, braking, payload series) to estimate motor, drive, wheel-ground and inertial parameters with confidence intervals. Tan et al. used system identification to build an actuator model and latency into a legged-robot simulator [FACT, R05-S51]; Kawachi reports a low-cost approach of measuring effective proportional gains on hardware to constrain training, for a balancing robot with a 110:1 gearbox [FACT, R05-S53].
2. *Parameter calibration with provenance:* each parameter tagged with source (datasheet, measured, assumed), uncertainty, and date.
3. *State synchronisation:* defined mapping from telemetry (pose, wheel speeds, battery state, payload ID, faults) to twin state, with explicit latency and a divergence monitor.
4. *Fit-for-purpose statement:* the intended use and acceptance criteria written before validation, as NASA-STD-7009B requires for models and simulations [FACT, R05-S47].
5. *Lifecycle:* wear, battery ageing, and firmware changes alter parameters; recalibration triggers are needed. The MiR100 study found similar models for two batteries of different age but warns the sample is too small for a conclusion [FACT, R05-S58].

**Validation vocabulary from NASA-STD-7009B (approved 2024-03-05).** Verification is whether the M&S complies with its specified requirements; validation is the degree to which it accurately represents the real world from the perspective of its intended uses; a "referent" is the data or system compared against (the real system, an analogous system, or a higher-fidelity model); the *domain of validation* (inputs where results compared favourably) must be compared to the *domain of operation*; favourable comparison requires at minimum overlapping uncertainty intervals around the means; acceptance criteria for verification, validation, uncertainty and sensitivity must be defined; and validation Levels 0 to 4 run from insufficient evidence, through conceptual validation (1), comparison with a representative system (2), representative environment (3), up to operating environment with validation points spanning the operating domain (4); no level above 1 may be assigned until conceptual validation holds [FACT, R05-S47].

### 3.15 The reality gap in the peer-reviewed literature

| Work | What it shows | Relevance and limit |
|---|---|---|
| Zhao, Queralta, Westerlund (arXiv 2009.13303, v1 2020-09-24) | Survey of sim-to-real transfer in deep RL for robotics; categories: domain randomisation, domain adaptation, imitation learning, meta-learning, knowledge distillation [R05-S48] | RL-focused; not a wheeled-AMR validation method |
| Muratore et al. (arXiv 2111.00956, 2021) | Review of robot learning from randomised simulations; frames the reality gap as arising because every simulator is built on imperfect models [R05-S56] | Same limit |
| Tobin et al. (arXiv 1703.06907, 2017) | Visual domain randomisation: a detector trained only on randomised simulated images localised real objects to within 1.5 cm [R05-S49] | Perception, not dynamics |
| Peng et al. (arXiv 1710.06537, 2017) | Dynamics randomisation: policies trained only in randomised simulation performed comparably on a physical arm pushing task and tolerated calibration error [R05-S50] | Arm pushing; randomisation range is a design choice |
| Tan et al. (arXiv 1804.10332, 2018) | Quadruped locomotion: simulator improved via system identification including an accurate actuator model and simulated latency, plus randomisation [R05-S51] | Abstract-level facts only; model details not read |
| Collins, Howard, Leitner (arXiv 1811.01484, 2018) | Quantified how closely several simulators match motion-capture-measured Kinova arm tasks; reports where each is better or worse [R05-S52] | Method (simulator versus motion-capture referent) is transferable; numbers are not |
| Ivaldi, Padois, Nori (arXiv 1402.7050, 2014) | User-feedback survey of dynamics simulation tools; objective comparison hard because most tools are not open source [R05-S55] | Dated; opinion-based |
| Kawachi (arXiv 2507.23445, 2025) | Domain randomisation often fails when the gap is large, notably for low-gear-ratio, backdrivable actuators; measured effective gains used as regularisation on a 110:1 gearbox balancing robot [R05-S53] | Two-wheeled balancing robot; actuator-dependence is the lesson |
| Akella, Ubellacker, Ames (arXiv 2209.09337, 2022) | Procedure to estimate a sim-to-real gap holding with minimum probability, add it to the nominal model, and verify a controller probabilistically; hardware needed only to identify the gap [R05-S54] | A framework for bounded claims; guarantees depend on assumptions not reviewed here |

A 2025 IEEE Robotics and Automation Letters paper on quantifying the sim2real gap for autonomous ground systems (a skid-steer robot) appeared in search results; its text could not be opened and it is not relied upon [UNRESOLVED].

**What the literature supports for the Valtoryn plan.** (1) Actuator and latency fidelity are repeatedly identified as the dominant gap sources [R05-S51, R05-S53]. (2) Randomising parameters is useful for robustness but is not a substitute for identification when the gap is structural [R05-S53, R05-S56]. (3) The cleanest way to *quantify* the gap is a referent measurement against hardware (motion capture, in Collins et al.) [R05-S52]. (4) The sources read cover manipulators, legged robots and balancing robots; direct, peer-reviewed evidence for Gazebo-class simulators on warehouse AMR navigation was not obtained [UNRESOLVED].

### 3.16 What simulation can never establish

[REC, with grounding]

1. **Safety certification of a physical machine.** ISO 3691-4 (the 2020 edition catalogue page was read; it is marked withdrawn and replaced by ISO 3691-4:2023) specifies safety requirements and *means of verification* for driverless industrial trucks, explicitly including AMRs [FACT, R05-S59]. The full text of either edition was not inspected; which verification activities accept simulation evidence is [UNRESOLVED] and belongs to R08. The reasoning available from sources read: NASA-STD-7009B requires validation against referent data in a domain covering intended use [R05-S47], and no simulation can supply referent data for a physical protective function of hardware that does not yet exist [EST].
2. **Unmodelled phenomena.** Anything absent from the model (floor contamination, wheel wear, cabling, EMI, RF multipath, thermal derating, mechanical looseness) is invisible to it; validation only covers the validated domain [FACT for the domain concept, R05-S47; EST for the list].
3. **True human and third-party behaviour.** Scripted or replayed trajectories are hypotheses about behaviour [EST].
4. **Hardware and software faults in real components.** Simulated faults are injected assumptions; real fault distributions require field data [EST].
5. **Long-term and fleet-level degradation** without long-duration hardware data [EST].
6. **Absolute performance numbers** (stopping distance, runtime, throughput) without validation at the relevant evidence level (Section 7) [REC].

---

## 4. Trade-off analysis

| Decision | Option A | Option B | Considerations (evidence) | Proposed direction [REC] |
|---|---|---|---|---|
| Primary simulator | Gazebo Sim (Apache-2.0, ROS 2 integration, DART default) | Isaac Sim (GPU requirement, Omniverse terms, fixed-step determinism) | Gazebo is the stack used by Open-RMF demos [R05-S26] and integrates with ros2_control [R05-S18]; Isaac needs RTX-class GPU per README [R05-S35] | Gazebo as default CI simulator; keep interfaces simulator-agnostic so others can be added |
| Physics engine | DART default | Bullet-Featherstone | DART supports all documented options [R05-S01]; Bullet-Featherstone marked preliminary [R05-S01] but received joint-limit enforcement [R05-S12] | DART baseline; run the same scenario on a second engine as a model-form sensitivity check |
| Actuator model | Native ros2_control joint interfaces | Valtoryn custom `SystemInterface` with motor/drive/battery model | Native interfaces model no motor dynamics [R05-S18]; custom pattern demonstrated by the low-pass demo [R05-S18] | Custom plant model, simulator-independent where possible |
| Noise | SDF Gaussian noise only | Custom noise callback / external degradation stage | Documented noise is i.i.d. Gaussian for lidar [R05-S06]; custom hook exists [R05-S16] | SDF noise for baseline, plus measured, structured degradation as hardware data arrives |
| Dynamic obstacles | Actors | Physics bodies | Actors have no contact [R05-S29] | Both, with explicit scope labels |
| Reproducibility | Assume determinism | Statistical gates | Open issue [R05-S31] | Statistical gates |
| Third-party worlds | Reuse AWS world | Author own world | Archived, unmaintained, licence file ambiguity [R05-S23, R05-S24] | Own world; third-party optional |

---

## 5. Implications and recommendations for Valtoryn

All items are [REC].

1. **Architecture.** Keep the simulator behind the same ros2_control/hardware-abstraction boundary used for real hardware, so that the controller stack is unchanged between simulation, HIL and hardware; the simulator-specific part is limited to a system plugin. `gz_ros2_control` shows this pattern (a ros2_control hardware block selects the Gazebo system plugin) [R05-S18]. Put motor, drive, battery and latency models in simulator-independent libraries and call them from thin simulator adapters.
2. **Version pinning.** Pin one Gazebo LTS release (Jetty or Harmonic; both LTS per [R05-S05]) together with ROS 2 distro, `ros_gz`, `gz_ros2_control` and DART versions; record them with every result. Decide between Jetty and Harmonic after checking Open-RMF and `gz_ros2_control` compatibility, since the RMF README names Ionic [R05-S26], which reaches end of life in December 2026 [R05-S05] [UNRESOLVED].
3. **Parameter registry.** A machine-readable registry where every simulation parameter carries source class (datasheet / measured / assumed), value, uncertainty, measurement date, and method. Assumed parameters make dependent results "simulated, unvalidated" automatically.
4. **Evidence labels on every result.** Each simulation report states its evidence level (Section 7) and validated domain; dashboards must not show bare numbers.
5. **Wheel-ground model.** Start with explicit friction values and `fdir1` set deliberately; add WheelSlip only after an in-place rotation and a straight-line slip test on hardware justify it, and recompute `wheel_normal_force` per payload.
6. **Latency and degradation layer.** An injectable, seed-controlled stage for sensor and command delay, jitter, dropout and bias drift, configurable from measured distributions.
7. **Determinism.** Fixed step, explicit seeds, N-repeat statistics, recorded logs (`--record`) for debugging, and a standing "run-to-run spread" monitor in CI (Section 8, F1).
8. **Headless CI.** Use `-s`, `--iterations`, `--seed`, `--headless-rendering` for lidar/camera scenarios [R05-S30]; budget wall-clock using measured RTF, not the nominal target.
9. **Hardware validation campaign design (before first hardware arrives).** Write the validation test procedures and acceptance forms now (Section 8) so that the first hardware data collection is not ad hoc. Plan motion-capture or equivalent ground truth, as in Collins et al. [R05-S52].
10. **Digital twin staging.** Use the three-term vocabulary (simulation model / calibrated model / digital twin). Do not use "digital twin" for an unsynchronised model.
11. **Safety separation.** No simulation result may be cited as safety evidence in R08 deliverables without a hardware-referenced validation at Level 3 or 4 *and* explicit agreement with the safety case owner; simulation may support hazard analysis scenarios and regression of safety-function *software* behaviour only.
12. **Cross-reference R08.** The question of which simulation evidence a notified body or assessor accepts for ISO 3691-4 verification must be resolved there.

---

## 6. Simulation test taxonomy

| Level | Scope | Typical content | Can claim | Cannot claim | Determinism requirement |
|---|---|---|---|---|---|
| Unit | One function/class, no simulator | Kinematics, motor equation, battery equation, noise injector maths | Code behaves per specification on tested inputs (verification) | Anything about the real robot | Bitwise reproducible |
| Component | One module with simulated or recorded inputs | Controller step response against plant model; localiser on a recorded log; planner on a map | Module-level behaviour against the *model*; with recorded real data, module-level behaviour on that data | System-level behaviour, timing under load | Seeded, tolerance-based |
| System (integration) | Full software stack in simulator | Navigation of a world with the full node graph | Integration works, interfaces and timing consistent in simulation | Real-world task performance | Statistical (N runs) |
| Scenario | Defined situations with pass/fail | Blocked aisle, person crossing, comms outage, low battery, payload change | Behaviour in the named scenario under the modelled assumptions; relative A/B comparison if assumptions held fixed | Coverage of reality; that real hazards match scenarios | Statistical, seeds logged |
| Regression | Fixed scenario set run on every change | Baseline metrics with tolerance bands | A change did not move tracked metrics beyond band; run-to-run spread monitored | Correctness (a stable wrong answer passes) | Statistical gates |
| HIL | Real compute / firmware / drives with simulated plant and sensors | Real motion controller or MCU with simulated wheels and battery; real network stack with emulated link | Timing, interface, firmware and fault-handling behaviour on real hardware paths; limited by the plant model's validity | Plant dynamics beyond the model; mechanical or environmental effects | Real-time; jitter measured |
| (Reference) Hardware test | Real robot in real environment | Dyno, floor, site trials | Referent data used to validate every layer above | n/a | n/a |

---

## 7. Evidence levels and permitted claims

[REC] Evidence levels are proposed, loosely aligned with NASA-STD-7009B validation levels 0 to 4 [R05-S47]. The mapping is a Valtoryn proposal, not part of that standard.

| Level | Name | Evidence required | Corresponds to NASA validation level (approximate) | Claims permitted | Claims forbidden |
|---|---|---|---|---|---|
| E0 | Simulated, unvalidated | Code runs; parameters partly assumed | 0 | "The software executes scenario S and produces output X in simulation"; logic and interface checks | Any performance, energy, throughput or safety number presented as predictive |
| E1 | Simulated, verified and conceptually justified | Verification evidence; written intended use; model assumptions reviewed | 1 | Relative comparisons of algorithm variants *labelled simulation-only*; sensitivity ranking of parameters | Absolute predictions |
| E2 | Component-validated | Subsystem models compared to bench/component hardware data (motor dyno, sensor noise logs, battery discharge) with uncertainty intervals overlapping | 2 | Subsystem predictions within the tested domain with stated uncertainty | Vehicle-level behaviour outside tested conditions |
| E3 | Vehicle-validated in representative environment | Vehicle-level simulated metrics compared to measurements on the real unit in a representative environment; validation points significantly span intended operating domain | 3 | Predicted vehicle behaviour (speed profiles, stopping distance estimates, localisation error distribution, runtime) within the validated domain, with intervals; pre-deployment tuning | Site-specific guarantees; safety certification |
| E4 | Operating-environment validated | Comparison in the actual operating environment across the operating domain | 4 | Site-specific throughput and congestion estimates with intervals | Safety certification by simulation; behaviours outside validated domain |

Safety certification is excluded at every level; claims about protective functions require physical verification as defined in R08 [REC; see 3.16].

---

## 8. Measurable simulation fidelity requirements

[REC] Throughout, "to be set from measured hardware data" means the threshold must be derived from (a) the uncertainty of the hardware measurement and (b) the tolerance of the downstream decision the simulation informs; no numerical threshold is asserted here. The generic acceptance form is:

> For metric M over a defined test condition set C: let the simulated distribution and hardware distribution be summarised by means and expanded-uncertainty intervals. Accept if (i) the intervals overlap (the minimum NASA-STD-7009B comparison condition [R05-S47]) **and** (ii) |mean_sim − mean_hw| ≤ δ_M, where δ_M is set from measured hardware data and the decision tolerance, and (iii) the spread ratio (sim/hw) lies within a band set from measured data.

Validation points must be recorded as a set, because the validated domain is the region those points span [R05-S47].

| ID | Dimension | Metric | Measurement procedure (hardware referent and simulation) | Proposed acceptance form | Highest claim when passed |
|---|---|---|---|---|---|
| F1 | Run-to-run reproducibility | Spread (max pairwise deviation and standard deviation) of final pose and key metrics over N identical seeded runs | Run each regression scenario N times, fixed seed/step, separate processes; no hardware | Spread ≤ f × scenario tolerance, with f chosen by the team (placeholder) and justified; any increase tracked in CI | Simulation-stack quality (E0/E1 enabler only) |
| F2 | Time-step convergence | Change in key metrics when `max_step_size` is halved | Run scenario at step h and h/2 (and h/4 if needed) | Relative metric change ≤ ε_conv set from the scenario tolerance | E1 |
| F3 | Timing and real-time factor | Measured RTF and per-step wall time vs robot count and sensor load | Instrument runs on the CI hardware class; record machine spec | RTF ≥ target needed for CI wall-clock budget; target to be set from the CI requirement | Operational feasibility only |
| F4 | Kinematics and odometry | Position and heading error after straight-line, in-place rotation, and closed-path (e.g. square) command sequences; odometry drift per metre and per radian | Hardware: ground truth by motion capture or surveyed marks over repeated trials on each floor type; sim: same commands | Overlap of distributions; δ set from hardware repeatability | E2/E3 |
| F5 | Longitudinal/yaw dynamics | Velocity step response: delay, rise time, overshoot, steady-state error; yaw-rate response; for each payload level | Hardware: command steps and log wheel encoders plus external ground truth; fit simple model; sim: replicate | Metric differences within δ set from hardware run-to-run spread | E2 then E3 |
| F6 | Braking and stopping | Stopping distance and deceleration vs speed, payload, floor type | Hardware: controlled stops from commanded speeds; sim: same | Sim stopping distance not shorter than hardware lower bound by more than δ (conservative one-sided form); δ from data | E3 for *estimation*, never for safety-function verification |
| F7 | Wheel-ground friction and slip | Slip ratio vs drive torque and load; lateral drift on turn; direction-dependence (isotropy) of friction; yaw error in rotation | Hardware: pull/push tests and in-place turns on each floor surface and payload; sim: sweep `mu`, `slip`, `fdir1` | Fitted parameters with confidence intervals; predictive check on held-out tests | E2/E3 |
| F8 | Motor/drive electrical | Current vs torque, voltage vs speed, current-limit behaviour, torque-speed curve, supply sag | Dyno or on-vehicle measurements of V, I, ω, T; sim: same loads | Curve-fit residuals ≤ δ from measurement uncertainty | E2 |
| F9 | Payload effects | Change in F5/F6/F7 metrics between payload levels; COM and inertia error | Hardware: repeat F5 to F7 at defined payload masses and COM offsets; identify inertia (method to be chosen); sim: payload manifest | Sim reproduces the *sign and magnitude* of payload sensitivity within δ | E3 |
| F10 | Lidar | Range bias and standard deviation vs range, target reflectivity and incidence angle; dropout rate; angular accuracy | Hardware: static targets at known distances/surfaces; sim: same | Noise model parameters fitted; residual structure (correlation) compared; δ from hardware | E2 |
| F11 | IMU | Noise density, bias stability (e.g. from long static logs), scale-factor error | Hardware: static and rate-table or equivalent logs; sim: matched noise/bias parameters | Parameter match within hardware identification uncertainty | E2 |
| F12 | Camera / depth | Pixel noise, exposure and distortion effects relevant to the perception algorithm; task-level detection rate | Hardware dataset with labels; sim dataset; compare algorithm performance on both | Algorithm metric difference ≤ δ set from data | E2 |
| F13 | Latency chain | Command-to-motion delay, sensor-to-timestamp delay, end-to-end loop delay: distributions (p50, p95, p99) | Hardware: instrumented loopback (e.g. command edge to encoder response) and timestamp analysis; sim: injected distributions | Percentiles within δ per percentile, set from measured data | E2 |
| F14 | Localisation | Pose-error distribution against ground truth; consistency (e.g. NEES); recovery success after displacement | Hardware runs with external ground truth; sim runs in matched map | Error and consistency distributions overlap; δ from data | E3 |
| F15 | Battery and energy | Energy per metre and per mission; voltage under load; runtime to cut-off; state-of-charge estimate error | Hardware: logged discharge in defined missions and payloads (cf. long discharge cycles in [R05-S58]); sim: matched | Predicted energy within δ of measured over validated missions | E2 then E3 |
| F16 | Communications | Delay distribution, loss rate, burst length, outage duration at the robot's real operating locations | Hardware: packet logs on site Wi-Fi; sim: netem/QoS profiles reproducing them [R05-S20] | Emulated distributions match logged distributions within δ | E2 |
| F17 | Dynamic obstacles | Speed, path and reaction distributions of people/vehicles at the site | Site observation datasets; sim: replay or sampling | Distribution match for chosen features; δ from data | E3/E4 for site claims |
| F18 | Environment geometry | Deviation of simulated world from surveyed geometry; floor slope/thresholds | Survey (laser measure/scan) vs world file | Max geometric deviation ≤ δ related to the sensor/planner tolerance | Prerequisite for E3/E4 |
| F19 | Multi-robot throughput | Fleet KPIs (task completion time, waiting time, deadlock count) vs logged fleet operation | Hardware fleet logs vs sim fleet at same task mix | KPI intervals overlap; δ from data | E4 |
| F20 | Task-level paired validation | Mission success rate and duration for matched tasks on hardware and in simulation | Paired experiments with identical start conditions | Success-rate difference within confidence bound set from sample size | E3/E4 |

All dimensions currently have status "no hardware data" and therefore no validated threshold.

---

## 9. Limitations of this research

- No simulator was run and no hardware exists; nothing here is empirical for Valtoryn.
- Several documentation pages were summarised by a fetch-time extraction model; quoted defaults and units should be re-verified in the pinned version. Gazebo API pages read were versions 9 and 10 (the "latest" docs describe Jetty); SDFormat spec pages were version 1.11.
- The SDF sensor specification was read for the first 200,000 of about 230,000 characters; the remainder (including possibly camera or latency elements) was not read.
- The ISO 23247-1 full text and the ISO 3691-4 full text were not inspected; only catalogue pages and a publisher-hosted preview of the terms were read.
- The reality-gap evidence comes mostly from manipulators, legged robots and a balancing robot, not warehouse AMRs; abstracts were read for most papers, not full texts, and no quantitative results from them are reused.
- Source weakness: the `design.ros2.org` QoS article is marked work in progress and is old; the ROS QoS content was read from the documentation source file, not the rendered page (which was blocked).
- Physics-engine behaviour (DART's handling of ODE/Bullet-labelled friction elements, WheelSlip's normal-force handling, gz-sensors timestamp semantics) requires reading source code or running experiments.

## 10. Unresolved questions

| ID | Question | What would resolve it |
|---|---|---|
| U1 | Does DART in the pinned Gazebo release use the SDF `mu`/`mu2`/`slip` elements as documented for ODE, and how does it treat friction anisotropy? | Read gz-physics DART plugin source; run a controlled sliding-block test |
| U2 | Does WheelSlip use actual dynamic normal force or only the configured constant? | Read WheelSlip source in the pinned version |
| U3 | What consumes the `--seed` value in Gazebo Sim, and is physics deterministic across processes on one machine? | Source reading; N-repeat experiment (also addresses issue #3349) |
| U4 | Real-time factor versus robot count, sensor count, and engine for a warehouse-scale world | Benchmark in Valtoryn CI |
| U5 | Compatibility of Open-RMF demos and `gz_ros2_control` with Jetty/Harmonic | Check release notes and run demos |
| U6 | Does the AWS small warehouse world run on current Gazebo Sim, and is its licence MIT or MIT-0, including asset licences? | Run/convert the world; read the full LICENSE and per-asset metadata |
| U7 | Licence of each Fuel asset considered for use | Per-asset metadata on Fuel |
| U8 | Which simulation evidence, if any, is accepted for ISO 3691-4:2023 verification? | Obtain the standard; R08 |
| U9 | Does tc/netem work in Valtoryn's intended CI and developer environments? | Test on the target environments |
| U10 | Does the unread tail of the SDF sensor spec contain latency/lag elements? | Read the remaining ~30,000 characters or the libsdformat source |
| U11 | Peer-reviewed quantitative evidence for wheeled/skid-steer sim-to-real gaps (e.g. the 2025 RAL paper found only in search results) | Open that paper |
| U12 | Isaac Sim, Webots and MuJoCo friction/contact and sensor-noise details sufficient for a wheeled AMR comparison | Read each simulator's physics and sensor docs in depth |

---

## 11. Sources

| ID | Title | Organization / author | URL | Published / revision date | Accessed | What it supports |
|---|---|---|---|---|---|---|
| R05-S01 | Gazebo Sim: Physics engines (API v10) | Open Robotics / Gazebo | https://gazebosim.org/api/sim/10/physics.html | n/a (not stated on page) | 2026-11-07 | Default DART; preliminary Bullet/Bullet-Featherstone; DART collision detector and solver options |
| R05-S02 | Gazebo Sim: WheelSlip Class Reference (v10) | Open Robotics / Gazebo | https://gazebosim.org/api/sim/10/classgz_1_1sim_1_1systems_1_1WheelSlip.html | n/a (not stated on page) | 2026-11-07 | Slip compliance semantics, fdir1 assumption, constant normal-force parameter in example |
| R05-S03 | Gazebo Sim: DiffDrive Class Reference (v9) | Open Robotics / Gazebo | https://gazebosim.org/api/sim/9/classgz_1_1sim_1_1systems_1_1DiffDrive.html | n/a (not stated on page) | 2026-11-07 | DiffDrive parameters and defaults; no odometry noise mentioned |
| R05-S04 | Gazebo Sim: Battery (v10) | Open Robotics / Gazebo | https://gazebosim.org/api/sim/10/battery.html | n/a (not stated on page) | 2026-11-07 | Battery model, parameters, runtime formula, known issues |
| R05-S05 | Gazebo Releases | Open Robotics / Gazebo | https://gazebosim.org/docs/all/releases/ | n/a (not stated on page) | 2026-11-07 | Release names, dates, LTS and EOL |
| R05-S06 | SDFormat Specification 1.11: Sensor | Open Source Robotics Foundation | http://sdformat.org/spec/1.11/sensor/ | n/a (not stated on page) | 2026-11-07 | Noise types and parameters for generic, IMU, lidar, camera sensors; update_rate (first ~200,000 characters read) |
| R05-S07 | SDFormat Specification 1.11: Collision | Open Source Robotics Foundation | http://sdformat.org/spec/1.11/collision/ | n/a (not stated on page) | 2026-11-07 | Friction (ODE, Bullet, torsional), contact and soft-contact parameters |
| R05-S08 | SDFormat Specification 1.11: Physics | Open Source Robotics Foundation | http://sdformat.org/spec/1.11/physics/ | n/a (not stated on page) | 2026-11-07 | max_step_size, real_time_factor, real_time_update_rate, max_contacts defaults |
| R05-S09 | SDFormat Specification 1.11: Joint | Open Source Robotics Foundation | http://sdformat.org/spec/1.11/joint/ | n/a (not stated on page) | 2026-11-07 | Joint dynamics (damping, friction) and limits; no backlash element |
| R05-S10 | SDFormat Specification 1.11: Link | Open Source Robotics Foundation | http://sdformat.org/spec/1.11/link/ | n/a (not stated on page) | 2026-11-07 | Inertial mass, centre-of-mass pose, inertia tensor; battery element |
| R05-S11 | gazebosim/gz-physics (README) | Open Robotics / Gazebo | https://github.com/gazebosim/gz-physics | n/a (not stated on page) | 2026-11-07 | Engine plugins (dartsim, TPE, bullet), Apache-2.0 |
| R05-S12 | Gazebo Ionic Release | Open Robotics (Open Robotics Discourse) | https://discourse.openrobotics.org/t/gazebo-ionic-release/49064 | 2024-09-30 | 2026-11-07 | Bullet-Featherstone improvements |
| R05-S14 | Open Dynamics Engine v0.039 User Guide | Russell Smith / ode.org | https://ode.org/ode-0.039-userguide.html | n/a (not stated on page) | 2026-11-07 | Friction cone approximation, pyramid, mu, slip, fdir1, first-order integrator accuracy |
| R05-S15 | Gazebo tutorial: Sensors (Jetty docs) | Open Robotics / Gazebo | https://gazebosim.org/docs/latest/sensors/ | n/a (not stated on page) | 2026-11-07 | IMU, contact, lidar sensor SDF usage; update_rate; render engine requirement |
| R05-S16 | Gazebo Sensors: Noise Class Reference (v10) | Open Robotics / Gazebo | https://gazebosim.org/api/sensors/10/classgz_1_1sensors_1_1Noise.html | n/a (not stated on page) | 2026-11-07 | Noise base class, custom noise callback |
| R05-S17 | Gazebo Sensors: GaussianNoiseModel (v9) | Open Robotics / Gazebo | https://gazebosim.org/api/sensors/9/classgz_1_1sensors_1_1GaussianNoiseModel.html | n/a (not stated on page) | 2026-11-07 | Gaussian noise class with mean, stddev, bias |
| R05-S18 | gz_ros2_control documentation | ros2_control project | https://control.ros.org/rolling/doc/gz_ros2_control/doc/index.html | n/a (not stated on page) | 2026-11-07 | Command/state interfaces, velocity-slip warning, position P-law, custom low-pass demo |
| R05-S19 | AMCL (Nav2 documentation, rolling) | Nav2 project | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/others/configuring_amcl/ | n/a (not stated on page) | 2026-11-07 | Odometry noise alphas, laser model, particles, update thresholds |
| R05-S20 | tc-netem(8) manual | iproute2 project (man7.org rendering) | https://man7.org/linux/man-pages/man8/tc-netem.8.html | Manual dated 2011-11-25; rendering 2026-09-09 | 2026-11-07 | Delay/loss/duplication/corruption/reorder/rate emulation and limits |
| R05-S21 | About Quality of Service Settings (documentation source, Jazzy branch) | ROS 2 documentation project (GitHub raw) | https://raw.githubusercontent.com/ros2/ros2_documentation/jazzy/source/Concepts/Intermediate/About-Quality-of-Service-Settings.rst | n/a (not stated on page) | 2026-11-07 | QoS policies, default profiles, compatibility rules |
| R05-S22 | ROS 2 Quality of Service policies (design article) | ROS 2 design (design.ros2.org) | https://design.ros2.org/articles/qos.html | Written Oct 2015; last modified May 2019 | 2026-11-07 | Core QoS policies (older, work in progress) |
| R05-S23 | aws-robotics/aws-robomaker-small-warehouse-world | AWS Robotics (GitHub) | https://github.com/aws-robotics/aws-robomaker-small-warehouse-world | n/a (not stated on page) | 2026-11-07 | Warehouse world; archived; end-of-support notice; production warning |
| R05-S24 | LICENSE file, aws-robomaker-small-warehouse-world (ros2 branch) | Amazon.com, Inc. (GitHub raw) | https://raw.githubusercontent.com/aws-robotics/aws-robomaker-small-warehouse-world/ros2/LICENSE | n/a (not stated on page) | 2026-11-07 | Licence text begins with Amazon copyright, MIT-style wording |
| R05-S25 | aws-robomaker-small-warehouse-world (ROS index) | ROS index (index.ros.org) | https://index.ros.org/r/aws-robomaker-small-warehouse-world/ | Last Updated 2021-12-15 as displayed | 2026-11-07 | Package version, distros, status display |
| R05-S26 | Demonstrations of Open-RMF (rmf_demos) | Open-RMF project (GitHub) | https://github.com/open-rmf/rmf_demos | n/a (not stated on page) | 2026-11-07 | Demo worlds, tested Gazebo Ionic and ROS 2 Kilted, Apache-2.0, crowd sim option |
| R05-S27 | gazebosim/gz-fuel-tools (README) | Open Robotics / Gazebo | https://github.com/gazebosim/gz-fuel-tools | n/a (not stated on page) | 2026-11-07 | Fuel client, default server, CLI; no licence info for models |
| R05-S28 | Gazebo tutorial: Inserting models from Fuel | Open Robotics / Gazebo | https://gazebosim.org/docs/latest/fuel_insert/ | n/a (not stated on page) | 2026-11-07 | Fuel hosts models; no model licence information on page |
| R05-S29 | Gazebo tutorial: Actors | Open Robotics / Gazebo | https://gazebosim.org/docs/latest/actors/ | n/a (not stated on page) | 2026-11-07 | Actors are non-physical, visible to cameras and GPU sensors |
| R05-S30 | gz-sim `cmdsim.rb.in` (gz sim CLI script, gz-sim9 branch) | Open Robotics / Gazebo (GitHub raw) | https://raw.githubusercontent.com/gazebosim/gz-sim/gz-sim9/src/cmd/cmdsim.rb.in | n/a (not stated on page) | 2026-11-07 | gz sim CLI options: -s, -r, --iterations, -z, --seed, --record, --playback, --network-role, --headless-rendering |
| R05-S31 | Issue 3349: Rigid body motion is non-deterministic across identical simulations | gazebosim/gz-sim GitHub issue (reporter liyitao-code) | https://github.com/gazebosim/gz-sim/issues/3349 | Opened 2026-02-24; follow-up 2026-09-05 | 2026-11-07 | Reported run-to-run divergence; open, no maintainer response visible |
| R05-S32 | Gazebo Classic tutorial: Random numbers | Open Robotics / Gazebo Classic | https://classic.gazebosim.org/tutorials?tut=random_numbers | n/a (not stated on page) | 2026-11-07 | Classic --seed behaviour; default seed from process ID |
| R05-S33 | gazebosim/gz-sim (README) | Open Robotics / Gazebo | https://github.com/gazebosim/gz-sim | n/a (not stated on page) | 2026-11-07 | Apache-2.0; Windows server/GUI split |
| R05-S34 | Launch Gazebo from ROS 2 | Open Robotics / Gazebo | https://gazebosim.org/docs/latest/ros2_launch_gazebo/ | n/a (not stated on page) | 2026-11-07 | use_sim_time, /clock bridge, server-only launch file |
| R05-S35 | isaac-sim/IsaacSim (README) | NVIDIA (GitHub) | https://github.com/isaac-sim/IsaacSim | n/a (not stated on page) | 2026-11-07 | Apache-2.0 badge, Omniverse terms, GPU requirements, RTX sensors, ROS bridge |
| R05-S36 | Physics: Isaac Sim Documentation | NVIDIA | https://docs.isaacsim.omniverse.nvidia.com/latest/physics/index.html | n/a (not stated on page; search listing showed 2026-10-14) | 2026-11-07 | PhysX default, Newton experimental backend |
| R05-S37 | Robot Simulation Tips: Isaac Sim Documentation | NVIDIA | https://docs.isaacsim.omniverse.nvidia.com/latest/robot_simulation/robot_simulation_tips.html | n/a (not stated on page; search listing showed 2026-10-14) | 2026-11-07 | Wheeled-robot friction guidance, fixed time stepping and determinism, mass/inertia defaults |
| R05-S38 | cyberbotics/webots (README) | Cyberbotics (GitHub) | https://github.com/cyberbotics/webots | n/a (not stated on page) | 2026-11-07 | Apache-2.0; platforms; description |
| R05-S39 | Webots reference: Physics (documentation source) | Cyberbotics (GitHub raw) | https://raw.githubusercontent.com/cyberbotics/webots/master/docs/reference/physics.md | n/a (not stated on page) | 2026-11-07 | ODE usage; inertiaMatrix, centerOfMass; ContactProperties |
| R05-S40 | google-deepmind/mujoco (README) | Google DeepMind (GitHub) | https://github.com/google-deepmind/mujoco | n/a (not stated on page) | 2026-11-07 | Apache-2.0 code; features; "not officially supported" notice |
| R05-S41 | MuJoCo Documentation: Computation | Google DeepMind | https://mujoco.readthedocs.io/en/stable/computation/index.html | n/a (not stated on page) | 2026-11-07 | Elliptic/pyramidal friction cones; soft constraints; relation to LCP (first ~100,000 characters read) |
| R05-S42 | DART documentation (DART 6 LTS) | DART project | https://dart.readthedocs.io/en/latest/ | DART 6.19.5 release noted as 2026-10-04 | 2026-11-07 | Generalised coordinates; Featherstone ABA |
| R05-S43 | ISO 23247-1:2021 (catalogue page) | ISO | https://www.iso.org/standard/75066.html | 2021-10 (Edition 1) | 2026-11-07 | Scope abstract, status, committee, pages (full text not inspected) |
| R05-S44 | ISO 23247-1:2021 public preview (terms, introduction) | ISO text as hosted by iTeh Standards | https://cdn.standards.iteh.ai/samples/75066/ec0a1c59176e488887873acda6b7ecd9/ISO-23247-1-2021.pdf | 2021 (© ISO 2021) | 2026-11-07 | Digital twin definition (fit for purpose, synchronisation); OME list; series parts |
| R05-S45 | Digital twins (NIST) | NIST | https://www.nist.gov/digital-twins | n/a (not stated on page) | 2026-11-07 | NIST description and use cases |
| R05-S46 | Definitions and State of the Art (NIST digital twins) | NIST | https://www.nist.gov/digital-twins/definitions-and-state-art | 2025-12-04 | 2026-11-07 | Lack of unified definition; bidirectional exchange, lifecycle aspects |
| R05-S47 | NASA-STD-7009B Standard for Models and Simulations | NASA Office of the Chief Engineer | https://standards.nasa.gov/sites/default/files/standards/NASA/B/1/NASA-STD-7009B-Final-3-5-2024.pdf | Approved 2024-03-05 | 2026-11-07 | Verification, validation, referent, domain of validation, comparison criteria, levels 0 to 4 |
| R05-S48 | Sim-to-Real Transfer in Deep Reinforcement Learning for Robotics: a Survey | Zhao, Queralta, Westerlund (arXiv 2009.13303) | https://arxiv.org/abs/2009.13303 | v1 2020-09-24; v2 2021-07-08 | 2026-11-07 | Survey and categories of reality-gap methods |
| R05-S49 | Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World | Tobin et al. (arXiv 1703.06907) | https://arxiv.org/abs/1703.06907 | 2017-03-20 | 2026-11-07 | Visual domain randomisation result |
| R05-S50 | Sim-to-Real Transfer of Robotic Control with Dynamics Randomization | Peng et al. (arXiv 1710.06537) | https://arxiv.org/abs/1710.06537 | v1 2017-10-18; v3 2018-03-03 | 2026-11-07 | Dynamics randomisation result |
| R05-S51 | Sim-to-Real: Learning Agile Locomotion For Quadruped Robots | Tan et al. (arXiv 1804.10332) | https://arxiv.org/abs/1804.10332 | v1 2018-04-27; v2 2018-05-16 | 2026-11-07 | System identification, actuator model, simulated latency (abstract level) |
| R05-S52 | Quantifying the Reality Gap in Robotic Manipulation Tasks | Collins, Howard, Leitner (arXiv 1811.01484) | https://arxiv.org/abs/1811.01484 | v1 2018-11-05 | 2026-11-07 | Simulator versus motion-capture referent comparison |
| R05-S53 | Quantifying and Visualizing Sim-to-Real Gaps: Physics-Guided Regularization for Reproducibility | Kawachi (arXiv 2507.23445) | https://arxiv.org/abs/2507.23445 | 2025-07-31 | 2026-11-07 | Domain randomisation limits with backdrivable actuators; hardware gain measurement |
| R05-S54 | Safety-Critical Controller Verification via Sim2Real Gap Quantification | Akella, Ubellacker, Ames (arXiv 2209.09337) | https://arxiv.org/abs/2209.09337 | 2022-09-19 | 2026-11-07 | Probabilistic quantification of sim2real gap |
| R05-S55 | Tools for dynamics simulation of robots: a survey based on user feedback | Ivaldi, Padois, Nori (arXiv 1402.7050) | https://arxiv.org/abs/1402.7050 | 2014-02-27 | 2026-11-07 | Simulator selection survey; comparison difficulty |
| R05-S56 | Robot Learning from Randomized Simulations: A Review | Muratore et al. (arXiv 2111.00956) | https://arxiv.org/abs/2111.00956 | v1 2021-11-01; v2 2022-01-18 | 2026-11-07 | Reality gap framing; domain randomisation review |
| R05-S57 | A Simplified Approach to dc Motor Modeling for Dynamic Stability Analysis (SLUA076) | Texas Instruments (ed. M. McClure) | https://www.ti.com/lit/pdf/slua076 | July 2000 | 2026-11-07 | Torque and voltage constants equal in SI; motor as transformer; inertial load model |
| R05-S58 | Multi-Parameter Predictive Model of Mobile Robot's Battery Discharge for Intelligent Mission Planning in Multi-Robot Systems | Poskart et al., Sensors 22(24):9861 | https://www.mdpi.com/1424-8220/22/24/9861 | 2022 (day not stated on page) | 2026-11-07 | MiR100 discharge experiments, resistance decomposition, regression model and residuals |
| R05-S59 | ISO 3691-4:2020 (catalogue page, withdrawn) | ISO | https://www.iso.org/standard/70660.html | 2020-02 (Edition 1; withdrawn; new version ISO 3691-4:2023 noted) | 2026-11-07 | Scope: safety requirements and verification for driverless trucks including AMRs (full text not inspected) |
| R05-S60 | Gazebo Sim: Tutorials (API v10) | Open Robotics / Gazebo | https://gazebosim.org/api/sim/10/tutorials.html | n/a (not stated on page) | 2026-11-07 | Tutorial index (headless rendering, logging, battery, wheel slip; none on performance or determinism) |

**Sources that could not be inspected (not cited for any claim):**

- ROS 2 QoS rendered page on docs.ros.org (blocked by a bot-protection challenge); the documentation source file was used instead (R05-S21).
- Shao et al., "Framework for a Digital Twin in Manufacturing" on PubMed Central (verification screen returned instead of the article).
- University of Michigan Control Tutorials DC motor modelling page (HTTP 403).
- Waheed et al., "Quantifying the sim2real gap: Model-based verification and validation in autonomous ground systems," IEEE RA-L 2025 (ADS and IEEE pages not retrievable; seen only in search listings).
- docs.ros.org package page for the AWS warehouse world (bot challenge; a licence statement seen in a search snippet was therefore not used).
- NIST IR 8356 (Security and Trust Considerations for Digital Twin Technology), ISO 23247-2 to -4, and ISO 3691-4:2023 (not fetched or paywalled).
- A Gazebo community discourse thread and a gz-sim issue about Bullet-Featherstone joint velocity control, and an Open-RMF demo crash thread (search listings only).
- Source code of gz-sim, gz-physics, gz-sensors and the DART plugin (not read; several [UNRESOLVED] items depend on it).

