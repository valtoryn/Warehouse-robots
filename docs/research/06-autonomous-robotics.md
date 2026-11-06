# R06 — Autonomy: Mapping, Localisation, Planning, Control and Fault Handling

> **Status:** Research document — proposed findings, nothing here is implemented.
> **Workstream:** R06 · **Last verified:** 2026-11-07 · **Evidence legend:** see below

## Evidence legend

- **[FACT]** established by a cited source, always followed by a source ID such as [R06-S08].
- **[CALC]** derived by a shown calculation from cited or labelled inputs.
- **[EST]** engineering estimate or assumption (basis stated).
- **[REC]** Valtoryn recommendation or proposal (engineering judgement, not established fact).
- **[UNRESOLVED]** could not be established; what would resolve it is stated.

Nothing in this document describes an implemented Valtoryn capability. No hardware exists, and no hardware was tested. Every statement about "Valtoryn" is a proposal.

---

## 1. Scope and method

**Question.** Which autonomy functions (mapping, localisation, planning, control, obstacle handling, recovery, task execution, fault handling) can be one reusable implementation across every Valtoryn robot configuration, and which must be parameterised or replaced per configuration (footprint, kinematics, dynamics limits, sensor placement and field of view, payload-dependent limits, docking geometry, safety zones)?

**Method.** I read primary documentation for Nav2 (the `rolling` documentation set, with two pages cross-checked against `jazzy`), SLAM Toolbox (JOSS paper and repository README), Cartographer, RTAB-Map, `robot_localization`, ROS 2 lifecycle design, `diagnostics`, `ros2_control`/`ros2_controllers`, BehaviorTree.CPP, and a SICK reflector-localisation manual. Only pages actually fetched are cited. Where a claim comes from a vendor blog it is labelled weak. Nav2 pages in this documentation set carry no visible publication date, so "n/a (not stated on page)" appears in the Sources table.

**Version basis.** The Nav2 documentation home page lists Rolling as development, Jazzy as active support, Kilted and Humble as maintained, and a "Lyrical" release as active support [R06-S01]. Two fetches of that page rendered the Lyrical codename differently (one "Luth", one "Lynx"); the `diagnostics` repository README says "Lyrical Luth" [R06-S45], so I use only "Lyrical". Parameter names and defaults below are from the Rolling docs and can differ in released distributions. One concrete example: the Jazzy MPPI page describes the motion model as a string choice of `DiffDrive`, `Omni` or `Ackermann` [R06-S57], whereas the Rolling page describes plugin classes `mppi::DiffDriveMotionModel`, `mppi::OmniMotionModel`, `mppi::AckermannMotionModel` [R06-S08]. **[REC]** Valtoryn must pin one distribution and generate configuration per distribution.

**Not done.** No code was run, no Nav2 build was attempted, and no benchmark was reproduced. All performance numbers quoted are documentation claims on unspecified hardware and must be treated as such.

---

## 2. Summary of conclusions

1. **[FACT]** Nav2 states it targets "nearly any class of robot kinematics and dynamics; shape size", realised through plugin choice [R06-S01]. The plugin catalogue tags each controller and planner with supported drivetrains (differential, omnidirectional, Ackermann, legged), and these tags are not uniform: RPP does not list omnidirectional; MPPI does not list legged; Theta\* lists only differential and omnidirectional [R06-S02]. Kinematic coverage is therefore a per-plugin property, not a framework property.
2. **[FACT]** Three of the supplied planners (NavFn, Theta\*, Smac 2D) treat the robot as a 2D point/circle (holonomic particle) and rely on a smoother or on the controller for feasibility; only Smac Hybrid-A\* and Smac State Lattice produce kinematically feasible paths that can include reversing [R06-S02][R06-S03][R06-S10].
3. **[FACT]** Nav2's own safety node (Collision Monitor) states it is not a hard real-time safety certification [R06-S15]. **[REC]** It must be treated as a performance-level behaviour layer above, not instead of, a certified safety function (scope of another workstream).
4. **[FACT]** AMCL in Nav2 ships only differential and omnidirectional motion models, plus a custom-plugin hook [R06-S19]. An Ackermann or other kinematic class therefore needs a custom motion model or a different localiser.
5. **[FACT]** SLAM Toolbox is LGPL-2.1 [R06-S36][R06-S37]; Cartographer is Apache-2.0 but "no longer actively maintained" [R06-S38]; RTAB-Map is BSD-licensed only when OpenCV is built without the nonfree module [R06-S40]. **[REC]** Licence and maintenance status belong in the selection criteria for an open-source platform.
6. **[REC]** The reusable core should be the contracts and mechanisms (TF tree, lifecycle bring-up, behaviour-tree skeleton, task API, map/zone/graph asset pipeline, diagnostics schema). The configuration-dependent part should be a single declarative robot profile from which the planner, controller, motion-model, footprint, collision-zone, speed-limit and dock parameters are generated and checked. Section 4 gives the full matrix.
7. **[UNRESOLVED]** Whether the "long aisle, repetitive rack, dynamic racking" failure modes can be handled by 2D LiDAR SLAM alone could not be established from primary sources. I found only one weak vendor article and one domain-adjacent (subterranean) paper on geometric degeneracy (Section 3.2). This is the highest-risk item for hardware validation.

---

## 3. Findings

### 3.1 How Nav2 officially describes robot-type support

- **[FACT]** The Nav2 home page describes navigation for "nearly any class of robot kinematics and dynamics", any shape and size, indoor or outdoor, any sensor configuration [R06-S01]. This is a project claim; it is a statement of design intent, not a validated compatibility matrix.
- **[FACT]** Servers host named plugins (planner, controller, smoother, behaviour, route). A behaviour tree refers to an abstract name such as `FollowPath`, so the algorithm behind it can be swapped without editing the tree [R06-S22][R06-S24].
- **[FACT]** The footprint is either a circle (`robot_radius`) or a polygon (`footprint`), and can be updated at run time through the costmap `~/footprint` topic, with the docs naming "picking up a pallet" and a moving manipulator as examples [R06-S22][R06-S29]. If both are set, the polygon is used [R06-S29].
- **[FACT]** There is no requirement for a lidar; the only requirement is to provide the REP-105 frames `map -> odom -> base_link -> sensor frames` [R06-S20].
- **[FACT]** The architecture (behaviour-tree orchestration of independent task servers, aimed at dynamic environments) is described in a peer-reviewed IROS 2020 paper by the Nav2 authors, who also report a campus experiment alongside pedestrians; the abstract does not state a robot-kinematics coverage result [R06-S53].

**Drivetrain support as tagged in the official plugin catalogue** [R06-S02] (the "Drivetrain support" column; bold marks the catalogue's own emphasis):

| Component | Differential | Omni | Ackermann | Legged | Other / note |
|---|---|---|---|---|---|
| DWB controller | yes | yes | no | yes | DWA implementation |
| TEB controller | yes | yes | **yes** | yes | third-party plugin |
| Regulated Pure Pursuit | yes | not listed | **yes** | yes | |
| MPPI controller | yes | yes | **yes** | not listed | motion models DiffDrive/Omni/Ackermann [R06-S08] |
| Rotation Shim | yes | yes | not listed | not listed | "model rotate in place" |
| Graceful controller | yes | yes | not listed | yes | |
| Vector Pursuit | yes | not listed | yes | yes | third-party |
| NavFn planner | yes | yes | not listed | yes | "2D holonomic particle" |
| Smac 2D | yes | yes | not listed | yes | |
| Smac Hybrid-A\* | yes | yes | **yes** | yes | Dubins or Reeds-Shepp |
| Smac State Lattice | yes | yes | yes | yes | "Arbitrary / Custom" |
| Theta\* | yes | yes | not listed | not listed | "2D holonomic particle" |

Observation **[FACT]**: the catalogue lists no first-party planner or controller whose entry is specific to skid-steer, mecanum with non-trivial slip models, or articulated/tricycle forklifts; those fall under "omni", "differential" or "arbitrary/custom lattice" only to the extent their commanded body twist fits those models [R06-S02][R06-S05]. **[EST]** Mecanum and swerve platforms would map to the Omni class; tricycle/forklift platforms to Ackermann or a custom lattice; the match is not confirmed by the sources read.

### 3.2 Mapping and SLAM

**SLAM Toolbox.**
- **[FACT]** A 2D lidar graph-SLAM package built on the Karto scan matcher, using Ceres for optimisation, with synchronous and asynchronous mapping, a localisation mode, multi-session mapping, kinematic map merging, and serialisation of the pose graph and raw data (not just submaps) [R06-S36][R06-S37]. It was published in JOSS on 2021-05-13 [R06-S36].
- **[FACT]** Serialised sessions (`.posegraph`) allow continued mapping with the same or a different robot, starting from a dock, a node, or a pose [R06-S37]. Map images (PGM) are a separate export [R06-S37].
- **[FACT]** "True lifelong" mapping with node removal is described by the author as "highly experimental"; the recommended practice is to build a complete map, then switch to pose-graph-deformation localisation mode [R06-S37].
- **[FACT]** Localisation mode keeps a rolling buffer of recent scans; scans expire and the underlying map is not changed [R06-S36][R06-S37]. The author says it needs significant tuning and high-quality odometry, and recommends AMCL as the out-of-the-box option [R06-S37].
- **[FACT]** Stated benchmarks: 5x+ real time up to about 30,000 sq ft and 3x up to about 60,000 sq ft, largest known 200,000 sq ft in synchronous mode [R06-S37]. **[CALC]** 30,000 sq ft x 0.0929 m²/sq ft = about 2,790 m²; 200,000 sq ft = about 18,600 m². The JOSS paper separately claims mapping of "24,000 m²" (about 250,000 sq ft) in real time [R06-S36]. The README and paper figures differ (about 18,600 m² versus 24,000 m²); both are author claims on unspecified hardware (README mentions only a "low power 7th gen i7" for solver benchmarks) [R06-S37]. **[UNRESOLVED]** Neither is a warehouse-specific benchmark.
- **[FACT]** The package publishes a pose with scan-match covariance and exposes `position_covariance_scale` and `yaw_covariance_scale` to tune its influence in a downstream filter [R06-S37]. This is the mechanism for fusing a SLAM pose into an EKF.
- **[FACT]** The repository reports use in retail, warehouses, libraries and research [R06-S37]; it is a developer-reported usage statement, not an audited deployment record. The README also describes a decentralised multi-robot node [R06-S37].
- **[FACT]** An ABI-breaking change on 2021-03-23 altered the frame in which scan data is serialised, affecting 360° or non-axially-mounted lidars [R06-S37]. **[REC]** Lidar mounting frame is a map-compatibility input; changing lidar placement across configurations may invalidate stored pose-graphs, so map assets should record sensor and frame metadata.
- **[FACT]** Nav2's setup guide names SLAM Toolbox as officially supported and recommended when SLAM is needed, and AMCL for localisation on a static map [R06-S33]. The state-estimation concept page says it provides `map -> odom` [R06-S20].

**Cartographer.**
- **[FACT]** Two subsystems: local SLAM building locally consistent submaps (which drift), and global SLAM finding loop closures by scan-matching nodes against submaps [R06-S39]. Apache-2.0 [R06-S38].
- **[FACT]** The upstream repository states it is no longer actively maintained and that ROS binary packages are a limited-capacity fork [R06-S38]. The SLAM Toolbox paper (2021) also describes Cartographer as abandoned by Google [R06-S36]; the paper is a competitor's characterisation and is dated.
- **[REC]** Not a baseline candidate for a platform meant to be maintained for years, unless Valtoryn is prepared to own a fork.

**RTAB-Map.**
- **[FACT]** Graph-based SLAM for RGB-D, stereo and lidar using an appearance-based (bag-of-words) loop-closure detector with a memory-management scheme to bound real-time cost; it supports multi-session mapping [R06-S40]. Licence is BSD unless OpenCV is built with the nonfree module (SURF), in which case it is free for research only [R06-S40]. ROS 2 binaries are listed for Humble, Jazzy, Kilted, Lyrical and Rolling [R06-S41].
- **[REC]** Candidate when a configuration is vision-first or needs 3D; adds a licence-build check to the supply chain.

**Warehouse-specific limitations (source-limited).**
- **[FACT]** Lasers can miss mirrors and glass: transparent surfaces refract and mirrors reflect, so scan returns may lie behind the surface or appear as a virtual image; the cited work demonstrates detection with sonar fusion and mirror tracking on a single research robot (2008) [R06-S42]. It also notes that mapping and localisation can still work when mirror images are treated as real structure, but the map then disagrees with physical reality, which makes navigation unsafe [R06-S42].
- **[FACT, weak source]** A lidar vendor's field article lists glass and mirrors as causing missing returns and drift, and long featureless corridors as causing ambiguous scan matching and map "stretch"; its remedies are physical (matte tape, added features) [R06-S43]. This is a vendor marketing-adjacent blog; treat as indicative only.
- **[FACT]** A degeneracy-aware SLAM paper treats geometrically ambiguous environments (its focus is subterranean tunnels, caves, mines) as ones where existing methods perform inadequately [R06-S55]. **[EST]** Long straight rack aisles share the geometry issue; the paper does not test warehouses.
- **[UNRESOLVED]** No inspected source quantifies SLAM or localisation error in rack aisles, under dynamic racking (pallets added or removed), or with shrink-wrap and mesh. This must be measured on a Valtoryn robot in a representative aisle (Section 6).

### 3.3 Maps, static facility maps and costmaps

- **[FACT]** The ROS occupancy grid message is a row-major 2D grid whose values are application-dependent; commonly 0 free, 1 definitely occupied, -1 unknown (the message comment text) [R06-S47]. Nav2's Map Server loads a map from a YAML file name and publishes it on `map` in frame `map` [R06-S32]. **[UNRESOLVED]** Image formats, resolution and origin fields of the YAML were not read (map_server README not fetched).
- **[FACT]** Nav2's environment representation is a regular 2D costmap with layers (static, obstacle, voxel, range, inflation) [R06-S21][R06-S33]. Costs run 0 to 254 (254 lethal) in the setup guide [R06-S33]. Other representations (3D, gradient, mesh) require 3D planning and collision checking [R06-S21].
- **[FACT]** Costmap filters apply spatially dependent behaviour using filter masks: keep-out/safety zones, speed-restriction areas, preferred lanes [R06-S21]. The speed filter maps a mask value linearly to a limit via `speed_limit = base + multiplier * mask_value`, expressed as percent or absolute, and publishes it for the controller server [R06-S27][R06-S13]. The keepout filter can lower lethal cost inside a zone so a robot that has entered can leave [R06-S28]. The catalogue also lists a binary filter and a zone-parameter filter that applies a parameter set based on the mask value at the robot pose [R06-S02].
- **[FACT]** The speed filter has an optional path look-ahead that samples the plan over a velocity-dependent window using `v^2 / (2*max_decel)` so deceleration starts before the zone [R06-S27].
- **[FACT]** Additional layers in the catalogue include a spatio-temporal voxel layer with decay, a denoise layer for isolated obstacles, and a virtual layer for dynamic cost zones [R06-S02].
- **[REC]** Valtoryn should treat the facility as three separately versioned assets: (a) the SLAM/occupancy map used for localisation; (b) filter masks (keep-out, speed, lane); (c) a route graph (Section 3.9). Rack reconfiguration then invalidates only the assets it affects.

### 3.4 Localisation and sensor fusion

**AMCL (Nav2).**
- **[FACT]** Adaptive Monte Carlo localiser on a static map. Defaults: 500 to 2000 particles, `laser_model_type` likelihood field, `update_min_d` 0.25 m, `update_min_a` 0.2 rad, `robot_model_type` `nav2_amcl::DifferentialMotionModel`; the alternative is `nav2_amcl::OmniMotionModel` or a custom plugin [R06-S19].
- **[FACT]** `recovery_alpha_fast` and `recovery_alpha_slow` default to 0.0, so random-pose injection for recovery is off by default; the docs suggest 0.1 and 0.001 as "good" values [R06-S19]. The pose and covariance are saved to parameters at up to `save_pose_rate` (0.5 Hz) and reused on restart unless `always_reset_initial_pose` is set [R06-S19].
- **[FACT]** A behaviour-tree node `ReinitializeGlobalLocalization` exists to trigger AMCL global relocalisation after severe delocalisation or a kidnapped-robot event [R06-S35].
- **[FACT]** The Nav2 docs state localisation need not be lidar-based; vision or depth-based positioning is acceptable if it supplies `map -> odom` [R06-S20].

**Odometry fusion.**
- **[FACT]** Nav2 expects odometry to give a smooth, continuous `odom -> base_link`, with the global localiser correcting drift through `map -> odom` [R06-S20]. `robot_localization` provides EKF (`ekf_node`) and UKF (`ukf_node`) nodes fusing `nav_msgs/Odometry`, `sensor_msgs/Imu`, pose and twist messages with covariance, publishing `odometry/filtered` and optionally the TF [R06-S34]. It is a nonlinear state-estimation package developed by Charles River Analytics [R06-S54].
- **[FACT]** `robot_localization` guidance in the Nav2 tutorial: set `world_frame` to `odom` for continuous sources; if fusing discrete-jump global data (GPS, landmark fixes), set it to `map` and ensure another node produces `odom -> base_link` [R06-S34].
- **[FACT]** `diff_drive_controller` (ros2_controllers) publishes odometry from joint feedback, with `pose_covariance_diagonal` and `twist_covariance_diagonal` defaults of zero and a note that they "should be tuned" to the robot's data; wheel separation and radius errors alter curve and speed behaviour directly [R06-S51]. **[EST]** Left at zero, the covariance gives a downstream filter no usable weighting information; whether `robot_localization` substitutes a floor value was not verified here.
- **[REC]** Treat odometry covariance as a calibrated per-configuration artifact (wheel slip depends on floor, load and drivetrain), not a shared constant.

**Reflector and marker localisation (industrial).**
- **[FACT]** A SICK NAV350 operating manual (revision dated 2024-11-29) describes a 2D lidar that detects retro-reflectors and outputs an absolute position: up to 12,000 reflectors along a route, reflector range 0.5 m to 70 m, position accuracy of 4 mm to 25 mm depending on average reflector distance, scan at 8 Hz, and optional contour output for mixed reflector-and-contour navigation [R06-S44]. Initial positioning requires the vehicle to be stationary with at least three reflectors in view; reflectors closer than 0.6° angular separation are suppressed; windows, stainless steel and metal pipes can produce false reflections [R06-S44].
- **[FACT]** That manual describes the sensor's own telegram interface (CoLa-A/CoLa-B) and does not describe ROS integration [R06-S44]. **[UNRESOLVED]** ROS 2 driver status for such sensors was not investigated.
- **[REC]** Define localisation as a pluggable provider of `map -> odom` (plus covariance and a health state). AMCL, SLAM Toolbox localisation, a reflector localiser, or a visual-marker localiser then differ only behind that interface. This is what lets the same navigation stack serve a reflector-navigated facility and a natural-feature facility.

**Uncertainty handling.**
- **[FACT]** AMCL and SLAM Toolbox both emit covariance-bearing poses [R06-S19][R06-S37]. Nav2 BT conditions exist to react to controller/planner error codes [R06-S02][R06-S24]. No inspected page describes a first-party "localisation quality gate" that stops navigation when covariance is too large.
- **[REC]** Add a Valtoryn localisation-health node publishing `ok / degraded / lost` from covariance, scan-match response, innovation, and TF age; the behaviour tree and speed limiter consume it. Thresholds are **[UNRESOLVED]** and must come from hardware data.

### 3.5 Global path planning

| Planner | Robot model assumed | Feasible (kinematic) paths | Reversing | Collision check | Source |
|---|---|---|---|---|---|
| NavFn | circular holonomic particle; wavefront Dijkstra or A\* | no | no | circular assumed; per-cell check [R06-S29] | [R06-S06][R06-S29] |
| Smac 2D | circular or omnidirectional; A\*, 4 or 8 neighbours | no | no | circular robot assumed [R06-S03] | [R06-S03][R06-S02] |
| Theta\* | 2D holonomic particle; any-angle line segments | no | no | point/particle assumed [R06-S02] | [R06-S07][R06-S02] |
| Smac Hybrid-A\* | SE2; Dubins or Reeds-Shepp; `minimum_turning_radius` default 0.4 m | yes | Reeds-Shepp only | footprint polygon when possible | [R06-S04][R06-S29] |
| Smac State Lattice | arbitrary kinematics via precomputed minimum control sets; includes generator for Ackermann, differential, omni, legged | yes | optional `allow_reverse_expansion` | footprint | [R06-S05][R06-S03] |

- **[FACT]** Smac Hybrid-A\* and State Lattice are described as kinematically feasible and supporting reversing, with example planning times on a roughly 75 m path of 144 ms (Hybrid), 113 ms (Lattice), 243 ms (2D), versus 146 ms for NavFn; usual times below 100 ms and occasionally up to 200 ms; hardware not stated in the page [R06-S03]. Treat as order-of-magnitude only.
- **[FACT]** State Lattice has no costmap downsampler and no minimum-turning-radius parameter because both are fixed when the control set is generated, and the control set is tied to map resolution [R06-S05]. **[REC]** A lattice file is therefore a build artifact derived from the robot profile and the costmap resolution, and should be regenerated and version-checked, never hand-copied between configurations.
- **[FACT]** Hybrid-A\*: `analytic_expansion_max_length` "should never be smaller than 4-5x the minimum turning radius" or planning time spikes [R06-S04]. See Section 5 for a worked check.
- **[FACT]** `goal_heading_mode` can be `DEFAULT`, `BIDIRECTIONAL` or `ALL_DIRECTION`, letting a symmetric or bidirectional vehicle accept either end orientation [R06-S04][R06-S05].
- **[FACT]** Non-feasible planners (NavFn, Theta\*, Smac 2D) are paired with the Rotation Shim controller in the docs, because feasible planners start search from the true heading and need no initial rotation [R06-S10].
- **[FACT]** Smoothers: Simple, Constrained (maintains minimum turning radius), Savitzky-Golay [R06-S02].

### 3.6 Trajectory tracking and control

| Controller | Method | Kinematics (catalogue) | Key config-coupled parameters | Source |
|---|---|---|---|---|
| DWB | Dynamic Window Approach, critic plugins | diff, omni, legged | max/min vel x,y,theta, accel/decel limits, sim_time (example 1.7 s), samples | [R06-S12][R06-S02] |
| Regulated Pure Pursuit | pure pursuit with curvature and proximity speed regulation; optional dynamic-window variant | diff, Ackermann, legged | `max_linear_vel`, accel/decel limits, lookahead, `regulated_linear_scaling_min_radius`, `allow_reversing` | [R06-S09] |
| MPPI | sampling MPC with critics; motion models Diff/Omni/Ackermann | diff, omni, Ackermann | `vx_max/vx_min/vy_max/wz_max`, `ax_*/ay_*/az_max`, `min_turning_r`, horizon `time_steps*model_dt`, `consider_footprint` | [R06-S08] |
| Graceful | smooth pose-following control law (Park and Kuipers) | diff, omni, legged | lookahead, velocity limits, footprint scaling with speed | [R06-S11] |
| Rotation Shim | rotate in place to path heading, then hand over to a primary controller | diff, omni (in-place rotation) | angular thresholds, `max_angular_accel` | [R06-S10] |

- **[FACT]** MPPI: batch default 1000 trajectories; `time_steps` default 56 and `model_dt` 0.05 s, prediction horizon = their product; the docs claim 100+ Hz on a "modest" 4th-generation i5 [R06-S08]. The default `consider_footprint` is `false` for both the trajectory validator and critics, in which case a circular point-cost check is used; polygon (SE2) footprint cost is optional and more expensive [R06-S08]. **[REC]** Any non-circular configuration (rectangular AMR, pallet-carrying) must set `consider_footprint: true` and have that choice validated by test, since the default assumes a circular robot.
- **[FACT]** MPPI: the trajectory validator does not need to check dynamic or kinematic constraints because sampled trajectories are guaranteed to lie within the motion model [R06-S08]. Velocity Deadband and Twirling critics exist for hardware limits and holonomic vehicles respectively [R06-S08].
- **[FACT]** MPPI costmap sizing: if the prediction horizon at maximum speed is longer than the local costmap half-width, speeds are artificially limited [R06-S08] (worked in Section 5).
- **[FACT]** RPP slows with path curvature and with proximity to obstacles, uses adaptive lookahead, and includes a collision-detection projection of `max_allowed_time_to_collision_up_to_carrot` (default 1.0 s) using the footprint; `use_rotate_to_heading` and `allow_reversing` cannot both be true [R06-S09]. The paper cited for RPP is Macenski et al., Autonomous Robots, 2023 [R06-S09].
- **[FACT]** Rotation Shim hand-off speed is approximately `min(rotate_to_heading_angular_vel, sqrt(2*max_angular_accel*angular_disengage_threshold))`, which with defaults is stated as 1.59 rad/s, and should not exceed the primary controller's angular limit [R06-S10].
- **[FACT]** The Graceful controller expands the footprint with speed (default up to 125% at maximum speed) and retries at lower speed when in collision [R06-S11]. This is a speed-dependent inflation convention that must be validated for any load.
- **[FACT]** Velocity Smoother applies velocity, acceleration and deadband limits per axis `[x, y, theta]` (defaults y = 0, i.e. non-holonomic), runs in open-loop or closed-loop feedback, and zeroes output after `velocity_timeout` (default 1.0 s) without commands [R06-S17]. **[REC]** Holonomic configurations must set the `y` entries; this is easy to miss because the default disables lateral motion.
- **[FACT]** The controller server exposes `failure_tolerance` (default 0.0 s, meaning the action fails immediately on controller exception), `costmap_update_timeout` (0.3 s), progress and goal checker plugins, and a `speed_limit_topic` [R06-S13].
- **[FACT]** `ros2_controllers` describes its controllers as generalised and "ready to use" with Nav2 among other consumers [R06-S50]; that page lists a wheeled-mobile-robot section, but its contents did not render in my fetch, so which drive types are covered is **[UNRESOLVED]**.
- **[FACT]** The `ros2_controllers` `diff_drive_controller` applies velocity, acceleration and jerk limits, stops automatically after `cmd_vel_timeout` (default 0.5 s), and is chainable [R06-S51]. It reads only linear x and angular z of the command [R06-S51].
- **[FACT]** Nav2 offers `TwistStamped` (default) or `Twist` for `cmd_vel` on each node via `enable_stamped_cmd_vel` [R06-S17][R06-S15]. **[REC]** Standardise on stamped commands for latency diagnostics and fix the setting globally.

### 3.7 Obstacle detection and dynamic avoidance

- **[FACT]** Costmap obstacle and voxel layers ingest `LaserScan` and `PointCloud2` with marking and clearing (raytracing) and height limits; range sensors via a range layer; the inflation layer encodes robot-geometry clearance [R06-S33][R06-S02].
- **[FACT]** Collision Monitor takes sensor data directly, bypassing the costmap and trajectory planners, and limits `cmd_vel` at emergency-stop level [R06-S14][R06-S15]. It supports stop, slowdown, limit and approach (time-to-collision) models; polygon, circle, footprint, and `VelocityPolygon` zones (polygon switching by commanded velocity, with a holonomic mode); data from laser scan, point cloud, range, and costmap sources [R06-S15].
- **[FACT]** Safety-relevant defaults: `source_timeout` 2.0 s (robot stopped if source data stale; per-source overrides allowed), `min_points` 4, optional consecutive-cycle debouncing (`trigger_consecutive_points`, `release_consecutive_points`), `base_shift_correction` on by default and recommended odometry rates near 100 Hz [R06-S15].
- **[FACT]** Exclusion zones mask returns from known structure (for example a charging dock or conveyor, or parts of the robot itself such as a mast), anchored to any TF frame; the filter fails safe (no masking) when its transform is unavailable [R06-S15]. This is the documented mechanism for load-carrying attachments and dock approaches.
- **[FACT]** The documentation states the node "does not provide hard real-time safety certifications" and is the CPU-level analogue of a safety-scanner field set [R06-S15]. It also targets obstacles that appear suddenly or approach fast, especially around people or other dynamic agents [R06-S15].
- **[FACT]** The catalogue includes a Follow Object action and Assisted Teleop behaviour (scales teleop to prevent collision) [R06-S02]. MPPI's author states MPPI can avoid dynamic obstacles "fluidly" with appropriate critic weighting [R06-S08], an author claim, not a measured result.
- **[UNRESOLVED]** None of the inspected pages describes pedestrian trajectory prediction or social-navigation rules in first-party Nav2 plugins. Nav2's costmap is a grid of current observations [R06-S21]; **[EST]** this means moving people are treated reactively (re-plan and slow), with no prediction, and the Wait recovery is the documented response to "human traffic" [R06-S02]. Verification against Nav2 source is needed before relying on this.
- **[REC]** Provide at least two independent collision layers: the costmap-based avoidance in the planner/controller, and a Collision Monitor layer on separately configured sensors, plus (outside this document's scope) a certified safety layer.

### 3.8 Recovery behaviours

- **[FACT]** Default behaviour server plugins: `spin`, `backup`, `drive_on_heading`, `wait`; spin/backup collision-check ahead using a look-ahead time of 2.0 s on the costmaps and published footprint [R06-S31]. The docs say backing up or spinning is used "if permissible" [R06-S22].
- **[FACT]** The reference "Navigate To Pose" tree retries the whole navigation task 6 times, replans at 1 Hz, clears the relevant costmap on planner or controller failure, and in the global recovery branch cycles through (round-robin) costmap clearing, a spin of 1.57 rad, a 5 s wait and a 0.30 m back-up at 0.15 m/s; a `GoalUpdated` check keeps it responsive to new goals [R06-S24]. Condition nodes (`WouldAControllerRecoveryHelp`, `WouldAPlannerRecoveryHelp`) gate recovery on error codes [R06-S24].
- **[FACT]** Behaviour trees use BehaviorTree.CPP v4 [R06-S23]; that library advertises first-class asynchronous actions, run-time XML tree loading, and logging/profiling [R06-S52]. Nav2 states that centralising logic in the tree allows formal analysis [R06-S23], which is a project claim.
- **[REC]** The recovery menu is configuration-dependent: Spin requires in-place rotation (diff, omni) and sufficient swept-area clearance with the actual load; BackUp requires rear sensor coverage; Ackermann/tricycle configurations need an alternative (such as re-plan with Hybrid-A\* from the current pose, or request human help). Recovery actions must also respect payload-dependent speed and acceleration limits, which the stock behaviours do not know about **[EST]** (the behaviour server parameters read expose fixed velocity limits per plugin [R06-S31]).
- **[FACT]** The docs note the behaviour server can host a recovery that calls an operator by email, SMS or chat in case of total failure [R06-S22]. **[REC]** In a warehouse, "escalate to the fleet manager and hold safe" should be the terminal recovery, with a defined stopped state.

### 3.9 Autonomous task execution, route graphs and docking

- **[FACT]** `nav2_waypoint_follower` takes ordered waypoints and executes a task-executor plugin at each (wait, photo, wait for input); `stop_on_failure` defaults to true [R06-S30]. The docs lay out two architectures: dumb robot with smart central dispatcher (waypoint follower as one unit of work such as one pick or one aisle) versus smart robot with a custom behaviour tree carrying more logic [R06-S22].
- **[FACT]** The Route Server (`nav2_route`) plans over a predefined directed graph (lanes, allowed areas, teach-and-repeat routes), parsing `geojson` by default; edges are directional; scoring plugins use distance, time, penalty, semantic class, and orientation scorers, plus dynamic edge cost/closure via a service; route operations run on entering/leaving edges or nodes (speed-limit adjustment, collision check, rerouting service, trigger events) [R06-S25][R06-S26][R06-S02]. The graph can be replaced at run time via a service [R06-S26]. The README reports average search times from 0.0031 ms (100 nodes) to 44 ms (1,000,000 nodes) on unstated hardware [R06-S26].
- **[FACT]** Documented usage patterns include: route dense path straight into the controller, or sparse route into the planner to plan between nodes [R06-S26]. The route server docs exist in the Rolling set and in the Jazzy set [R06-S25][R06-S56]. **[UNRESOLVED]** Availability in Kilted/Lyrical was not confirmed (the Kilted URL I tried returned 404; this may be a path difference).
- **[REC]** Route graphs map naturally to warehouse aisles and one-way lanes; they provide a place to store per-edge speed limits and payload-class restrictions as semantic metadata, and are the natural integration point with a multi-robot traffic manager (a later workstream).
- **[FACT]** `opennav_docking`: a dock server with dock plugins (`SimpleChargingDock`, `SimpleNonChargingDock`) for charging stations or non-charging docks such as the end of a conveyor or a pallet; dock database of many dock types and instances; staging pose offset (default -0.7 m); optional external detection pose (AprilTag-compatible rotation offsets); forward or backward docking (`dock_direction`), `rotate_to_dock` for backing into docks without rear sensors; stall detection or battery status for "is docked"; collision checking disabled within `dock_collision_threshold` (default 0.3 m) of the dock pose; control law with default `v_linear_max` 0.24 m/s [R06-S18]. It is "designed to be called by an application BT" rather than inside navigate-to-pose [R06-S18]. It fixes motion in the `odom` frame, recommended to be smooth odometry [R06-S18].
- **[EST]** The built-in docking control law and tolerance parameters are expressed as linear and angular velocity only, so a holonomic strafe-in docking approach would need a custom controller or dock plugin; this is an inference from the parameter list, not a statement in the docs.

### 3.10 Fault detection and diagnostics

- **[FACT]** Lifecycle Manager brings nodes up in order (configure, activate) and down in reverse; it creates bond connections to servers and, if any server is non-responsive or crashes, transitions all managed nodes down (default `bond_timeout` 4.0 s, `bond_heartbeat_period` 0.25 s); it can attempt to reconnect for `bond_respawn_max_duration` (10 s) if respawn is enabled, otherwise manual re-activation is required [R06-S16].
- **[FACT]** ROS 2 managed nodes have primary states Unconfigured, Inactive, Active, Finalized and an ErrorProcessing transition; an error in Active triggers ErrorProcessing; supervision is expected to come from an external manager [R06-S48].
- **[FACT]** The ROS 2 diagnostics system is built around the `/diagnostics` topic with `DiagnosticArray` messages; `diagnostic_updater` helps publish, `diagnostic_aggregator` aggregates by plugin rules, and `diagnostic_remote_logging` forwards diagnostics to remote systems [R06-S45]. `DiagnosticStatus` levels are OK, WARN, ERROR, STALE with name, message, hardware ID and key-value pairs [R06-S46].
- **[FACT]** `ros2_control` hardware components (Actuator, Sensor, System) follow a lifecycle with `on_configure`, `on_activate`, `on_deactivate`, `on_shutdown` and `on_error`; the framework can publish a `control_msgs/HardwareStatus` message with generic health status (OK or ERROR in the example) at a configured rate, with a real-time-safe update method [R06-S49]. The cited page is the development-version documentation, so API stability is **[UNRESOLVED]** for released distributions.
- **[FACT]** Watchdog-like timeouts already in the chain: `diff_drive_controller` `cmd_vel_timeout` 0.5 s [R06-S51]; velocity smoother `velocity_timeout` 1.0 s [R06-S17]; Collision Monitor `source_timeout` 2.0 s [R06-S15]; costmap update timeout 0.3 s [R06-S13]; lifecycle bond timeout 4.0 s [R06-S16]. **[EST]** The lowest of these defaults (0.5 s at the drive layer) bounds how long a stale command can persist at the actuators, but the end-to-end reaction time depends on which node fails and on the other timeouts in the chain; I cannot derive a single number from the sources. **[REC]** Define the fault-reaction time budget per fault class during design and set each timeout from it, not from defaults.
- **[REC]** One shared health vocabulary: every autonomy node publishes `DiagnosticStatus` with a stable `hardware_id` and key-value payload; a Valtoryn supervisor aggregates into robot states (nominal, degraded, hold-safe, fault) and exposes them to the fleet layer. Ownership of the safety-rated stop path is outside this workstream.

---

## 4. Reusable versus configuration-dependent matrix

Legend: **R** = reusable implementation across configurations; **P** = reusable code, per-configuration parameters/assets; **C** = configuration-specific implementation or plugin choice. Rationale and recommendations are **[REC]** throughout; the "Evidence" column gives the factual basis.

| # | Function | Class | Reusable core | Configuration-dependent inputs | Evidence | [REC] rationale |
|---|---|---|---|---|---|---|
| 1 | Frame contract (REP-105 TF tree) | R | `map -> odom -> base_link -> sensors` | sensor extrinsics (static transforms from robot description) | [R06-S20] | Every Nav2 and localisation component assumes it; a single contract is what makes plugins swappable |
| 2 | Lifecycle bring-up, bond supervision | R | Lifecycle manager ordering, bond timeouts policy | node list, timeouts per fault-reaction budget | [R06-S16][R06-S48] | Pure mechanism; only the node list and timeouts vary |
| 3 | Behaviour-tree skeleton for navigation, retry and recovery sequencing | R | BT XML and custom nodes (BehaviorTree.CPP v4) | recovery selection, retry counts | [R06-S23][R06-S24][R06-S52] | Task logic and error handling should be identical for every robot; configurations only enable/disable recovery branches |
| 4 | Task API (goal, waypoint, dock, undock, route) | R | Action interface and task executor plugin set | task executors that touch payload hardware | [R06-S30][R06-S22] | A fleet manager must command heterogeneous robots uniformly |
| 5 | Diagnostics schema and aggregation | R | `/diagnostics` conventions, aggregator rules | `hardware_id`, thresholds | [R06-S45][R06-S46] | Uniform health vocabulary |
| 6 | Hardware-health publication from driver layer | P | ros2_control lifecycle and `HardwareStatus` use | per-actuator fault codes | [R06-S49] | Interface shared, content per hardware |
| 7 | Occupancy map storage and serving | R | Map server, grid message | map resolution (must match lattice), map version | [R06-S32][R06-S47][R06-S05] | Same asset type for every robot; lattice resolution coupling is a compatibility check |
| 8 | Zone masks (keep-out, speed, lane, parameter zones) | P | Costmap filters, mask authoring pipeline | payload-class variants of speed masks, footprint-inflated keepout | [R06-S27][R06-S28][R06-S21] | Facility knowledge is robot-independent; its effect on a given robot depends on footprint and limits |
| 9 | Route graph | P | Route server, geojson graph | per-edge payload/size restrictions, edge speed metadata | [R06-S25][R06-S26] | Graph is facility data; edge admissibility depends on robot class |
| 10 | SLAM / mapping algorithm | P | SLAM Toolbox (or alternative) as a map-building tool | lidar model, mounting frame, FOV, range limits | [R06-S37][R06-S36] | Offline procedure; stored maps record sensor metadata (ABI note on mount frame) |
| 11 | Localisation provider interface | R | `map -> odom` contract + health topic | which provider (AMCL, SLAM Toolbox, reflector, marker) | [R06-S20][R06-S44][R06-S19] | Interface reusable; provider is facility- and sensor-dependent |
| 12 | AMCL motion model | C | AMCL | diff, omni, or custom plugin for other kinematics | [R06-S19] | Only two stock models |
| 13 | Odometry source and covariance | C | `robot_localization` EKF/UKF pipeline | wheel geometry, slip, IMU, calibrated covariance | [R06-S34][R06-S51] | Slip and geometry are drivetrain-specific |
| 14 | Footprint (circle or polygon, dynamic) | C | Dynamic `~/footprint` mechanism | polygon per payload state, overhang | [R06-S29][R06-S22] | Footprint changes with the load and attachments |
| 15 | Global planner choice | C | Planner server, plugin selection | kinematic class and need for reversing/feasibility | [R06-S02][R06-S03] | 2D planners for circular holonomic; Hybrid/Lattice for non-holonomic and non-circular |
| 16 | Lattice control set or Hybrid turning radius | C | Generator script | min turning radius, wheelbase, heading bins, resolution | [R06-S05][R06-S04] | Build artifact from the robot profile |
| 17 | Local controller choice and motion model | C | Controller server, plugin selection | kinematic class | [R06-S02][R06-S08] | Catalogue support differs per plugin |
| 18 | Velocity/acceleration/jerk limits | C | Velocity smoother, drive-controller limits | per-axis limits, payload-dependent | [R06-S17][R06-S51] | Dynamics depend on mass and traction |
| 19 | Rotation behaviour (rotate-to-heading, shim) | C | Rotation shim | exists only if in-place rotation is possible | [R06-S10][R06-S09] | Not applicable to Ackermann |
| 20 | Collision Monitor zones | C | Collision Monitor node, velocity-polygon mechanism | polygon geometry, stopping distance, sensor placement and FOV, exclusion zones | [R06-S15] | Depends on stopping distance, footprint and what the sensors can see |
| 21 | Costmap sensor layers | P | Obstacle/voxel/range layers | sensor topic, height window, range, clearing | [R06-S33] | Layers reusable; sensor geometry sets values |
| 22 | Recovery set | P | Behaviour server, BT branches | which recoveries are permitted | [R06-S31][R06-S24] | Spin and back-up invalid for some configurations |
| 23 | Docking | C | Dock server, dock database | dock plugin, geometry, approach direction, detector, contact threshold | [R06-S18] | Docking geometry is robot- and dock-specific |
| 24 | Speed limiting by payload | C | Speed-limit topic path | payload-to-limit table | [R06-S27][R06-S13] | Stock filter provides spatial limits only |
| 25 | Localisation health and degraded-mode policy | R | Health node and BT conditions | threshold values | none (Valtoryn proposal) | Must be uniform; thresholds from hardware data |

**Design rule [REC].** Keep one **robot profile** (declarative, versioned) containing: kinematic class; footprint polygons per payload state; per-axis velocity/acceleration/jerk limits per payload state; minimum turning radius or equivalent; sensor table (mount pose, FOV, range, update rate, frame); safety zone definitions tied to stopping-distance calculations; dock definitions; odometry calibration; permitted recoveries. A generator emits Nav2 parameters, the lattice file, Collision Monitor polygons and the costmap footprint, and a validator rejects inconsistent combinations (for example MPPI Ackermann model with a Rotation Shim, `consider_footprint: false` with a non-circular footprint, or a lattice resolution that disagrees with the costmap).

---

## 5. Worked calculations

All inputs below are either documentation defaults (cited) or hypothetical values marked **[EST]**; none describes a real Valtoryn robot.

**5.1 MPPI horizon versus local costmap.**
- Horizon = `time_steps * model_dt` = 56 x 0.05 s = 2.8 s **[CALC]** from defaults [R06-S08].
- Required look-ahead distance = horizon x `vx_max`. At the default 0.5 m/s: 1.4 m; the docs say the costmap half-width must be at least this [R06-S08].
- Hypothetical warehouse AMR at 1.5 m/s **[EST]**: 2.8 s x 1.5 m/s = 4.2 m radius, so a local costmap of at least about 8.4 m wide **[CALC]**, with proportionally larger path-follow offsets. The Nav2 example uses a 3 m costmap [R06-S33].
- Implication: speed, horizon, costmap size and compute cost are coupled and cannot be copied between a slow indoor configuration and a faster one.

**5.2 Stopping-zone sizing for Collision Monitor.**
- Stopping distance d = v²/(2a) + v·t_latency (standard kinematics; **[EST]** formula, not from a cited source).
- Inputs: v = 1.0 m/s **[EST]**; a = 2.5 m/s² (the velocity smoother default `max_decel` magnitude [R06-S17]); t_latency = 0.2 s **[EST]**, covering sensor, processing and actuator delay.
- d = 1.0²/(2 x 2.5) + 1.0 x 0.2 = 0.2 + 0.2 = 0.4 m **[CALC]**.
- If a loaded configuration can only decelerate at 1.0 m/s² **[EST]**: d = 0.5 + 0.2 = 0.7 m **[CALC]**. The same hardware therefore needs a larger stop polygon when loaded; the stock `VelocityPolygon` switches on commanded velocity, not on payload [R06-S15], so payload state must select a different polygon set or parameter set **[REC]**.
- The documentation recommends odometry near 100 Hz for `base_shift_correction`, which adds on average about `1/(2 x odom_rate)` delay: at 100 Hz that is 5 ms [R06-S15] **[CALC]**.

**5.3 Hybrid-A\* analytic-expansion limit.**
- The docs require `analytic_expansion_max_length` of at least 4 to 5 times the minimum turning radius [R06-S04].
- Default `minimum_turning_radius` 0.4 m gives 1.6 to 2.0 m minimum, below the default 3.0 m **[CALC]**.
- Hypothetical Ackermann/tricycle vehicle with 2.0 m turning radius **[EST]**: needs 8 to 10 m **[CALC]**, so the default 3.0 m would cause "planning times will begin to spike" per [R06-S04]. The parameter set cannot be shared across such vehicles.

**5.4 Rotation Shim hand-off.**
- Stated formula and default result: min(1.8, sqrt(2 x 3.2 x 0.3925)) = 1.59 rad/s [R06-S10]. Re-check **[CALC]**: 2 x 3.2 x 0.3925 = 2.512; sqrt = 1.585 rad/s, matching the doc.
- A configuration with a primary controller angular limit below 1.59 rad/s (for example a heavy rotating platform) must lower `rotate_to_heading_angular_vel` or `angular_disengage_threshold`.

---

## 6. Failure modes and what must be validated on hardware

No hardware exists; this section lists tests to perform when it does. Acceptance thresholds are **[UNRESOLVED]** and should be derived from the safety and performance requirements of other workstreams, not from this document.

| Failure mode | Cause (source-supported where noted) | Effect | Mitigations [REC] | Hardware validation |
|---|---|---|---|---|
| Localisation drift or ambiguity in long aisles | featureless, repetitive geometry; scan matching ambiguous [R06-S43][R06-S55] | pose slips along aisle; docking and pick-point errors | add features or reflectors; fuse wheel odom and IMU; localisation-health gate | Drive full aisle lengths repeatedly, both directions, with dynamic pallets; log pose versus ground truth reference |
| Map staleness from racking and pallet changes | changed environment; SLAM Toolbox lifelong mode is experimental [R06-S37] | localisation mismatch | scheduled remap with serialised sessions; version maps; keep dynamic obstacles out of static map | Compare scans to map after a representative re-slot |
| Glass, mirrors, shrink-wrap, polished floor | specular reflection or transmission [R06-S42][R06-S43] | missing obstacles, ghost structure | mask or cover surfaces; second sensor modality; keep-out zones | Test with each facility surface type at several approach angles |
| Reflector occlusion or false reflections | fewer than three reflectors, close reflector pairs, windows or steel [R06-S44] | localiser loses fix | design reflector layout; mixed contour mode | Occlusion walk-through with load and forks in view |
| Wheel slip changes odometry | floor, load, acceleration | EKF input biased | calibrate covariance per payload; limit acceleration | Slip tests on worst floor with maximum payload |
| Overshoot or late stop under load | payload raises stop distance (Section 5.2) | collisions; zone violation | payload-aware limits and polygons | Measured stop distance versus speed and payload |
| Footprint mismatch | load overhang not in footprint [R06-S22][R06-S29] | scraping racks | dynamic footprint topic on pick/place | Measure swept area on turns with each payload |
| Collision monitor false stops | `min_points` too low, noise, dock structures [R06-S15] | throughput loss, jerky motion | debouncing, exclusion zones | False-trigger rate in clean and dusty conditions |
| Collision monitor misses | zone too small, sensor FOV gaps | impact | zone design from stopping distance; overlapping FOVs | Approach tests with test objects at each side, at speed |
| Source stale | sensor driver dies; timeout 2.0 s default [R06-S15] | stop after timeout | shorten per-source timeout; diagnostics | Unplug each sensor during motion, record reaction |
| Server crash | node crash; bond loss tears down stack [R06-S16] | robot stops | respawn policy; hold-safe state | Kill each node during motion; verify stop and recovery behaviour |
| Planner infeasible for kinematics | 2D planner on non-holonomic robot [R06-S10] | oscillation, impossible turns | choose feasible planner; shim | Tight-corner and aisle-entry trials |
| Recovery unsafe | blind spin or back-up in congested aisle [R06-S31][R06-S24] | contact with rack or person | configuration-specific recovery set; hold and escalate | Trigger each recovery with obstacles at rear and side |
| Docking failure | detector loss, geometry drift, contact threshold [R06-S18] | no charge or misalignment | retries (default 3), timeouts, re-stage | Dock from varied start poses and lighting, count success |
| Speed filter lag | mask applies at robot pose without look-ahead [R06-S27] | entering zone too fast | enable path look-ahead | Zone entry speed measurement |
| TF or time-sync fault | clock skew, missing transform | stale commands, wrong pose | TF-age diagnostics; common time source | Inject latency and clock offset |
| Controller compute overrun | MPPI batch size, horizon, footprint check [R06-S08] | missed cycles | pin compute budget; profile on target | Loop-rate histogram under full load |

**Validate regardless of simulation results [REC].** Real stopping distances and decelerations at each payload; odometry slip and calibration; sensor FOV and blind spots with the robot's own structure; localisation repeatability in the real facility; lidar behaviour on real surfaces; dock approach tolerances; end-to-end fault-reaction times; CPU load on the target computer.

---

## 7. What is established versus what is Valtoryn assumption

| Statement | Status |
|---|---|
| Nav2 provides plugin servers, behaviour trees, costmap filters, a collision monitor, a route server, a docking server, and a lifecycle manager | **[FACT]** [R06-S22][R06-S14][R06-S25][R06-S18][R06-S16] |
| Nav2 supports differential, omni, Ackermann and legged robots | **[FACT]**, per-plugin as tagged in [R06-S02]; the framework-level claim is a project statement [R06-S01] |
| Nav2 AMCL supports Ackermann out of the box | **False per docs**: only diff and omni models [R06-S19] |
| Collision Monitor is safety-certified | **False per docs** [R06-S15] |
| Nav2 predicts pedestrian motion | **[UNRESOLVED]**, not found in sources read |
| SLAM Toolbox handles long rack aisles reliably | **[UNRESOLVED]**; no inspected evidence |
| Nav2 is the right foundation for Valtoryn | **Valtoryn assumption [REC]**; this document supports it as the baseline candidate but does not decide it |
| Differential drive is the first reference configuration | Project premise given in the brief, not a Nav2 fact |
| Payload-dependent limits can be added via BT/parameters/speed topic | **[REC]**; no stock payload mechanism found in the docs read |

---

## 8. Implications and recommendations for Valtoryn (all [REC])

1. **Adopt Nav2 as the baseline candidate behind an abstraction.** Reasons: documented per-plugin kinematic coverage, active support for several distributions [R06-S01], a route server, a docking server and a collision monitor. Keep Valtoryn interfaces (task API, health, profile) independent of Nav2 so a plugin or the whole stack can be replaced.
2. **Define the robot profile and generator now**, before writing any controller code. It is the main mechanism for reuse across diff, omni, Ackermann and other chassis (Section 4).
3. **Pin one ROS 2 / Nav2 distribution** and record the parameter schema version in each profile; the MPPI example shows parameter naming differs between distributions [R06-S57][R06-S08].
4. **Planner/controller defaults for the diff-drive reference.** Candidate combination, to be confirmed by hardware trials: Smac 2D or Hybrid/Lattice (if a rectangular footprint is a constraint) with Rotation Shim and Regulated Pure Pursuit or MPPI. Rationale: Rotation Shim and RPP are documented for rotating-in-place platforms [R06-S10][R06-S09]; MPPI requires footprint checking enabled and compute validation [R06-S08].
5. **Treat the localiser as a swappable `map -> odom` provider with a health state**; implement AMCL or SLAM Toolbox localisation first, leave a reflector/marker provider as a planned alternative [R06-S44].
6. **Version facility assets separately** (SLAM map, filter masks, route graph, dock database) and record sensor/frame metadata with each map.
7. **Make payload state a first-class input** that switches footprint, limits and Collision Monitor zone sets. The stock components expose the mechanisms (footprint topic, speed-limit topic, polygon topics) but no payload logic [R06-S22][R06-S27][R06-S15].
8. **Define fault-reaction budgets per fault class** and derive every timeout from them; replace the defaults catalogued in Section 3.10.
9. **Run an early "aisle and surface" characterisation campaign** with the first real robot (Section 6), because the largest uncertainty (aisle geometry, glass and reflective surfaces, dynamic racking) is not resolved by any source read.
10. **Prefer SLAM Toolbox for mapping and keep the LGPL-2.1 obligation visible** [R06-S37]; track RTAB-Map's nonfree OpenCV caveat if a vision configuration is added [R06-S40]; do not build on Cartographer without a maintenance plan [R06-S38].

---

## 9. Limitations of this research

- Documentation-only; no code, tests, builds or measurements.
- Nav2 pages are mostly from the Rolling (development) docs. Defaults and plugin availability differ in released distributions; only MPPI and Route Server pages were cross-checked against Jazzy.
- Performance figures (MPPI at 100+ Hz, planner times, SLAM scale, route-server timings) are vendor/author claims on unspecified or loosely specified hardware.
- Warehouse-specific evidence on SLAM failure is thin: one weak vendor article, one 2008 research paper on mirrors/windows, one subterranean degeneracy abstract. Search-result snippets about 2D lidar degeneracy were not opened and are not cited.
- The Cartographer description rests on the repository README and the walkthrough page, not on the original paper. RTAB-Map claims rest on the project home page, not the journal papers.
- Reflector localisation evidence comes from one manufacturer manual; other vendors and ROS integration were not examined.
- `ros2_control` hardware-status information is from development-version documentation.
- Dynamic-obstacle and people-handling conclusions are partly negative (nothing found), which is weaker than a source-code review.

## 10. Unresolved questions

1. Quantified localisation error of AMCL and SLAM Toolbox localisation in rack aisles with dynamic pallets — needs hardware trials or warehouse benchmarks.
2. Whether Nav2 plugins handle people prediction or social rules — needs source review or Nav2 maintainer statement.
3. Route Server availability and maturity per released distribution (Kilted, Lyrical) — check release notes.
4. Map file format details in Nav2 Map Server (resolution, origin, thresholds) — read the Map Server README.
5. Whether `robot_localization` floors zero odometry covariance — read its configuration documentation (the `docs.ros.org` page was blocked by an anti-bot challenge).
6. How the stock docking control law behaves for holonomic platforms — read the `opennav_docking` source.
7. Payload-aware limiting strategy (BT parameter updates, Zone Parameter Filter, external node publishing `speed_limit`) — prototype and measure.
8. Fault-reaction time budgets and localisation-health thresholds — derive from safety analysis and measured data.
9. Whether Nav2 Lyrical's codename is "Luth" or "Lynx" — immaterial to engineering but inconsistent across fetches.

---

## Sources

| ID | Title | Organization / author | URL | Published / revision date | Accessed | What it supports |
|---|---|---|---|---|---|---|
| R06-S01 | NAV2 — Nav2 Docs (home) | Nav2 / Open Navigation | https://docs.nav2.org/rolling/ | n/a (not stated on page) | 2026-11-07 | Kinematics claim, distribution support levels, BT/server architecture overview |
| R06-S02 | Navigation Plugins | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/navigation_plugins/ | n/a (not stated on page) | 2026-11-07 | Plugin catalogue, drivetrain support tags, layers, filters, BT nodes, route plugins |
| R06-S03 | Smac Planner | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/planners_plugins/smac/ | n/a (not stated on page) | 2026-11-07 | Smac 2D/Hybrid/Lattice scope, feasibility, reversing, example planning times |
| R06-S04 | Smac Hybrid-A* Planner | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/planners_plugins/smac/smac_hybrid/configuring_smac_hybrid/ | n/a (not stated on page) | 2026-11-07 | Hybrid-A* parameters, turning radius, analytic expansion rule, goal heading modes |
| R06-S05 | Smac State Lattice Planner | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/planners_plugins/smac/smac_lattice/configuring_smac_lattice/ | n/a (not stated on page) | 2026-11-07 | Lattice control sets, no turning-radius parameter, resolution coupling, reverse expansion |
| R06-S06 | NavFn Planner | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/planners_plugins/configuring_navfn/ | n/a (not stated on page) | 2026-11-07 | NavFn holonomic wavefront planner |
| R06-S07 | Theta Star Planner | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/planners_plugins/thetastar/configuring_thetastar/ | n/a (not stated on page) | 2026-11-07 | Theta* any-angle planning |
| R06-S08 | Model Predictive Path Integral Controller | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/controller_plugins/mppi_controller/configuring_mppic/ | n/a (not stated on page) | 2026-11-07 | MPPI motion models, defaults, footprint option, horizon/costmap coupling |
| R06-S09 | Regulated Pure Pursuit | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/controller_plugins/configuring_regulated_pp/ | n/a (not stated on page) | 2026-11-07 | RPP regulation, collision projection, rotate/reverse constraint |
| R06-S10 | Rotation Shim Controller | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/controller_plugins/configuring_rotation_shim_controller/ | n/a (not stated on page) | 2026-11-07 | Rotation shim use, pairing with non-feasible planners, hand-off speed formula |
| R06-S11 | Graceful Controller | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/controller_plugins/configuring_graceful_motion_controller/ | n/a (not stated on page) | 2026-11-07 | Graceful controller law, speed-dependent footprint scaling |
| R06-S12 | DWB Controller | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/controller_plugins/dwb_controller/ | n/a (not stated on page) | 2026-11-07 | DWB structure, critics, kinematic parameters |
| R06-S13 | Controller Server | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/controller_server/ | n/a (not stated on page) | 2026-11-07 | Controller server parameters, failure tolerance, speed-limit topic, hosts local costmap |
| R06-S14 | Collision Monitor | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/collision_monitor/ | n/a (not stated on page) | 2026-11-07 | Collision monitor and detector node scope |
| R06-S15 | Collision Monitor Node | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/collision_monitor/configuring_collision_monitor_node/ | n/a (not stated on page) | 2026-11-07 | Zone models, sources, timeouts, exclusion zones, non-certified statement |
| R06-S16 | Lifecycle Manager | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/configuring_lifecycle_manager/ | n/a (not stated on page) | 2026-11-07 | Bond monitoring, ordered bring-up, shutdown on non-responsive server |
| R06-S17 | Velocity Smoother | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/configuring_velocity_smoother/ | n/a (not stated on page) | 2026-11-07 | Per-axis velocity/acceleration limits, timeout, feedback modes |
| R06-S18 | Docking Server | Nav2 (opennav_docking) | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/configuring_docking_server/ | n/a (not stated on page) | 2026-11-07 | Dock plugins, docking geometry parameters, detection, collision threshold |
| R06-S19 | AMCL | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/others/configuring_amcl/ | n/a (not stated on page) | 2026-11-07 | AMCL motion models, recovery parameters, defaults |
| R06-S20 | State Estimation | Nav2 | https://docs.nav2.org/rolling/getting_started/navigation_concepts/state_estimation/ | n/a (not stated on page) | 2026-11-07 | REP-105 frames, odometry/localisation roles, no lidar requirement |
| R06-S21 | Environmental Representation | Nav2 | https://docs.nav2.org/rolling/getting_started/navigation_concepts/environmental_representation/ | n/a (not stated on page) | 2026-11-07 | Costmaps, layers, filters, other representations |
| R06-S22 | Navigation Servers | Nav2 | https://docs.nav2.org/rolling/getting_started/navigation_concepts/navigation_servers/ | n/a (not stated on page) | 2026-11-07 | Server/plugin model, footprint topic, waypoint follower architectures, recoveries, route server |
| R06-S23 | Behavior Trees | Nav2 | https://docs.nav2.org/rolling/getting_started/navigation_concepts/behavior_trees/ | n/a (not stated on page) | 2026-11-07 | BehaviorTree.CPP v4 use, subtree composition |
| R06-S24 | Navigate To Pose (recovery tree) | Nav2 | https://docs.nav2.org/rolling/getting_started/nav2_behavior_trees/trees/nav_to_pose_recovery/ | n/a (not stated on page) | 2026-11-07 | Retry counts, replanning rate, recovery sequence values |
| R06-S25 | Route Server | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/route_server/configuring_route_server/ | n/a (not stated on page) | 2026-11-07 | Route server scope and parameters |
| R06-S26 | Nav2 Route Server README | Nav2 (Macenski, Open Navigation) | https://raw.githubusercontent.com/ros-navigation/navigation2/main/nav2_route/README.md | n/a (not stated on page) | 2026-11-07 | Route server features, architectures, search-time metrics |
| R06-S27 | Speed Filter Parameters | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/costmap_2d/costmap_filters/speed_filter/ | n/a (not stated on page) | 2026-11-07 | Speed limit mask mapping, path look-ahead |
| R06-S28 | Keepout Filter Parameters | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/costmap_2d/costmap_filters/keepout_filter/ | n/a (not stated on page) | 2026-11-07 | Keepout behaviour and lethal-cost override |
| R06-S29 | Setting Up the Robot's Footprint | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/first_time_robot_setup_guide/footprint/setup_footprint/ | n/a (not stated on page) | 2026-11-07 | Footprint vs robot_radius, planner collision-check assumptions, dynamic footprint |
| R06-S30 | Waypoint Follower | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/waypoint_follower/ | n/a (not stated on page) | 2026-11-07 | Waypoint following, task executor plugins, stop_on_failure |
| R06-S31 | Behavior Server | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/configuring_behavior_server/ | n/a (not stated on page) | 2026-11-07 | Default behaviours, collision look-ahead for spin and back-up |
| R06-S32 | Map Server | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/map_server/configuring_map_server/ | n/a (not stated on page) | 2026-11-07 | Map loading from YAML, map topic |
| R06-S33 | Mapping and Localization (setup guide) | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/first_time_robot_setup_guide/sensors/mapping_localization/ | n/a (not stated on page) | 2026-11-07 | SLAM Toolbox and AMCL recommendation, costmap layers, cost range |
| R06-S34 | Smoothing Odometry using Robot Localization | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/first_time_robot_setup_guide/odom/setup_robot_localization/ | n/a (not stated on page) | 2026-11-07 | EKF/UKF fusion inputs, outputs, world_frame guidance |
| R06-S35 | ReinitializeGlobalLocalization (BT node) | Nav2 | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/bt_plugins/actions/ReinitializeGlobalLocalization/ | n/a (not stated on page) | 2026-11-07 | Global relocalisation trigger for kidnapped robot |
| R06-S36 | SLAM Toolbox: SLAM for the dynamic world (JOSS paper PDF) | Macenski, S.; Jambrecic, I. | https://joss.theoj.org/papers/10.21105/joss.02783.pdf | 2021-05-13 (published) | 2026-11-07 | SLAM Toolbox features, modes, serialisation, licence, scale claims |
| R06-S37 | slam_toolbox repository README | Macenski (SteveMacenski/slam_toolbox) | https://github.com/SteveMacenski/slam_toolbox | n/a (not stated on page) | 2026-11-07 | Modes, lifelong mapping status, localisation mode, services, covariance scaling, serialisation note, benchmarks, licence |
| R06-S38 | Cartographer repository | cartographer-project | https://github.com/cartographer-project/cartographer | n/a (not stated on page) | 2026-11-07 | Maintenance status, Apache-2.0 |
| R06-S39 | Cartographer ROS: algorithm walkthrough | Cartographer ROS documentation | https://google-cartographer-ros.readthedocs.io/en/latest/algo_walkthrough.html | n/a (not stated on page) | 2026-11-07 | Local vs global SLAM structure |
| R06-S40 | RTAB-Map home page | IntRoLab / M. Labbé | https://introlab.github.io/rtabmap/ | n/a (not stated on page) | 2026-11-07 | RTAB-Map approach, multi-session, licence caveat |
| R06-S41 | rtabmap repository | IntRoLab | https://github.com/introlab/rtabmap | n/a (not stated on page) | 2026-11-07 | ROS 2 distribution binaries listed |
| R06-S42 | Dealing with Laser Scanner Failure: Mirrors and Windows | Yang, S.-W.; Wang, C.-C. (ICRA) | https://www.csie.ntu.edu.tw/~bobwang/Papers/yang_icra08.pdf | 2008 (year per proceedings; not stated on page) | 2026-11-07 | Laser failure on mirrors/glass, effect on mapping and navigation |
| R06-S43 | Common Indoor SLAM Failure Scenarios and How to Fix Them (weak source) | Shanghai Slamtec Co., Ltd. | https://www.slamtec.com/en/news/detailen/common-indoor-slam-failure-scenarios-and-how-to-fix-them | n/a (not stated on page) | 2026-11-07 | Vendor claims on glass and long-corridor failures; indicative only |
| R06-S44 | NAV350 2D LiDAR sensor operating instructions | SICK AG | https://www.sick.com/media/docs/3/43/143/operating_instructions_nav350_laser_positioning_sensor_en_im0040143.pdf | 2024-11-29 (document revision) | 2026-11-07 | Reflector-based AGV localisation capabilities and constraints |
| R06-S45 | ros/diagnostics repository | ROS maintainers | https://github.com/ros/diagnostics | n/a (not stated on page) | 2026-11-07 | Diagnostics packages and data flow; Lyrical Luth naming |
| R06-S46 | DiagnosticStatus.msg | ROS (ros2/common_interfaces) | https://raw.githubusercontent.com/ros2/common_interfaces/rolling/diagnostic_msgs/msg/DiagnosticStatus.msg | n/a (not stated on page) | 2026-11-07 | Diagnostic levels and fields |
| R06-S47 | OccupancyGrid.msg | ROS (ros2/common_interfaces) | https://raw.githubusercontent.com/ros2/common_interfaces/rolling/nav_msgs/msg/OccupancyGrid.msg | n/a (not stated on page) | 2026-11-07 | Occupancy grid message semantics |
| R06-S48 | Managed nodes (node lifecycle design) | Biggs, G.; Foote, T. (ROS 2 design) | https://design.ros2.org/articles/node_lifecycle.html | 2021-02 (last modified) | 2026-11-07 | Lifecycle states and error handling |
| R06-S49 | Writing a Hardware Component | ros2_control | https://control.ros.org/rolling/doc/ros2_control/hardware_interface/doc/writing_new_hardware_component.html | n/a (documentation labelled Rolling Sep 2026) | 2026-11-07 | Hardware lifecycle, HardwareStatus health reporting |
| R06-S50 | ros2_controllers index | ros2_control | https://control.ros.org/rolling/doc/ros2_controllers/doc/controllers_index.html | n/a (documentation labelled Rolling Nov 2026) | 2026-11-07 | Existence of wheeled-base controllers usable with Nav2 (limited use) |
| R06-S51 | diff_drive_controller | ros2_control | https://control.ros.org/rolling/doc/ros2_controllers/diff_drive_controller/doc/userdoc.html | n/a (documentation labelled Rolling Nov 2026) | 2026-11-07 | Odometry covariance, limits, cmd_vel timeout, wheel parameter sensitivity |
| R06-S52 | BehaviorTree.CPP introduction | BehaviorTree.CPP | https://www.behaviortree.dev/docs/intro | n/a (doc version 4.8 shown) | 2026-11-07 | BT library features |
| R06-S53 | The Marathon 2: A Navigation System | Macenski, S. et al. (IROS 2020) | https://arxiv.org/abs/2003.00368 | 2020-03-01 (v1); 2020-07-14 (v2) | 2026-11-07 | Peer-reviewed description of Nav2 architecture and intent |
| R06-S54 | robot_localization repository | Charles River Analytics / cra-ros-pkg | https://github.com/cra-ros-pkg/robot_localization | n/a (not stated on page) | 2026-11-07 | Package description (nonlinear state estimation nodes) |
| R06-S55 | DARE-SLAM: Degeneracy-Aware and Resilient Loop Closing in Perceptually-Degraded Environments | Ebadi, K. et al. (arXiv) | https://arxiv.org/abs/2102.05117 | 2021-02-09 | 2026-11-07 | Geometric degeneracy as a documented SLAM problem class (subterranean focus) |
| R06-S56 | Route Server (Jazzy documentation) | Nav2 | https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/core_servers/route_server/configuring_route_server/ | n/a (not stated on page) | 2026-11-07 | Route server documented in Jazzy docs set |
| R06-S57 | Model Predictive Path Integral Controller (Jazzy documentation) | Nav2 | https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/controller_plugins/mppi_controller/configuring_mppic/ | n/a (not stated on page) | 2026-11-07 | Distribution-specific MPPI motion-model parameter form |

### Sources that could not be inspected (not cited)

- `docs.ros.org` pages for `robot_localization` and `diagnostic_updater` (blocked by an anti-bot challenge page).
- `control.ros.org` "Hardware Components description" page (404).
- Search-result-only items, not opened: Unipd thesis on laser-triangulation AGV navigation; IEEE/Springer/Wiley degeneracy-detection papers (Ji et al.; Chen et al.; Li et al.; Shi et al.); MIT, ScienceDirect, PMC and arXiv glass-lidar papers; Robotics Stack Exchange and Reddit AMCL threads.
- Nav2 Kilted route-server page (404 at the URL tried); Nav2 BT Navigator page; Nav2 Smac and MPPI GitHub READMEs; Nav2 Map Server README; Cartographer paper (Hess et al., ICRA 2016); RTAB-Map journal papers; SICK NAV310 manual.
