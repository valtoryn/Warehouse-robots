# R04 — Robotics Software Stack Evaluation
> **Status:** Research document — proposed findings, nothing here is implemented.
> **Workstream:** R04 · **Last verified:** 2026-11-07 · **Evidence legend:** see below

## Evidence legend

- **[FACT]** established by a cited source, always followed by a source ID such as [R04-S03].
- **[CALC]** derived by a shown calculation from cited or labelled inputs.
- **[EST]** engineering estimate or assumption (basis stated).
- **[REC]** Valtoryn recommendation or proposal (engineering judgement, not established fact). Nothing in this document describes a Valtoryn capability that exists; every Valtoryn statement is a proposal.
- **[UNRESOLVED]** could not be established from sources actually opened; the text states what would resolve it.

## 1. Scope and method

**Scope.** Evaluate the robotics software stack for the Valtoryn Warehouse Robotics platform: ROS 2 distribution choice, ros2_control, Nav2, SLAM and localisation packages, simulation (Gazebo and alternatives), robot-description formats, DDS/RMW middleware, implementation languages, real-time options, testing/diagnostics tooling, build/CI/container options, and Windows 11 host implications. Output is a recommended baseline stack with version constraints, risks and an upgrade strategy.

**Method and constraints that affect confidence (read these).**

1. Primary sources were official documentation sources, official repositories and metadata (ROS documentation source files, REPs, `ros/rosdistro`, project READMEs, package manifests, GitHub repository metadata).
2. `docs.ros.org` and `www.ros.org` sit behind a bot-protection challenge that the fetch tools could not pass; I did not attempt to defeat it. Where ROS documentation was needed, I read the same documentation as reStructuredText source from the `ros2/ros2_documentation` GitHub repository (rolling branch), or as a mirror embedded in the eProsima Vulcanexus documentation site (a derivative copy of older ROS documentation; labelled "mirror" below and treated as weaker evidence for current-distro statements).
3. Most pages were read through a summarising fetch tool, so the extracted statements are that tool's rendering of the page. Items that matter most were cross-checked: the REP files and the four `rosdistro` distribution files were downloaded and searched locally, and key dates were compared across two sources where both existed.
4. REP-2000 as fetched from `ros-infrastructure/rep` (master) has no Lyrical section and a Rolling note dated May 2025 [R04-S02]; the Lyrical platform data therefore comes from the Lyrical supported-platforms source page [R04-S03], not from REP-2000.
5. No hardware or software was run or benchmarked. No performance numbers in this document are measurements; where a source gives none, this document says so.

## 2. Findings

### 2.1 ROS 2 distributions, lifecycle and platform support

**Release policy [FACT].** REP-2000 states a 12-month release cadence, alternating LTS (even years, about 5 years of support, matched to the Ubuntu LTS standard-support window) and non-LTS (odd years, 1.5 years); a distribution has full Tier 1 support for a single Ubuntu LTS only, with an older LTS possible as Tier 3 on a case-by-case basis [R04-S02]. Tier 1 means frequent CI including the unit test suite; Tier 2 means periodic CI with public build and test results; Tier 3 means community-reported functionality [R04-S02].

**Current distribution list as of 2026-11-07 [FACT].** The documentation release table lists the following [R04-S01]:

| Distribution | Release date | EOL (per Releases table) | LTS? | Notes |
|---|---|---|---|---|
| Lyrical Luth | 2026-05-22 | May 2031 | Yes [R04-S04] | Twelfth ROS 2 release [R04-S04] |
| Kilted Kaiju | 2025-05-23 | December 2026 | No (non-LTS cadence) | REP-2000 text gives "November 2026" as the end of the window [R04-S02] — see discrepancy below |
| Jazzy Jalisco | 2024-05-23 | May 2029 | Yes | |
| Humble Hawksbill | 2022-05-23 | May 2027 | Yes | |
| Makoa Mata-mata (future) | May 2027 | December 2028 | No (odd-year) | Listed as "future distribution" [R04-S01] |
| Rolling Ridley | rolling | n/a | n/a | Development distribution, may contain breaking changes [R04-S01] |

Iron Irwini (EOL 2024-12-04) and older releases are end-of-life [R04-S01].

**Discrepancy to know about [FACT].** The Releases table gives Kilted's EOL as December 2026 [R04-S01]; the REP-2000 text gives the support window as ending November 2026 [R04-S02]. Either way, as of today Kilted is within roughly 1–2 months of EOL [CALC: 2026-11-07 to 2026-11-30 or 2026-12-31]. The LTS flag for Jazzy, Humble and the "no LTS" status of Kilted are inferred from the REP-2000 alternation rule [R04-S02] and the support windows in [R04-S01]; the individual Jazzy/Humble/Kilted release pages I read did not themselves state LTS status [R04-S06][R04-S07][R04-S08].

**Remaining support from today [CALC]:** Humble ends May 2027 (about 6 months); Jazzy ends May 2029 (about 2.5 years); Lyrical ends May 2031 (about 4.5 years). Inputs: dates from [R04-S01]; today = 2026-11-07; exact day-of-month for EOL is not stated, so these are approximate.

**Platform tiers per distribution [FACT].**

| Distribution | Tier 1 | Tier 2 | Tier 3 (selected) | Source |
|---|---|---|---|---|
| Lyrical | Ubuntu 26.04 "Resolute" (amd64, arm64); Windows 11 with Visual Studio 2022 (amd64) | RHEL 10 (amd64) | Ubuntu 24.04 "Noble" (amd64, arm64, arm32; early EOL listed, supported until 2029-06-01), macOS, Debian Trixie, OpenEmbedded/Yocto | [R04-S03][R04-S05] |
| Jazzy | Ubuntu 24.04 (amd64, arm64); Windows 10 with VS2019 (amd64) | RHEL 9 | macOS, Debian Bookworm | [R04-S06] |
| Kilted | Ubuntu 24.04 (amd64, arm64); Windows 10 with VS2019 | RHEL 9 | macOS, Debian Bookworm, Yocto | [R04-S07] |
| Humble | Ubuntu 22.04 (amd64, arm64); Windows 10 with VS2019 | RHEL 8 | Ubuntu 20.04, macOS, Debian Bullseye | [R04-S08] |

Tier 3 platforms require building ROS from source [R04-S03]. For Lyrical, language baselines are C++20 and C17, and Python 3.12–3.14 [R04-S03]. Lyrical's release announcement recommends Ubuntu 26.04 and Windows 11 for newcomers [R04-S05].

**Ecosystem readiness on Lyrical [FACT, snapshot].** The `ros/rosdistro` distribution files (read 2026-11-07) show these released versions [R04-S11]. This shows "released into the distribution file", not that binaries have synced to the public apt repository (sync status not checked).

| Package | Humble | Jazzy | Kilted | Lyrical |
|---|---|---|---|---|
| navigation2 | 1.1.20 | 1.3.14 | 1.4.2 | 1.5.3 |
| ros2_control | 2.54.4 | 4.50.0 | 5.20.0 | 6.13.0 |
| ros2_controllers | 2.54.1 | 4.43.1 | 5.18.1 | 6.10.1 |
| slam_toolbox | 2.6.10 | 2.8.5 | 2.9.0 | 2.10.0 |
| robot_localization | 3.5.5 | 3.8.4 | 3.9.5 | 3.11.0 |
| fuse | absent | 1.1.6 | 1.2.7 | 1.3.4 |
| rtabmap_ros | 0.23.13 | 0.23.13 | 0.23.13 | 0.23.13 |
| ros_gz | 0.244.27 | 1.0.25 | 2.1.19 | 3.0.12 |
| gz_ros2_control | absent (`gazebo_ros2_control`, `ign_ros2_control` present) | 1.2.20 | 2.0.17 | 3.0.9 |
| rmw_zenoh | 0.1.11 | 0.2.13 | 0.6.10 | 0.10.8 |
| rosbag2 | 0.15.17 | 0.26.11 | 0.32.0 | 0.33.4 |
| Gazebo Classic (`gazebo_ros_pkgs`) | present | present | absent | absent |

Additional observations from the same files: `rclrs` is not a released ROS package in any of the four distributions (only `rosidl_rust` appears); `webots_ros2`, `mujoco_vendor` and `mujoco_ros2_control` are released in all four [R04-S11]. Lyrical's release platforms are Ubuntu Resolute, Debian Trixie, RHEL 10 and Fedora 43 [R04-S11].

**Notable Lyrical features relevant to Valtoryn [FACT].** A callback-group events executor for rclcpp (the announcement claims 10–15% lower CPU than the single- and multi-threaded executors; the claim is the announcement's, not independently verified); an asyncio-based node for rclpy; `rosidl::Buffer` zero-copy buffers for `uint8[]` fields (currently only with `rmw_fastrtps_cpp`; Zenoh support planned); URDF 1.2 acceleration and jerk limits (Lyrical onward); rosbag2 remote-control services, Python control APIs, circular recording limits and message-loss reporting; richer `ros2 doctor --report` [R04-S04][R04-S05]. The default RMW is `rmw_fastrtps_cpp` [R04-S03].

### 2.2 ros2_control

**Architecture [FACT].** The Controller Manager (CM) is the entry point; it loads, activates, deactivates and unloads controllers, matches controller-required interfaces to hardware-provided interfaces, and runs the control loop (`update()`: read hardware, update active controllers, write). The Resource Manager abstracts hardware ("hardware components") loaded through `pluginlib`, manages their lifecycle and command/state interfaces. Controllers derive from `ControllerInterface` and are `pluginlib` plugins with a lifecycle-node-based lifecycle [R04-S25]. User interaction is through CM services and the `ros2 control` CLI [R04-S25].

**Hardware component types [FACT].** Three types: System (complex multi-DOF, single logical communication channel, e.g. an industrial robot), Sensor (read-only), Actuator (simple 1-DOF) [R04-S25]. The URDF `<ros2_control>` tag declares each component (`type`, `<hardware><plugin>`, `<joint>`, `<sensor>`, `<gpio>`), command/state interfaces with optional `min`, `max`, `initial_value`, `data_type` (double by default; float32, bool, integer types selectable), custom interface names, and `<group>` tags to share error handling [R04-S36]. There is no generic GPIO publisher; applications need a custom GPIO controller [R04-S36]. The documentation index also lists mock components, asynchronous components and different update rates as supported topics [R04-S95].

**Controllers available [FACT].**

| Category | Controllers in current (Rolling/Lyrical) index [R04-S27] | In Jazzy index [R04-S34] | In Humble index [R04-S35] |
|---|---|---|---|
| Wheeled mobile | Differential Drive, Mecanum Drive, Omni Wheel Drive, Steering Controllers Library (Bicycle, Tricycle, Ackermann), Tricycle | same | Differential Drive, Mecanum Drive, Steering Controllers Library, Tricycle (no Omni listed) |
| Manipulator/other | Admittance, Forward Command, GPIO Command, Joint Trajectory, Motion Primitive, Parallel Gripper, PID | similar plus Effort/Position/Velocity controllers | Admittance, Effort, Forward Command, Gripper, Joint Trajectory, PID, Position, Velocity, GPIO Command |
| Broadcasters | Joint State, IMU, Force-Torque, Range, Pose, GPS, State Interfaces, Magnetometer, Battery State | similar (no Battery listed) | Force-Torque, IMU, Joint State, Range, Pose |

Controller details (Rolling documentation, so exact parameters may differ per distro):

- **diff_drive_controller** commands wheel joint velocity; takes position or velocity feedback (`position_feedback`), supports `open_loop`, subscribes to `~/cmd_vel` as `geometry_msgs/TwistStamped`, publishes `~/odom` and optionally `/tf`, offers `~/set_odometry`, has `cmd_vel_timeout` (default 0.5 s), per-axis velocity/acceleration/jerk limits, odometry covariance parameters, and is documented as real-time safe and chainable [R04-S28]. In Humble the topic type depends on `use_stamped_vel` (default true: `TwistStamped` on `~/cmd_vel`; false: `Twist` on `~/cmd_vel_unstamped`) [R04-S33].
- **mecanum_drive_controller**: four-wheel mecanum, holonomic reference (`linear/x`, `linear/y`, `angular/z` velocity), `TwistStamped` input, odometry, wheel velocity commands, per-axis limits; values are returned unfiltered by design [R04-S29].
- **omni_wheel_drive_controller**: three or more omni wheels at equal angular spacing, `TwistStamped` input, odometry, timeout stop, documented as real-time safe [R04-S31].
- **steering_controllers_library**: bicycle (1 steering + 1 drive joint), tricycle (1 steering + 2 drive), Ackermann (2 steering + 2 drive); inverse kinematics only, no path tracking; front or rear steering; chainable [R04-S30].

**Real-time behaviour [FACT].** The CM main thread attempts `SCHED_FIFO` with priority 50 regardless of kernel; the node parameters `thread_priority` (0–99, default 50), `cpu_affinity` and `lock_memory` (default false on non-RT kernel, true on RT kernel) are documented; `update_rate` defaults to 100 Hz and is read-only; an `rtprio`/`memlock` entry in `/etc/security/limits.conf` for a `realtime` group is required for non-root; in Docker, `--cap-add=sys_nice`, `--ulimit rtprio=99`, `--ulimit memlock=-1`. Overrun detection (`overruns.manage`) is on by default and disabled with sim time. CM services run outside the RT loop, and `get_lifecycle_state()` must not be called inside RT code [R04-S26]. The docs name an RT kernel as lowest jitter and a `linux-lowlatency` kernel as an easier option that "can still help a lot" [R04-S26] (paraphrase of the docs' wording).

**Branch/distro mapping [FACT].** The repository has branches `master` (Rolling and Lyrical), `kilted`, `jazzy`, `humble` [R04-S32]. The Rolling docs state the Rolling branch builds from source against Humble and Jazzy [R04-S25]. The page states the framework is released on Ubuntu and RHEL following REP-2000 [R04-S25]; Windows is not mentioned.

**Not established.** Whether ros2_control is supported on Windows 11 natively: [UNRESOLVED] (the documentation I read lists Ubuntu and RHEL only; resolving requires the Lyrical installation/CI matrix for ros2_control). REP-2005 ("common packages") does not list ros2_control in the version I downloaded [R04-S10] (note that this REP master snapshot is stale relative to 2026, see below).

### 2.3 Nav2

**Status and versions [FACT].** The Nav2 documentation site marks Lyrical and Jazzy "Active Support", Kilted and Humble "Maintained", Iron and Galactic end-of-life [R04-S37]. The repository README lists build status for `humble`, `jazzy` and `lyrical` only [R04-S39]. Released versions per distribution are in the table in 2.1 [R04-S11]. Open Navigation LLC provides leadership/maintenance; sponsors listed include Dexory, NVIDIA, AMD, Polymath Robotics, Stereolabs, 3Laws Robotics and Staer [R04-S39]. The site claims use by "300+ companies" [R04-S37] (marketing claim, unverified). Licensing is per-package: the repository states unmarked files are Apache-2.0, some portions are LGPL-2.1-or-later, BSD-3-Clause or Apache-2.0 AND BSD-3-Clause, and each `package.xml` states its licence [R04-S49]; `nav2_bringup` declares Apache-2.0 [R04-S50]. The Nav2 stack's architecture is behaviour-tree orchestration of independent task servers over action/service interfaces [R04-S37].

**Plugin ecosystem (documented list) [FACT, Rolling docs] [R04-S38].**

- Navigators: NavigateToPose, NavigateThroughPoses, Coverage.
- Controllers (with documented drivetrain support): DWB (differential, omni, legged), TEB (Ackermann, differential, omni), Regulated Pure Pursuit (Ackermann, differential, legged), MPPI (differential, omni, Ackermann), Rotation Shim, Graceful, Vector Pursuit.
- Planners: NavFn, Smac Hybrid-A* (Ackermann, differential, omni, legged), Smac 2D, Smac Lattice (any vehicle including custom, with generator scripts), Theta*.
- Smoothers: Simple, Constrained, Savitzky-Golay.
- Costmap layers: Static, Obstacle, Voxel, Range, Inflation (OpenMP option), Asymmetric Inflation, Denoise, Plugin Container, Spatio-Temporal Voxel, Ground Consistency, Semantic Segmentation, Virtual layers; filters: Keepout, Speed, Binary, Zone Parameter.
- Behaviors: Spin, BackUp, Wait, DriveOnHeading, AssistedTeleop, Clear Costmap.
- Many behaviour-tree nodes (e.g. ComputePathToPose, FollowPath, DockRobot, UndockRobot, ComputeRoute, ComputeAndTrackRoute, ToggleCollisionMonitor).
- Route plugins: edge scorers (distance, time, penalty, semantic, orientation, dynamic edges), route operations (speed-limit adjust, collision monitor, rerouting, event trigger), and a GeoJSON graph parser (the only supported format currently) [R04-S38].
This list is from the Rolling documentation; individual plugins appear in specific releases. Examples that I could attribute to a release from migration guides: Route Server released in Kilted [R04-S40], docking introduced in Jazzy [R04-S40], Vector Object Server, Following Server, Pause/Resume and `nav2_ros_common` in Lyrical [R04-S40][R04-S41]. Each plugin's presence in Humble is not verified: [UNRESOLVED] (resolve by reading the Humble documentation plugin list).

**Docking server [FACT].** `opennav_docking` implements docking and undocking against charging stations or non-charging locations such as a conveyor end or pallet; dock plugins generalise across kinematics, charging methods and sensors; it holds a database of dock types and locations; it is intended to be called by an application BT rather than inside navigate-to-pose; `SimpleChargingDock` is provided; the robot-to-dock control loop defaults to 50 Hz; NVIDIA sponsored it [R04-S43]. Docking can be used with static infrastructure or dynamic docking from Kilted [R04-S42].

**Collision Monitor [FACT].** A separate node operating on sensor data and bypassing costmaps and planners for emergency-stop-level protection; zones are polygons, circles, robot footprint (approach model only) or `VelocityPolygon`s that switch with commanded speed; behaviours are Stop, Slowdown, Limit and Approach (time-to-collision); sources are `LaserScan`, `PointCloud2`, `Range` and (cautiously) Costmap. The documentation says explicitly that it is CPU-level, not a hard-real-time safety certification, and is an analogue of safety-rated scanner functions for users who lack safety-rated hardware [R04-S44]. The Lyrical migration adds a toggle service and BT plugin, exclusion zones and debounce parameters [R04-S41].

**Route Server [FACT].** `nav2_route` computes routes over a predefined navigation graph (nodes and edges, GeoJSON) instead of free-space planning; it can replace free-space planning or provide long-range routing with a planner doing local path generation; customisation is via edge scorers, route operations and graph parsers; tutorials cover QGIS-based graph authoring and NVIDIA's SWAGGER graph generation [R04-S45]. A warehouse/depot sample graph set ships in `nav2_bringup` [R04-S45]. Lyrical adds corner smoothing for the route server [R04-S41].

**Lifecycle manager and composition [FACT].** The configuration guide lists a Lifecycle Manager and per-server configuration; nav2 uses a lifecycle-node bond mechanism with a configurable heartbeat (e.g. AMCL `bond_heartbeat_period` default 0.1 s; Lyrical changed a bond default and the roadmap targets reduced bond overhead) [R04-S46][R04-S41][R04-S40]. The Gazebo ROS 2 overview recommends composition (`use_composition`) for ros_gz launches [R04-S20]. Details of Nav2's own composition container behaviour were not read: [UNRESOLVED].

**Cross-cutting changes that affect Valtoryn integration [FACT].**

- From Kilted, the default cmd_vel in Nav2 is `TwistStamped` [R04-S42]; ros2_control's diff, mecanum and omni controllers use `TwistStamped` on their reference input in the current documentation [R04-S28][R04-S29][R04-S31].
- Lyrical introduces `nav2_ros_common` and a Nav2 lifecycle node wrapper: custom plugins and task servers must migrate to the `nav2::` namespace types if they use Nav2 utilities, and a global set of QoS profiles is provided [R04-S41].
- The "Kilted to L-turtle" migration page also lists a centralised path-handler in the controller server, goal-checker additions (e.g. adaptive tolerance, axis goal checker), MPPI changes (per-axis delay compensation, plugin-based motion models, open-loop option), the Following Server, partial paths from the planner server, and an option for intra-process communication [R04-S41].
- Nav2's roadmap for the next release (M-Turtle) includes behaviour-tree refinement, an environmental modelling framework prototype and continued abstraction of ROS APIs into `nav2_ros_common` for multi-distro support [R04-S40].

### 2.4 SLAM, mapping and localisation

**Maintenance snapshot (GitHub metadata, 2026-11-07) [FACT]** [R04-S12]:

| Project | Licence | Last push | Archived? | Notes |
|---|---|---|---|---|
| slam_toolbox (`SteveMacenski`) | LGPL-2.1 | 2026-11-02 | No | README: "currently supported ROS2-SLAM library"; maintainer says maintained largely in free time; a Nav2-officially supported SLAM library [R04-S51][R04-S47] |
| cartographer (`cartographer-project`) | Apache-2.0 | 2024-01-05 | No | README says no longer actively maintained, no issue response, occasional critical PRs only [R04-S52] |
| cartographer_ros (`ros2` fork) | Apache-2.0 | 2025-05-24 | No | README (core repo) says ROS fork gets limited maintenance [R04-S52]; still `maintained` status in rosdistro for all four distros [R04-S11] |
| rtabmap_ros | BSD-3-Clause | 2026-11-04 | No | Humble, Jazzy, Kilted, Lyrical, Rolling listed; graph SLAM with RGB-D, stereo, 3D lidar [R04-S53] |
| robot_localization | Apache-2.0 (package.xml) | 2026-11-02 | No | Version 4.0.0 on rolling-devel branch; maintainers Tom Moore and Steve Macenski [R04-S54] |
| fuse (`locusrobotics`) | BSD (package.xml) | 2026-08-19 | No | Version 0.15.0 on devel; maintainer Stephen Williams [R04-S56]; released as 1.3.4 in Lyrical [R04-S11] |

"Last push" is the most recent push to any branch, so it indicates activity, not release quality.

**slam_toolbox [FACT].** 2D SLAM; lifelong mapping (continue from a saved pose graph); serialisation of pose graph plus metadata; optimisation-based "elastic pose-graph" localisation mode with a rolling scan buffer; multi-session refinement and map merging; multi-robot mapping via a separate node; an experimental node-removal mode; CI enforces ABI compatibility within released distributions [R04-S51]. Nav2 documentation recommends it where SLAM is needed and lists `nav2_amcl` for localisation on a static map [R04-S47].

**AMCL [FACT].** Particle-filter localisation on a static map using laser scans; pluggable motion models (`DifferentialMotionModel`, `OmniMotionModel`, or custom); default 500–2000 particles; default laser model `likelihood_field`; update thresholds 0.25 m / 0.2 rad [R04-S46]. Ackermann or other motion models require a custom motion-model plugin (inference from the plugin options listed; not explicitly stated).

**RTAB-Map [FACT].** Graph-based SLAM with appearance-based loop closure; RGB-D, stereo and 3D lidar inputs; outputs occupancy grid, point cloud and OctoMap; odometry nodes (`rgbd_odometry`, `stereo_odometry`, `icp_odometry`); 553 open issues were shown on the repository page [R04-S53].

**robot_localization and fuse [FACT].** robot_localization provides `ekf_node`, `ukf_node` (inputs: `nav_msgs/Odometry`, `sensor_msgs/Imu`, `PoseWithCovarianceStamped`, `TwistWithCovarianceStamped`; outputs `odometry/filtered`, `accel/filtered`, optional `odom`→`base_link` TF) and `navsat_transform_node` for GPS [R04-S48]. Nav2's first-time setup guide documents using it for odometry smoothing; with a single odometry source it has minimal effect other than smoothing [R04-S48]. fuse is a plugin-based nonlinear least-squares (Ceres) sensor-fusion framework for state estimation, localisation, mapping and calibration; its README does not mention ROS 2 support, licence terms or maintenance status [R04-S55], but rosdistro lists it for Jazzy, Kilted and Lyrical (not Humble) with status `maintained` [R04-S11]. The Nav2 Jazzy roadmap lists a "Fuse Migration" item [R04-S40].

**Gaps [UNRESOLVED].** I did not inspect other SLAM or LiDAR-inertial odometry packages that appear in rosdistro (for example `rko_slam`) [R04-S11]; their capability and maintenance were not evaluated. I did not verify 3D SLAM options beyond RTAB-Map.

### 2.5 Simulation: Gazebo and alternatives

**Naming lineage [FACT].** The older releases (Gazebo 9, 11) are called Gazebo Classic; the newer lettered releases (Fortress, Garden, Harmonic, ...) were formerly called "Ignition" and are now simply "Gazebo" [R04-S19]. `ros_ign` packages are shims redirecting to `ros_gz` [R04-S13]. Gazebo Classic packages (`gazebo_ros_pkgs`) exist in the Humble and Jazzy distribution files and are absent from Kilted and Lyrical [R04-S11]. Gazebo Classic's end-of-life date was not stated on the migration page: [UNRESOLVED] (resolve via the Gazebo Classic release page).

**Gazebo releases [FACT]** [R04-S15]:

| Release | Date | EOL | LTS |
|---|---|---|---|
| Rotary | rolling (nightly from `main`) | n/a | experimental |
| "M" (planned) | Mar 2027 | Dec 2028 | not stated |
| Jetty | Sep 2025 | May 2031 | LTS |
| Ionic | Sep 2024 | Dec 2026 | not stated |
| Harmonic | Sep 2023 | May 2029 | LTS |
| Fortress | Sep 2021 | May 2027 | LTS |
| Garden | Sep 2022 | Nov 2024 | EOL |

The Lyrical announcement says Gazebo is moving to March releases, two months before the matching ROS release, with names starting with the same letter [R04-S05]. Jetty's page recommends Ubuntu 26.04 and 24.04; Windows is "experimental" via conda-forge/Pixi with known runtime issues; macOS Sequoia (arm64) is recommended [R04-S17]. The general install page says Ubuntu Noble and Resolute (amd64) are officially supported and arm, Windows and macOS are best-effort [R04-S16]. In gz-sim's own README, on Windows the server and GUI cannot yet run together and must be started in separate terminals [R04-S18].

**ROS/Gazebo pairing (official table) [FACT]** [R04-S14]:

| ROS 2 | Fortress | Harmonic | Ionic | Jetty |
|---|---|---|---|---|
| Lyrical | not possible | possible with effort | possible with effort | recommended |
| Kilted | not possible | possible with effort | recommended | not possible |
| Jazzy | not possible | recommended | not possible | not possible |
| Humble | recommended | possible with effort | not possible | not possible |

(The fetched table was garbled; reconstruction follows the legend of the page and the `ros_gz` README, which gives Humble/Fortress, Jazzy/Harmonic, Kilted/Ionic and Lyrical/Jetty as binaries from `packages.ros.org`, with other pairings only from source or from `packages.osrfoundation.org` [R04-S13].) `gz_ros2_control` maps Lyrical→Jetty, Kilted→Ionic, Jazzy→Harmonic, Humble→Fortress/Harmonic [R04-S22].

**ros_gz bridge [FACT].** `parameter_bridge` bridges topics as `<topic>@<ROS type>@<Gazebo type>` (bidirectional default; `[` one-way from Gazebo); 72 topic mappings across 70 ROS message types plus four services (ControlWorld, DeleteEntity, SpawnEntity, SetEntityPose); YAML or XML launch config; `/clock` should come from Gazebo only [R04-S21]. Gazebo's ROS 2 overview documents three integration paths: launching, bridging, spawning [R04-S20].

**Alternatives (official docs only) [FACT].**

| Simulator | Licence/terms as read | ROS 2 integration | Windows |
|---|---|---|---|
| NVIDIA Isaac Sim | Repository Apache-2.0 [R04-S85], but building/using it requires components under the "NVIDIA Isaac Sim Additional Software and Materials License" (Omniverse Kit SDK, 3D models/textures) [R04-S86]; terms of that licence not read [UNRESOLVED] | ROS 2 bridge extension; Humble and Jazzy "recommended" (tested); other natively installed distros experimental [R04-S84]; Lyrical therefore experimental | Windows 11 supported; requirements include RTX GPU (minimum listed RTX 4080, 16 GB VRAM, 32 GB RAM); container runs only on Linux [R04-S83] |
| Webots | Apache-2.0 [R04-S87] | `webots_ros2` Apache-2.0 [R04-S88]; released in rosdistro for Humble–Lyrical [R04-S11]; supported distro list not stated on the README | Windows, Linux, macOS [R04-S87] |
| MuJoCo | Apache-2.0 [R04-S89] | Not ROS-native; `mujoco_ros2_control` lists Humble, Jazzy, Kilted, Lyrical [R04-S90] (licence not named on that README) | Windows x86-64 binaries [R04-S89] |

### 2.6 Robot description: URDF, Xacro, SDF

- **URDF** describes one robot in isolation. In the Gazebo Classic tutorial, the listed limits are: it cannot place the robot in a world, cannot represent kinematic loops, lacks properties such as friction, cannot describe non-robot elements such as lights or heightmaps, and relies heavily on XML attributes with no built-in backward-compatibility mechanism [R04-S23]. (The source is a Gazebo Classic tutorial; the structural limits of URDF are format-level, but Gazebo-specific tag names may differ in current Gazebo.)
- **Gazebo-specific URDF extension:** a `<gazebo>` element carries simulation properties (link friction/contact parameters, joint parameters, plugins); every link needs a valid `<inertial>` with mass greater than zero; fixing to the world requires a `world` link and fixed joint [R04-S23].
- **SDFormat** is an XML format for environments, objects and robots, including physics, lights, terrain and sensors [R04-S24]; Gazebo worlds are SDF and include models via `<include>` and `model://` paths resolved through `GZ_SIM_RESOURCE_PATH` [R04-S94]. libsdformat converts URDF to SDF; its changelog shows repeated fixes in fixed-joint reduction and in sensor/light poses on lumped links, so converted models need verification [R04-S24].
- **Xacro** is a macro language over URDF; I could not open an official page that defines its semantics in this session (search results only), so no Xacro claims are made beyond its role as a macro/property layer for URDF: [UNRESOLVED] (resolve via the xacro package README/wiki).
- **ros2_control** takes hardware definitions inside the URDF via `<ros2_control>` tags [R04-S36]; Lyrical's URDF 1.2 adds acceleration/jerk limits [R04-S05].

### 2.7 Middleware (DDS / RMW)

**Tiers [FACT].** Lyrical: `rmw_fastrtps_cpp` (default), `rmw_cyclonedds_cpp` and `rmw_zenoh_cpp` Tier 1 on all architectures; `rmw_connextdds` Tier 1 except arm64; `rmw_fastrtps_dynamic_cpp` Tier 2; a middleware's tier cannot exceed its platform's tier [R04-S03]. Jazzy: Fast DDS, Cyclone DDS Tier 1, Connext Tier 1 except arm64, Fast DDS dynamic Tier 2, GurumDDS Tier 3; `rmw_zenoh` is not in the Jazzy table [R04-S06]. Kilted: `rmw_zenoh_cpp` became Tier 1 on all platforms [R04-S07]. Vendor/licence summary (mirror of ROS docs, Jazzy-era): Fast DDS Apache-2.0; Cyclone DDS EPL-2.0; Connext commercial/research licence and installed separately; GurumDDS commercial, community support [R04-S60]. The mirror also states: no performance comparison is given; choice depends on licence, platform availability and footprint; cross-vendor communication is not guaranteed (documented `WString` gaps); use the same RMW across a distributed system [R04-S60]. **No official latency/throughput benchmark was found in the sources read: [UNRESOLVED]** (resolve by reading the ROS 2 `performance_test`/reference-system results or running Valtoryn's own benchmark with representative message sizes).

**Domain ID [FACT].** Default 0; theoretical range 0–232; on Linux 0–101 and 215–232 avoid the default ephemeral port range; on macOS/Windows 0–166; each ROS process is one DDS participant using two ports, so participants-per-machine limits apply near the top of the range (e.g. Linux domain 101: at most 54 processes) [R04-S61] (mirror of Humble-era documentation).

**Discovery and multi-host [FACT].**

- Default DDS discovery uses multicast (Simple Discovery), which scales poorly and may fail on Wi-Fi; the Fast DDS Discovery Server makes nodes clients of a server, selected with `ROS_DISCOVERY_SERVER` (`host:port`, multiple servers separated by `;`, default port 11811), supports redundant servers and a backup mode, and requires the ROS 2 CLI daemon to run as a Super Client [R04-S62][R04-S63]. The Vulcanexus tutorial says traffic is reduced but gives no measurements [R04-S63].
- Cyclone DDS: peers can be listed via `CYCLONEDDS_URI` when multicast is unavailable; the README recommends raising `net.core.rmem_max`/`rmem_default` for large samples (its text is Foxy-era) [R04-S64].
- `rmw_zenoh`: needs a Zenoh router (`rmw_zenohd`) for discovery because multicast discovery is disabled by default; sessions are peer-to-peer after discovery; multi-host bridging is done by pointing a router's `connect` endpoints at another host's router or running a session in client mode; shared memory is configurable; access control, authentication and encryption are supported; it does not interoperate with `zenoh-plugin-ros2dds`/`zenoh-bridge-ros2dds`; the router defaults to listen on IPv6 `[::]`, which fails on IPv4-only systems; Humble nodes and newer nodes silently drop messages to each other (type hashes in key expressions) [R04-S57]. `ROS_DOMAIN_ID` is the first segment of every key expression, so different domains cannot communicate even via interconnected routers [R04-S58].
- `rmw_zenoh` QoS limits: liveliness only `AUTOMATIC`; `DEADLINE` and `LIFESPAN` unimplemented; `TRANSIENT_LOCAL` history from a publisher-side cache [R04-S58]. A known issue: with SHM under high CPU load, service calls or `TRANSIENT_LOCAL` publications may be dropped at launch with many nodes (issue #978 cited in the README) [R04-S57].
- Quality levels: `rmw_zenoh_cpp` claims Quality Level 2, with documented gaps (no performance tests, public API docs not hosted) [R04-S59]; the Cyclone RMW README claims Quality Level 2 (README is dated) [R04-S64]; `rclcpp` claims Quality Level 1 when used with a Quality Level 1 middleware [R04-S65].

**Lyrical zero-copy [FACT].** `rosidl::Buffer` zero-copy currently works only with `rmw_fastrtps_cpp` [R04-S05].

### 2.8 Client libraries: C++, Python, Rust

- **rclcpp**: Quality Level 1 declaration (semantic versioning, API/ABI stability within a distribution, at least 95% line coverage excluding experimental code, all Tier 1 platforms) [R04-S65]. Executors present in Lyrical's `rclcpp` include `SingleThreadedExecutor`, `MultiThreadedExecutor`, `EventsCBGExecutor` (the callback-group events executor) and the experimental `EventsExecutor` [R04-S74][R04-S05].
- **rclpy**: listed in REP-2005 as a common package [R04-S10]; its quality declaration file could not be fetched at the guessed path [UNRESOLVED]. Lyrical adds an asyncio-based `AsyncNode` [R04-S05].
- **rclrs (Rust)**: not listed in REP-2005 as downloaded [R04-S10]; not a released ROS package in any of Humble–Lyrical per rosdistro [R04-S11]; README states "no stability guarantees for the moment", is distributed via crates.io (example `rclrs = "0.8"`), Apache-2.0, with a Windows CI badge [R04-S66]. Supported distributions are not named on the README [R04-S66].
- **Real-time suitability [FACT/EST].** The ROS 2 real-time documentation (mirror) says Xenomai or RT_PREEMPT are the usual real-time solutions, requires avoiding page faults, dynamic allocation and unbounded blocking in the loop, and warns against priority 99 [R04-S70]; its demo requires building ROS 2 from source with Connext and runs on Linux only [R04-S70]. The design article recommends `mlockall`, pre-faulting, avoiding `malloc`/`fork` in loops, and measuring with `cyclictest` [R04-S71]. ros2_control controllers and hardware components are `pluginlib` plugins built on C++ base classes [R04-S25] [EST: therefore real-time control code is naturally C++; Python is not suited to the CM loop].

### 2.9 Real-time options

- **PREEMPT_RT [FACT].** Makes the kernel almost fully preemptible via sleeping spinlocks, priority-inheriting rtmutexes and threaded interrupts (default SCHED_FIFO priority 50 for interrupt threads) [R04-S72]. Whether it is in mainline: the kernel documentation page I read does not say [UNRESOLVED]. Real-time Ubuntu ships a kernel with PREEMPT_RT; the overview page I read does not state licensing/Ubuntu Pro requirements or which Ubuntu releases are covered [R04-S73] [UNRESOLVED].
- **ros2_control RT settings** as in 2.2 [R04-S26].
- **Executors:** see 2.8. Lyrical's callback-group events executor claim (10–15% lower CPU) is the project's own statement [R04-S05].
- **Safety note [FACT].** Nav2's Collision Monitor documents that it does not provide hard-real-time safety certification [R04-S44].

### 2.10 Testing, diagnostics, recording

- **colcon** builds, tests and summarises results across multiple packages in dependency order; isolated and merged workspaces; packaging types CMake and Python; install via Debian, pip or source [R04-S79].
- **launch_testing**: integration testing of launched processes using Python `unittest`; `generate_test_description()` with `ReadyToTest`; active tests and `post_shutdown_test` classes; assertions on stdout and exit codes; CMake registration via `add_launch_test()` [R04-S75].
- **Linters/quality:** REP-2004 requires enforced code style and static analysis from Quality Level 2 upward; `rclcpp` reports passing the standard ROS 2 C++ linters [R04-S09][R04-S65]. Specific `ament_lint` package behaviour: [UNRESOLVED] (the README fetch failed).
- **Quality levels (REP-2004) [FACT].** Level 1: stable ≥1.0.0, API/ABI stability, peer-reviewed change control, documentation for every public API item, system and API tests, coverage tracked and enforced (about 90% line coverage recommended), performance tests, all Tier 1 platforms, disclosure policy. Level 2: similar but no peer-review or per-API documentation requirement and coverage tracked not necessarily enforced. Level 3: tooling and introspection with relaxed requirements. Level 4: demos. Level 5: no requirements, "should not be used" [R04-S09].
- **ros2doctor**: inspects distribution, platform and network interface, checks the running system, `-r`/`-rf` reports, extensible via entry points [R04-S78]; Lyrical adds richer `ros2 doctor --report` [R04-S05].
- **Diagnostics:** `diagnostic_updater` (C++/Python base classes), `diagnostic_aggregator` (plugin-based aggregation), `diagnostic_common_diagnostics`, `diagnostic_remote_logging` (e.g. to InfluxDB); `diagnostic_analysis` not ported to ROS 2; branches for Humble through Rolling, Lyrical included [R04-S76]. ros2_control additionally reports controller/hardware periodicity and execution-time diagnostics for asynchronous components [R04-S26].
- **rosbag2 and MCAP:** MCAP is the default storage plugin (alongside sqlite3); compression, splitting, snapshot mode, QoS overrides, playback services; Lyrical adds remote control, Python APIs and circular limits [R04-S77][R04-S05]. MCAP is a general container with chunking, zstd/lz4 compression, indexes and CRC32; the spec page states no licence terms [R04-S81]. `mcap_vendor` and `rosbag2_storage_mcap` are part of the `rosbag2` repo release in Lyrical [R04-S11].
- **Foxglove:** `foxglove_bridge` is a C++ node exposing live ROS data over the Foxglove WebSocket protocol (ROS 2 `.msg`/`.idl` schemas, parameters, graph introspection) with an optional remote-access mode using a device token; the page states no pricing or licence terms [R04-S80]. Foxglove's pricing and licence for team use: [UNRESOLVED]. RViz2 and PlotJuggler were not evaluated.

### 2.11 Build, CI and containers

- Official `ros` Docker images exist for Humble, Jazzy, Kilted, Lyrical and Rolling with variants `ros-core`, `ros-base` and `perception`; `lyrical` and `latest` map to `lyrical-ros-base` on Ubuntu Resolute; amd64 and arm64v8; desktop-type images with graphical dependencies are under the OSRF Docker Hub profile; maintained by OSRF [R04-S82]. Nav2 documents a Dev Container and Docker installation [R04-S37]. `ros2_control` publishes Docker images under `ghcr.io/ros-controls` [R04-S32].
- Nix packaging for ROS: [UNRESOLVED] (not investigated).

### 2.12 Windows 11 development host

- **Native ROS 2 on Windows.** Lyrical lists Windows 11 with Visual Studio 2022 as Tier 1 (amd64 only; no arm64) [R04-S03]. Jazzy/Kilted/Humble list Windows 10/VS2019 [R04-S06][R04-S07][R04-S08]. The Lyrical Windows install page itself could not be read (blocked); search metadata indicated a Pixi-based install, which is consistent with the Jazzy binary-install page in the mirror: Pixi/conda-forge environment, a short path such as `C:\pixi_ws` because of path-length limits, binaries not relocatable, Release builds, only a subset of the desktop variant packages [R04-S67]. The Humble-era mirror lists Chocolatey-based prerequisites and says "Only Windows 10 is supported" for that release [R04-S68]. The mirror's Humble installation page also says binaries are only created for Tier 1 operating systems [R04-S69].
- **Gazebo on Windows** is experimental for Jetty [R04-S17]; gz-sim on Windows has the server/GUI limitation noted above [R04-S18]. Isaac Sim supports Windows 11 with a high-end NVIDIA GPU [R04-S83]. The ROS 2 real-time demo does not run on Windows [R04-S70]. ros2_control and Nav2 on native Windows: [UNRESOLVED].
- **WSL2.** Microsoft documents that WSL uses NAT networking by default; mirrored networking mode (Windows 11 22H2 or higher) adds multicast support, IPv6, VPN compatibility and direct LAN connection to WSL, but needs a Hyper-V firewall rule or setting for inbound connections [R04-S91]; in NAT mode, reaching WSL from the LAN requires port proxying as for a VM [R04-S91]. USB devices are not natively available in WSL2; they are attached through `usbipd-win`, which takes the device away from Windows while attached and needs a kernel with USB/IP support [R04-S92]. A ROS community discussion (forum, weak evidence) reports Gazebo/RViz working in WSL with a GPU-rendering black-screen report on one WSLg setup, USB/serial difficulty, and a Docker-on-WSL2 workflow used daily by one user; a staff member says Windows is not recommended for newcomers learning ROS [R04-S93]. The Gazebo ROS-installation page recommends running a Tier 1 platform in a VM if the host OS does not match [R04-S14].
- **DDS in WSL2/VM environments:** because default DDS discovery is multicast-based [R04-S62], NAT networking in WSL2 can interfere with discovery between WSL and other hosts [EST: inference from the documented NAT behaviour [R04-S91] and the documented multicast dependence [R04-S62]; not tested].

## 3. Comparison and trade-off analysis

### 3.1 Distribution choice

| Criterion | Humble | Jazzy | Kilted | Lyrical |
|---|---|---|---|---|
| Support remaining (from 2026-11-07) | ~6 months | ~2.5 years | ~1–2 months | ~4.5 years |
| Ubuntu Tier 1 | 22.04 | 24.04 | 24.04 | 26.04 |
| Windows Tier 1 | Win 10 | Win 10 | Win 10 | Win 11 |
| Gazebo official partner | Fortress (EOL May 2027) | Harmonic (LTS, EOL May 2029) | Ionic (EOL Dec 2026) | Jetty (LTS, EOL May 2031) |
| Nav2 status | Maintained | Active | Maintained | Active |
| rmw_zenoh tier | not Tier 1 | not in tier table | Tier 1 | Tier 1 |
| Ecosystem maturity | highest age | mature | n/a | ~5.5 months since release; core packages released [R04-S11] |

Evidence: [R04-S01][R04-S03][R04-S06][R04-S07][R04-S08][R04-S14][R04-S15][R04-S37][R04-S11].

Trade-off: Lyrical is the only distribution whose full support window outlasts a multi-year product effort, is the only one with Gazebo Jetty (LTS to May 2031) as a recommended pairing, and has Windows 11 as Tier 1. Its disadvantage is age: it has existed about 5.5 months [CALC: 2026-05-22 to 2026-11-07], so third-party hardware drivers (LiDAR, motor-controller, camera vendors) may not yet be released for it; the rosdistro snapshot only covers packages that happened to be checked. A second disadvantage is that Lyrical on Ubuntu 24.04 is Tier 3 (source build) [R04-S03]; if the onboard computer's vendor BSP is stuck on 22.04/24.04, Jazzy (Tier 1 on Noble) is the natural fallback.

### 3.2 SLAM/localisation

| Option | Strengths (documented) | Weaknesses (documented) |
|---|---|---|
| slam_toolbox | 2D lidar, lifelong/serialised pose-graph maps, localisation mode, multi-session, Nav2-supported | Single main maintainer working largely in free time [R04-S51]; LGPL-2.1 licence |
| Nav2 AMCL | Static-map particle filter; differential/omni plugins | Needs map and initial pose; 2D scans [R04-S46] |
| RTAB-Map | RGB-D/stereo/3D lidar, loop closure, BSD-3-Clause | Large open-issue count (553) [R04-S53] |
| Cartographer | 2D/3D SLAM, Apache-2.0 | Upstream "no longer actively maintained" [R04-S52] |
| robot_localization EKF/UKF | Standard odometry fusion for Nav2, Apache-2.0 | Local fusion only, no map-based correction |
| fuse | Factor-graph fusion framework | README silent on ROS 2/maintenance; released in rosdistro for Jazzy–Lyrical [R04-S55][R04-S11] |

### 3.3 Middleware

| RMW | Lyrical tier | Strengths (documented) | Constraints (documented) |
|---|---|---|---|
| Fast DDS | Tier 1, default | Default and shipped; Discovery Server; only RMW with `rosidl::Buffer` zero-copy today | Default multicast discovery issues on Wi-Fi |
| Cyclone DDS | Tier 1 | Shipped; Quality Level 2 claim; `CYCLONEDDS_URI` peer config | README guidance is Foxy-era |
| Connext | Tier 1 (not arm64) | Commercial support option | Separate install, commercial/research licence [R04-S60] |
| rmw_zenoh | Tier 1 (Kilted onward) | Router-based discovery, TLS/auth/ACL, WAN-friendly bridging by router connect, SHM option | Requires router; QoS gaps (no deadline/lifespan); not interoperable with Humble nodes; IPv6 router default; SHM issue #978 [R04-S57][R04-S58] |

No performance ranking is made, because no official benchmark was read.

### 3.4 Simulators

Gazebo is the only simulator among those read with an official ROS-distribution pairing table, ROS vendor packages (`packages.ros.org`), an official bridge package and a ros2_control plugin (`gz_ros2_control`) [R04-S14][R04-S21][R04-S22]. Isaac Sim requires a high-end RTX GPU and officially tests Humble and Jazzy only [R04-S83][R04-S84]. Webots and MuJoCo are Apache-2.0 and have ROS 2 packages in rosdistro [R04-S87][R04-S89][R04-S11].

## 4. Implications and recommendations for Valtoryn (all [REC])

### 4.1 Recommended baseline stack

| Layer | Recommended baseline | Version / compatibility constraint | Rationale |
|---|---|---|---|
| ROS 2 distribution | **Lyrical Luth** (LTS) | Supported to May 2031; Tier 1: Ubuntu 26.04 and Windows 11 [R04-S01][R04-S03] | Longest remaining support; new project has no legacy distro; pairs with Gazebo Jetty LTS |
| Fallback distribution | **Jazzy Jalisco** (LTS) | Supported to May 2029; Ubuntu 24.04 Tier 1 [R04-S01][R04-S06] | Use if the onboard-compute BSP cannot run Ubuntu 26.04 or a mandatory driver is unavailable on Lyrical |
| Target OS | Ubuntu 26.04 (robot, CI, dev containers) | amd64 and arm64 Tier 1 [R04-S03] | Matches Lyrical Tier 1 |
| Simulation | **Gazebo Jetty** with `ros_gz` and `gz_ros2_control` from `packages.ros.org` | Jetty LTS to May 2031 [R04-S15]; ros_gz 3.0.x, gz_ros2_control 3.0.x on Lyrical [R04-S11] | Only recommended pairing for Lyrical [R04-S14] |
| Control | ros2_control 6.x + ros2_controllers 6.x | `TwistStamped` reference topics; one `System` hardware component per chassis; `diff_drive_controller` first, then mecanum/omni/steering controllers as new chassis appear [R04-S27] | Gives the hardware-abstraction seam needed for multiple locomotion types |
| Navigation | Nav2 1.5.x | MPPI or Regulated Pure Pursuit with Smac planners; Collision Monitor; Docking Server; Route Server for aisle/lane graphs; keepout and speed-limit filters [R04-S38][R04-S43][R04-S44][R04-S45] | Plugin coverage for diff, omni and Ackermann drivetrains |
| Mapping | slam_toolbox 2.10.x for offline map building | Treat maps as versioned artefacts (serialised pose graph) [R04-S51] | Nav2-supported, actively pushed |
| Localisation | AMCL or slam_toolbox localisation mode on a static map; `robot_localization` EKF for odometry fusion | Evaluate both on recorded data before choosing | Both documented in Nav2 guide [R04-S47][R04-S48] |
| Middleware | `rmw_fastrtps_cpp` for the first milestones, with an early spike on `rmw_zenoh_cpp` for multi-robot/WAN | Never mix RMWs in one system; one RMW per deployment [R04-S60]; do not mix Humble nodes with `rmw_zenoh` [R04-S57] | Default is best-supported; Zenoh is Tier 1 and better matched to router-based multi-host topologies |
| Languages | C++20 for hardware interfaces, controllers, Nav2 plugins and anything in an RT loop; Python for launch, tools, tests and non-RT orchestration; Rust only outside the robot control path | Lyrical requires C++20/Python 3.12–3.14 [R04-S03] | rclcpp is Quality Level 1; rclrs has no stability guarantee and is not a released ROS package [R04-S65][R04-S66][R04-S11] |
| Recording | rosbag2 with MCAP storage | Use snapshot mode for fault capture [R04-S77] | Default storage and indexable container |
| Testing | `colcon test`, gtest/pytest (language-appropriate), `launch_testing` for integration, simulation-in-the-loop tests in Gazebo | Declare a target Quality Level for Valtoryn packages (suggest Level 3 initially, Level 2 for core interfaces) [R04-S09] | See 4.4 |
| Diagnostics | `diagnostic_updater` + `diagnostic_aggregator`, `ros2 doctor` in CI and field checks | [R04-S76][R04-S78] | |
| Containers/CI | Official `ros:lyrical-ros-base` as the CI base image, a dev container for contributors | [R04-S82] | Reproducible across contributors |
| Dev host (Windows 11) | WSL2 Ubuntu 26.04 or a Linux dev container as the primary environment; native Windows only for tools and GUI viewers | See 4.5 | Gazebo on Windows is experimental [R04-S17] |

### 4.2 Version and compatibility constraints to record in the architecture

1. **Pin the triple (ROS distro, Gazebo release, ros_gz branch) as one unit.** The Lyrical/Jetty row is the only recommended one; Lyrical with Harmonic or Ionic is "possible with effort" and only from source [R04-S13][R04-S14].
2. **cmd_vel is `TwistStamped`** end to end (Nav2 from Kilted, ros2_control drive controllers) [R04-S42][R04-S28]. Any teleop or fleet-gateway component should be written for stamped velocities.
3. **Nav2 plugins are distro-branch-specific.** Custom plugins that use Nav2 utilities must use the `nav2::` types introduced in Lyrical [R04-S41]. Keep plugin code on a per-distro branch.
4. **Keep the ROS graph per robot and keep ROS_DOMAIN_ID assignment centrally managed.** Domain IDs 0–101 are safe on Linux; participant-count limits apply to a single machine [R04-S61].
5. **Do not make personnel or machine safety depend on the ROS graph.** Nav2's Collision Monitor is explicitly not a certified safety function [R04-S44]. Safety function allocation belongs to the safety workstream.

### 4.3 Decision gates before committing to Lyrical

- **Gate A (compute):** Confirm the onboard computer vendor image supports Ubuntu 26.04 (or can run a 26.04 container with an RT-capable host kernel [EST: containers share the host kernel, so RT behaviour depends on the host]). If not, adopt Jazzy and treat Lyrical as the migration target. [UNRESOLVED]: the actual compute platform is outside R04.
- **Gate B (drivers):** For each LiDAR, IMU, motor-controller and camera chosen by the hardware workstreams, confirm a released Lyrical package or a vendor-supported source build. rosdistro presence for the chosen drivers should be checked (the check done here covered only core packages).
- **Gate C (spike):** Run a one-week spike in simulation on Lyrical/Jetty with `diff_drive_controller`, Nav2 (MPPI + Smac + Collision Monitor + Docking) and slam_toolbox, and record the issues encountered.

### 4.4 Testing and quality strategy

- Treat three test layers as separate CI jobs: unit tests (gtest/pytest) per package; `launch_testing` integration tests that start controller manager plus mock hardware (ros2_control documents mock components [R04-S95]); and Gazebo-in-the-loop scenario tests.
- Use ros2_control mock components for chassis-agnostic controller tests so new locomotion types gain tests without hardware.
- Record rosbag2/MCAP of every simulation and, later, field run; use snapshot mode on the robot for fault capture [R04-S77].
- Adopt REP-2004 quality levels as a vocabulary for Valtoryn's own packages and write quality declarations for the public interface packages [R04-S09].

### 4.5 Windows 11 host guidance

- Primary: WSL2 with Ubuntu 26.04, or Docker/dev containers, for building, running Nav2 and Gazebo, with mirrored networking mode if DDS multicast between WSL and the LAN is needed [R04-S91]. Verify the Windows build supports mirrored mode (Microsoft states Windows 11 22H2 or higher); the host's Windows version should be confirmed with `winver` [UNRESOLVED] — the host reports build 10.0.26200, and the mapping of that build to a marketing version was not verified in a source. Also confirm that WSL2 is available on the Windows 11 Home edition used by the host [UNRESOLVED] (the Microsoft page read did not state edition requirements).
- Hardware access (serial adapters, CAN, LiDAR over USB) from WSL2 requires `usbipd-win` and takes the device from Windows [R04-S92]; for bring-up work, use a physical Ubuntu machine or the robot's own computer. Real-time tuning cannot be validated on WSL2 [EST: WSL2 runs a Microsoft-provided Linux kernel in a VM; no source read documents RT behaviour].
- Native Windows 11 ROS 2 (Tier 1 on Lyrical [R04-S03]) is reasonable for GUI tools, message inspection and scripting; do not plan on Gazebo or ros2_control on native Windows without verification.

### 4.6 Middleware and fleet recommendations

- Start with Fast DDS, and instrument via `ros2 doctor` plus bag recordings. In parallel, schedule an `rmw_zenoh` evaluation focused on: multi-host bridging through routers, behaviour over Wi-Fi, the documented QoS gaps (deadline/lifespan) and TRANSIENT_LOCAL cache semantics for maps and docks [R04-S58].
- Avoid multicast-dependent discovery on warehouse Wi-Fi: use either a Fast DDS Discovery Server with redundancy [R04-S62] or Zenoh routers [R04-S57].
- Cross-site/WAN fleet traffic should not rely on exposing DDS domains across the WAN; the multi-robot gateway design is for the fleet workstream. R04's contribution is that both Fast DDS (discovery server, TCP transport mentioned in vendor docs but not read) and Zenoh (router bridging) have documented mechanisms.

### 4.7 Risks

| # | Risk | Basis | Mitigation |
|---|---|---|---|
| 1 | Lyrical is new (about 5.5 months); third-party drivers/packages may lag | Release 2026-05-22 [R04-S01] | Gates A and B; keep Jazzy fallback documented |
| 2 | Ubuntu 26.04 may not be available on chosen embedded computers | Lyrical on Noble is Tier 3 [R04-S03] | Platform decision in compute workstream; containerise |
| 3 | Single-maintainer dependencies (slam_toolbox; AMCL via Nav2 is better staffed) | [R04-S51] | Fork-readiness: keep map formats and interfaces behind a localisation interface |
| 4 | Cartographer, Gazebo Classic lock-in | Cartographer unmaintained upstream [R04-S52]; Classic absent from Kilted/Lyrical [R04-S11] | Do not adopt |
| 5 | rmw_zenoh gaps (QoS, IPv6 router default, SHM issue) | [R04-S57][R04-S58] | Spike before committing; keep Fast DDS fallback |
| 6 | Nav2 plugin API churn between distros | Lyrical `nav2_ros_common` migration [R04-S41] | Per-distro branches; thin adapter layer |
| 7 | Documentation access: several primary ROS documentation pages could not be read directly | Method note | Re-verify against docs.ros.org with a normal browser before freezing the baseline |
| 8 | Isaac Sim/other simulator licence terms not fully read | [R04-S86] | Legal review if adopted |
| 9 | Windows dev experience gaps (Gazebo experimental, WSL USB/GPU caveats) | [R04-S17][R04-S92][R04-S93] | Provide Linux dev container and a physical Ubuntu bring-up machine |
| 10 | Quality claims in docs are self-declared | REP-2004 is self-assessed in each package's quality declaration | Own integration tests |

### 4.8 Upgrade strategy

- **Cadence:** ROS 2 releases yearly, alternating LTS/non-LTS [R04-S02]. Non-LTS Makoa (May 2027, EOL December 2028 [R04-S01]) should be treated as a CI canary only (build against Rolling/Makoa in a non-blocking job), not as a deployment target.
- **Next LTS:** by the REP-2000 alternation rule the next LTS is expected in May 2028 [R04-S02] [EST: derived from the stated even-year LTS rule; the name and platform are [UNRESOLVED]]. Plan an evaluation of that LTS in the second half of 2028 and a production migration within the Lyrical window (to May 2031) [CALC from R04-S01].
- **Gazebo:** Jetty LTS aligns with Lyrical (both May 2031) [R04-S15]. The announced Gazebo cadence change (March releases, "M" in March 2027) [R04-S05] means the canary job can track Gazebo M.
- **Dependency hygiene:** pin exact versions from `rosdistro` in a Valtoryn `.repos`/lock file; run a nightly job against the distribution's testing repository; keep Valtoryn-specific interfaces in their own message/service packages so that upgrades touch adapters only.
- **If forced to Jazzy:** Valtoryn code that avoids Lyrical-only features (URDF 1.2 jerk limits, `rosidl::Buffer`, `AsyncNode`, `nav2_ros_common` types) keeps the Jazzy fallback cheap; this is a [REC] to avoid adopting those features in core code before Gate A and B are passed.

## 5. Limitations of this research

- ROS documentation hosts (`docs.ros.org`, `www.ros.org`) were not directly readable; I did not attempt to bypass their bot-protection challenge. Substitutes (documentation source files, mirrors) may be older than the live pages. Items taken from the Vulcanexus mirror are dated to Humble/Jazzy-era text.
- Pages were mostly processed through a summarising fetch tool; summaries can drop caveats. The REP files and rosdistro files were checked directly.
- `rosdistro` shows released versions, not apt sync status or runtime quality.
- GitHub "last push" dates indicate activity only.
- No code was run, no performance was measured, no hardware was involved.
- Not covered: micro-ROS, MoveIt (not required for the initial AMR), fleet-management frameworks (e.g. Open-RMF), ROS 2 security (SROS2) beyond the Zenoh security mention, behaviour-tree libraries beyond Nav2's, perception stacks, lidar drivers, Nix-based ROS packaging, Jetson/Isaac ROS.

## 6. Unresolved questions

1. Exact Kilted EOL (November vs December 2026) — resolve on docs.ros.org Releases page in a normal browser.
2. Lyrical native Windows installation requirements — read the Lyrical "Windows (binary)" page.
3. Availability of ros2_control and Nav2 on native Windows 11 — Lyrical CI/package matrix.
4. Xacro official semantics and limits — xacro package README.
5. Official middleware performance data — ROS 2 performance test results or an in-house benchmark.
6. Ubuntu real-time kernel licensing and release coverage for 26.04; PREEMPT_RT mainline status.
7. Foxglove pricing/licence; Isaac Sim Additional Software and Materials License terms.
8. Plugin availability per distro for Humble/Jazzy (Nav2) — relevant only if Jazzy fallback is used.
9. Driver availability on Lyrical for the sensors/motor controllers Valtoryn selects.
10. Whether WSL2 and mirrored networking mode apply to the host's Windows edition/build.
11. Name and platform of the May 2028 LTS.

## 7. Sources

| ID | Title | Organization / author | URL | Published / revision date | Accessed | What it supports |
|---|---|---|---|---|---|---|
| R04-S01 | ROS 2 Distributions (Releases.rst, rolling branch) | Open Robotics / ros2_documentation | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Releases.rst | n/a (not stated on page) | 2026-11-07 | Distro release/EOL dates, future Makoa, Rolling |
| R04-S02 | REP 2000: ROS 2 Releases and Target Platforms (master snapshot) | Open Robotics (REP authors) | https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-2000.rst | n/a (not stated on page; no Lyrical section) | 2026-11-07 | Release cadence, LTS rules, tier definitions, Kilted window text |
| R04-S03 | Lyrical Luth Supported Platforms (supported-platforms.rst) | Open Robotics / ros2_documentation | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Releases/lyrical/supported-platforms.rst | n/a (not stated on page) | 2026-11-07 | Lyrical tiers, RMW tiers, default RMW, Python/C++ baselines |
| R04-S04 | Lyrical Luth release page (Release-Lyrical-Luth.rst) | Open Robotics / ros2_documentation | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Releases/Release-Lyrical-Luth.rst | n/a (not stated on page) | 2026-11-07 | LTS status, support to May 2031, feature areas |
| R04-S05 | ROS 2 Lyrical Luth Released! | Open Robotics Discourse (announcement) | https://discourse.openrobotics.org/t/ros-2-lyrical-luth-released/55021 | 2026-05-22 (per search listing) | 2026-11-07 | Tier summary, Gazebo Jetty availability, Gazebo cadence change, executor/Buffer/URDF 1.2 highlights |
| R04-S06 | Jazzy Jalisco release page | Open Robotics / ros2_documentation | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Releases/Release-Jazzy-Jalisco.rst | n/a (not stated on page) | 2026-11-07 | Jazzy platforms, RMW tiers, Harmonic pairing |
| R04-S07 | Kilted Kaiju release page | Open Robotics / ros2_documentation | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Releases/Release-Kilted-Kaiju.rst | n/a (not stated on page) | 2026-11-07 | Kilted platforms, Ionic pairing, rmw_zenoh Tier 1 |
| R04-S08 | Humble Hawksbill release page | Open Robotics / ros2_documentation | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Releases/Release-Humble-Hawksbill.rst | n/a (not stated on page) | 2026-11-07 | Humble platforms, Gazebo Classic/Fortress |
| R04-S09 | REP 2004: Package Quality Categories | Open Robotics (REP authors) | https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-2004.rst | n/a (not stated on page) | 2026-11-07 | Quality Level 1–5 definitions |
| R04-S10 | REP 2005: ROS 2 Common Packages (master snapshot) | Gerkey, Thomas / Open Robotics | https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-2005.rst | n/a (not stated on page; snapshot predates ros_gz) | 2026-11-07 | Common-package list; rclrs and ros2_control not listed |
| R04-S11 | rosdistro distribution files (humble, jazzy, kilted, lyrical) | ROS buildfarm / ros/rosdistro | https://raw.githubusercontent.com/ros/rosdistro/master/lyrical/distribution.yaml (and /humble, /jazzy, /kilted) | n/a (live file, read 2026-11-07) | 2026-11-07 | Released package versions, release platforms, presence/absence of packages |
| R04-S12 | GitHub REST API repository metadata | GitHub | https://api.github.com/repos/SteveMacenski/slam_toolbox (also cartographer-project/cartographer, ros2/cartographer_ros, introlab/rtabmap_ros, cra-ros-pkg/robot_localization, locusrobotics/fuse, ros-navigation/navigation2, ros-controls/ros2_control, gazebosim/ros_gz, ros2/rmw_zenoh) | live metadata, read 2026-11-07 | 2026-11-07 | Last-push dates, archived flag, SPDX licence |
| R04-S13 | gazebosim/ros_gz README | Gazebo / Open Robotics | https://raw.githubusercontent.com/gazebosim/ros_gz/ros2/README.md | n/a (not stated on page) | 2026-11-07 | ROS/Gazebo compatibility rows, branches, binaries location |
| R04-S14 | Installing Gazebo with ROS | Gazebo project | https://gazebosim.org/docs/latest/ros_installation/ | n/a (not stated on page) | 2026-11-07 | Official ROS 2 / Gazebo recommended pairing table |
| R04-S15 | Gazebo releases | Gazebo project | https://gazebosim.org/docs/latest/releases/ | n/a (not stated on page) | 2026-11-07 | Gazebo release dates, EOL, LTS |
| R04-S16 | Gazebo installation | Gazebo project | https://gazebosim.org/docs/latest/install/ | n/a (not stated on page) | 2026-11-07 | Officially supported vs best-effort platforms |
| R04-S17 | Gazebo Jetty getting started | Gazebo project | https://gazebosim.org/docs/jetty/getstarted/ | n/a (not stated on page) | 2026-11-07 | Jetty LTS, platform support incl. Windows experimental |
| R04-S18 | gz-sim README | Gazebo / Open Robotics | https://raw.githubusercontent.com/gazebosim/gz-sim/main/README.md | n/a (not stated on page) | 2026-11-07 | Gazebo Sim features, Apache-2.0, Windows server/GUI limitation |
| R04-S19 | Gazebo Classic migration | Gazebo project | https://gazebosim.org/docs/latest/gazebo_classic_migration/ | n/a (not stated on page) | 2026-11-07 | Ignition to Gazebo naming lineage |
| R04-S20 | ROS 2 integration overview | Gazebo project | https://gazebosim.org/docs/latest/ros2_overview/ | n/a (not stated on page) | 2026-11-07 | Integration types, composition recommendation |
| R04-S21 | ros_gz_bridge README | Gazebo / Open Robotics | https://raw.githubusercontent.com/gazebosim/ros_gz/ros2/ros_gz_bridge/README.md | n/a (not stated on page) | 2026-11-07 | Bridge syntax, message-type counts, clock handling |
| R04-S22 | gz_ros2_control README | ros-controls | https://raw.githubusercontent.com/ros-controls/gz_ros2_control/rolling/README.md | n/a (not stated on page) | 2026-11-07 | ROS/Gazebo mapping for ros2_control plugin |
| R04-S23 | Tutorial: Using a URDF in Gazebo (Gazebo Classic) | Open Robotics (Gazebo Classic docs) | https://classic.gazebosim.org/tutorials/?tut=ros_urdf | n/a (not stated on page) | 2026-11-07 | URDF limitations vs SDF, `<gazebo>` extension tags (Classic-era) |
| R04-S24 | sdformat (libsdformat) library page | Gazebo project | https://gazebosim.org/libs/sdformat/ | changelog latest entry 16.1.0 dated 2026-07-10 | 2026-11-07 | SDFormat description, URDF to SDF conversion history |
| R04-S25 | ros2_control Getting Started | ros-controls | https://control.ros.org/rolling/doc/getting_started/getting_started.html | n/a (not stated on page) | 2026-11-07 | Architecture, hardware types, supported distros |
| R04-S26 | Controller Manager user documentation | ros-controls | https://control.ros.org/rolling/doc/ros2_control/controller_manager/doc/userdoc.html | n/a (not stated on page) | 2026-11-07 | Real-time settings, parameters, diagnostics |
| R04-S27 | ros2_controllers index (Rolling) | ros-controls | https://control.ros.org/rolling/doc/ros2_controllers/doc/controllers_index.html | n/a (not stated on page) | 2026-11-07 | List of available controllers/broadcasters |
| R04-S28 | diff_drive_controller (Rolling) | ros-controls | https://control.ros.org/rolling/doc/ros2_controllers/diff_drive_controller/doc/userdoc.html | n/a (not stated on page) | 2026-11-07 | Differential drive interfaces and parameters |
| R04-S29 | mecanum_drive_controller (Rolling) | ros-controls | https://control.ros.org/rolling/doc/ros2_controllers/mecanum_drive_controller/doc/userdoc.html | n/a (not stated on page) | 2026-11-07 | Mecanum controller interfaces |
| R04-S30 | steering_controllers_library (Rolling) | ros-controls | https://control.ros.org/rolling/doc/ros2_controllers/steering_controllers_library/doc/userdoc.html | n/a (not stated on page) | 2026-11-07 | Bicycle/tricycle/Ackermann kinematics |
| R04-S31 | omni_wheel_drive_controller (Rolling) | ros-controls | https://control.ros.org/rolling/doc/ros2_controllers/omni_wheel_drive_controller/doc/userdoc.html | n/a (not stated on page) | 2026-11-07 | Omni wheel controller |
| R04-S32 | ros2_control README | ros-controls | https://raw.githubusercontent.com/ros-controls/ros2_control/master/README.md | n/a (not stated on page) | 2026-11-07 | Branch/distro table, Docker images |
| R04-S33 | diff_drive_controller (Humble) | ros-controls | https://control.ros.org/humble/doc/ros2_controllers/diff_drive_controller/doc/userdoc.html | n/a (not stated on page) | 2026-11-07 | `use_stamped_vel` behaviour in Humble |
| R04-S34 | ros2_controllers index (Jazzy) | ros-controls | https://control.ros.org/jazzy/doc/ros2_controllers/doc/controllers_index.html | n/a (not stated on page) | 2026-11-07 | Jazzy controller list |
| R04-S35 | ros2_controllers index (Humble) | ros-controls | https://control.ros.org/humble/doc/ros2_controllers/doc/controllers_index.html | n/a (not stated on page) | 2026-11-07 | Humble controller list |
| R04-S36 | Hardware interface types user documentation | ros-controls | https://raw.githubusercontent.com/ros-controls/ros2_control/master/hardware_interface/doc/hardware_interface_types_userdoc.rst | n/a (not stated on page) | 2026-11-07 | `<ros2_control>` URDF tag, interface data types, GPIO, groups |
| R04-S37 | Nav2 documentation home | Nav2 / Open Navigation | https://docs.nav2.org/index.html (redirects to /rolling/) | n/a (not stated on page) | 2026-11-07 | Distro support statuses, overview, architecture |
| R04-S38 | Navigation Plugins | Nav2 / Open Navigation | https://docs.nav2.org/rolling/configuration_and_development/navigation_plugins/ | n/a (not stated on page) | 2026-11-07 | Plugin lists, drivetrain support |
| R04-S39 | navigation2 README | Nav2 / Open Navigation | https://raw.githubusercontent.com/ros-navigation/navigation2/main/README.md | n/a (not stated on page) | 2026-11-07 | Distro builds, sponsors, maintainer organisation |
| R04-S40 | Nav2 Roadmaps | Nav2 / Open Navigation | https://docs.nav2.org/rolling/community/roadmaps/ | n/a (not stated on page) | 2026-11-07 | Per-release commitments (docking, route server, Lyrical, M-Turtle) |
| R04-S41 | Kilted to L-turtle (Lyrical) migration guide | Nav2 / Open Navigation | https://docs.nav2.org/rolling/configuration_and_development/migration_guides/Lyrical/ | n/a (not stated on page) | 2026-11-07 | Lyrical-era Nav2 changes |
| R04-S42 | Jazzy to Kilted migration guide | Nav2 / Open Navigation | https://docs.nav2.org/rolling/configuration_and_development/migration_guides/jazzy/Jazzy/ | n/a (not stated on page) | 2026-11-07 | Route Server, TwistStamped default, docking changes |
| R04-S43 | Docking Server | Nav2 / Open Navigation | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/configuring_docking_server/ | n/a (not stated on page) | 2026-11-07 | Docking server behaviour and parameters |
| R04-S44 | Collision Monitor Node | Nav2 / Open Navigation | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/collision_monitor/configuring_collision_monitor_node/ | n/a (not stated on page) | 2026-11-07 | Collision monitor models, sources, safety caveat |
| R04-S45 | Route Server | Nav2 / Open Navigation | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/route_server/configuring_route_server/ | n/a (not stated on page) | 2026-11-07 | Route Server behaviour and plugins |
| R04-S46 | AMCL (Jazzy docs) | Nav2 / Open Navigation | https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/others/configuring_amcl/ | n/a (not stated on page) | 2026-11-07 | AMCL parameters and motion models |
| R04-S47 | Mapping and Localization (first-time setup, Jazzy docs) | Nav2 / Open Navigation | https://docs.nav2.org/jazzy/configuration_and_development/first_time_robot_setup_guide/sensors/mapping_localization/ | n/a (not stated on page) | 2026-11-07 | slam_toolbox and AMCL as Nav2-supported options |
| R04-S48 | Smoothing Odometry using Robot Localization (Jazzy docs) | Nav2 / Open Navigation | https://docs.nav2.org/jazzy/configuration_and_development/first_time_robot_setup_guide/odom/setup_robot_localization/ | n/a (not stated on page) | 2026-11-07 | robot_localization EKF/UKF usage |
| R04-S49 | navigation2 LICENSE | Nav2 / Open Navigation | https://raw.githubusercontent.com/ros-navigation/navigation2/main/LICENSE | n/a (not stated on page) | 2026-11-07 | Per-package licensing statement |
| R04-S50 | nav2_bringup package.xml | Nav2 / Open Navigation | https://raw.githubusercontent.com/ros-navigation/navigation2/main/nav2_bringup/package.xml | n/a (not stated on page) | 2026-11-07 | nav2_bringup licence (Apache-2.0), version 1.5.0 |
| R04-S51 | slam_toolbox repository | Steve Macenski | https://github.com/SteveMacenski/slam_toolbox | n/a (not stated on page) | 2026-11-07 | Features, licence, maintenance statements |
| R04-S52 | Cartographer repository | Cartographer project | https://github.com/cartographer-project/cartographer | n/a (not stated on page) | 2026-11-07 | "No longer actively maintained" notice |
| R04-S53 | rtabmap_ros repository | IntRoLab | https://github.com/introlab/rtabmap_ros | n/a (not stated on page) | 2026-11-07 | RTAB-Map ROS 2 distro support, features |
| R04-S54 | robot_localization package.xml | cra-ros-pkg | https://raw.githubusercontent.com/cra-ros-pkg/robot_localization/rolling-devel/package.xml | n/a (not stated on page) | 2026-11-07 | Version 4.0.0, maintainers, Apache-2.0 |
| R04-S55 | fuse README | Locus Robotics | https://raw.githubusercontent.com/locusrobotics/fuse/devel/README.md | n/a (not stated on page) | 2026-11-07 | fuse feature description |
| R04-S56 | fuse package.xml | Locus Robotics | https://raw.githubusercontent.com/locusrobotics/fuse/devel/fuse/package.xml | n/a (not stated on page) | 2026-11-07 | fuse version 0.15.0, licence BSD |
| R04-S57 | rmw_zenoh README | ros2 / Open Robotics | https://raw.githubusercontent.com/ros2/rmw_zenoh/rolling/README.md | n/a (not stated on page) | 2026-11-07 | Router, config, WAN/multi-host, limitations, known issues |
| R04-S58 | rmw_zenoh design document | ros2 / Open Robotics | https://raw.githubusercontent.com/ros2/rmw_zenoh/rolling/docs/design.md | n/a (not stated on page) | 2026-11-07 | Discovery, key expressions, QoS support/limits, domain ID |
| R04-S59 | rmw_zenoh_cpp Quality Declaration | ros2 / Open Robotics | https://raw.githubusercontent.com/ros2/rmw_zenoh/rolling/rmw_zenoh_cpp/QUALITY_DECLARATION.md | n/a (not stated on page) | 2026-11-07 | Quality Level 2 claim and gaps |
| R04-S60 | About different ROS 2 DDS/RTPS vendors (Vulcanexus mirror of ROS docs, Jazzy) | eProsima (mirror of ROS documentation) | https://docs.vulcanexus.org/en/jazzy/ros2_documentation/source/Concepts/Intermediate/About-Different-Middleware-Vendors.html | n/a (not stated on page) | 2026-11-07 | Vendor/licence table, cross-vendor caveats (weaker: mirror) |
| R04-S61 | The ROS_DOMAIN_ID (Vulcanexus mirror of ROS docs, Humble) | eProsima (mirror of ROS documentation) | https://docs.vulcanexus.org/en/humble/ros2_documentation/source/Concepts/Intermediate/About-Domain-ID.html | n/a (not stated on page) | 2026-11-07 | Domain ID range, port/process limits (weaker: mirror) |
| R04-S62 | Use ROS 2 with Fast-DDS Discovery Server | eProsima | https://fast-dds.docs.eprosima.com/en/latest/fastdds/ros2/discovery_server/ros2_discovery_server.html | n/a (not stated on page) | 2026-11-07 | Discovery Server, Super Client, redundancy, backup |
| R04-S63 | How to use a Discovery Server to optimize ROS 2 node discovery (Vulcanexus Jazzy) | eProsima | https://docs.vulcanexus.org/en/jazzy/rst/tutorials/core/scalability/discovery_server/discovery_server_scalability.html | n/a (not stated on page) | 2026-11-07 | Discovery server rationale; no quantitative data |
| R04-S64 | rmw_cyclonedds README | ros2 / Open Robotics | https://raw.githubusercontent.com/ros2/rmw_cyclonedds/rolling/README.md | n/a (not stated on page; content appears dated) | 2026-11-07 | Cyclone RMW config, Quality Level 2 claim |
| R04-S65 | rclcpp Quality Declaration | ros2 / Open Robotics | https://raw.githubusercontent.com/ros2/rclcpp/rolling/rclcpp/QUALITY_DECLARATION.md | n/a (not stated on page) | 2026-11-07 | rclcpp Quality Level 1 claim |
| R04-S66 | ros2_rust README (rclrs) | ros2-rust community | https://raw.githubusercontent.com/ros2-rust/ros2_rust/main/README.md | n/a (not stated on page) | 2026-11-07 | rclrs status, stability statement, licence |
| R04-S67 | Windows (binary) install, Jazzy (Vulcanexus mirror) | eProsima (mirror of ROS documentation) | https://docs.vulcanexus.org/en/jazzy/ros2_documentation/source/Installation/Windows-Install-Binary.html | n/a (not stated on page) | 2026-11-07 | Pixi-based Windows install, path and relocation caveats (mirror) |
| R04-S68 | Windows (binary) install, Humble (Vulcanexus mirror) | eProsima (mirror of ROS documentation) | https://docs.vulcanexus.org/en/humble/ros2_documentation/source/Installation/Windows-Install-Binary.html | n/a (not stated on page) | 2026-11-07 | Humble Windows prerequisites, Windows 10 only (mirror) |
| R04-S69 | Installation (Humble, Vulcanexus mirror) | eProsima (mirror of ROS documentation) | https://docs.vulcanexus.org/en/humble/ros2_documentation/source/Installation.html | n/a (not stated on page) | 2026-11-07 | Binaries only for Tier 1 OS; Docker pointer (mirror) |
| R04-S70 | Real-time programming in ROS 2 (Vulcanexus mirror, Jazzy) | eProsima (mirror of ROS documentation) | https://docs.vulcanexus.org/en/jazzy/ros2_documentation/source/Tutorials/Demos/Real-Time-Programming.html | n/a (not stated on page) | 2026-11-07 | RT guidance, memlock/rtprio, demo limits (mirror) |
| R04-S71 | Introduction to Real-time Systems | ROS 2 Design (Open Robotics) | https://design.ros2.org/articles/realtime_background.html | n/a (not stated on page) | 2026-11-07 | RT background, allocation/priority-inversion guidance |
| R04-S72 | Theory of operation (PREEMPT_RT) | Linux kernel documentation | https://docs.kernel.org/core-api/real-time/theory.html | n/a (not stated on page) | 2026-11-07 | PREEMPT_RT mechanisms |
| R04-S73 | Real-time Ubuntu documentation | Canonical | https://ubuntu.com/real-time/docs/latest/ | n/a (not stated on page) | 2026-11-07 | Existence of Real-time Ubuntu (PREEMPT_RT kernel) |
| R04-S74 | rclcpp executors.hpp | ros2 / Open Robotics | https://raw.githubusercontent.com/ros2/rclcpp/rolling/rclcpp/include/rclcpp/executors.hpp | n/a (not stated on page) | 2026-11-07 | Executor classes in rclcpp |
| R04-S75 | launch_testing README | ros2 / Open Robotics | https://raw.githubusercontent.com/ros2/launch/rolling/launch_testing/README.md | n/a (not stated on page) | 2026-11-07 | Integration-test framework |
| R04-S76 | ros/diagnostics README | ROS community | https://raw.githubusercontent.com/ros/diagnostics/ros2/README.md | n/a (not stated on page) | 2026-11-07 | Diagnostic packages, distro branches |
| R04-S77 | rosbag2 README | ros2 / Open Robotics | https://raw.githubusercontent.com/ros2/rosbag2/rolling/README.md | n/a (not stated on page) | 2026-11-07 | Storage plugins, MCAP default, snapshot mode |
| R04-S78 | ros2doctor README | ros2 / Open Robotics | https://raw.githubusercontent.com/ros2/ros2cli/rolling/ros2doctor/README.md | n/a (not stated on page) | 2026-11-07 | ros2doctor checks and reports |
| R04-S79 | colcon documentation | colcon project | https://colcon.readthedocs.io/en/released/index.html | n/a (not stated on page) | 2026-11-07 | colcon build/test verbs, workspace layouts |
| R04-S80 | Foxglove Bridge (ROS) | Foxglove | https://docs.foxglove.dev/docs/connecting-to-data/ros-foxglove-bridge | n/a (not stated on page) | 2026-11-07 | foxglove_bridge capabilities, remote access |
| R04-S81 | MCAP specification | Foxglove / MCAP project | https://mcap.dev/spec | n/a (not stated on page) | 2026-11-07 | MCAP container features |
| R04-S82 | ros (Docker Official Image) | Docker Hub / OSRF | https://hub.docker.com/_/ros | n/a (page snapshot) | 2026-11-07 | ROS Docker tags, variants, architectures |
| R04-S83 | Isaac Sim requirements | NVIDIA | https://docs.isaacsim.omniverse.nvidia.com/latest/installation/requirements.html | n/a (not stated on page) | 2026-11-07 | Isaac Sim OS/GPU requirements |
| R04-S84 | Isaac Sim ROS 2 tutorials index | NVIDIA | https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/index.html | n/a (not stated on page) | 2026-11-07 | ROS 2 bridge, tested distros |
| R04-S85 | IsaacSim repository README | NVIDIA | https://raw.githubusercontent.com/isaac-sim/IsaacSim/main/README.md | n/a (not stated on page) | 2026-11-07 | Isaac Sim licence badge, build requirements |
| R04-S86 | IsaacSim LICENSE | NVIDIA | https://raw.githubusercontent.com/isaac-sim/IsaacSim/main/LICENSE | n/a (not stated on page) | 2026-11-07 | Apache-2.0 plus additional NVIDIA licence for Kit SDK/assets |
| R04-S87 | Webots README | Cyberbotics | https://raw.githubusercontent.com/cyberbotics/webots/master/README.md | n/a (not stated on page) | 2026-11-07 | Webots licence and platforms |
| R04-S88 | webots_ros2 README | Cyberbotics | https://raw.githubusercontent.com/cyberbotics/webots_ros2/master/README.md | n/a (not stated on page) | 2026-11-07 | webots_ros2 description, licence |
| R04-S89 | MuJoCo README | Google DeepMind | https://raw.githubusercontent.com/google-deepmind/mujoco/main/README.md | n/a (not stated on page) | 2026-11-07 | MuJoCo licence, platforms |
| R04-S90 | mujoco_ros2_control README | ros-controls | https://raw.githubusercontent.com/ros-controls/mujoco_ros2_control/main/README.md | n/a (not stated on page) | 2026-11-07 | MuJoCo/ros2_control integration and distro list |
| R04-S91 | Accessing network applications with WSL | Microsoft Learn | https://learn.microsoft.com/en-us/windows/wsl/networking | ms.date 2024-07-16; updated 2026-06-02 | 2026-11-07 | WSL2 NAT vs mirrored networking, multicast, firewall |
| R04-S92 | Connect USB devices to WSL | Microsoft Learn | https://learn.microsoft.com/en-us/windows/wsl/connect-usb | ms.date 2024-04-16; updated 2026-06-02 | 2026-11-07 | usbipd-win USB attachment to WSL2 |
| R04-S93 | Is WSL Sufficient for Learning and Using ROS? | ROS Discourse (community thread; weak evidence) | https://discourse.openrobotics.org/t/is-wsl-sufficient-for-learning-and-using-ros/42700 | 2025-03-21 (per search listing) | 2026-11-07 | Community experience with WSL, GUI/USB caveats |
| R04-S94 | Gazebo SDF worlds | Gazebo project | https://gazebosim.org/docs/latest/sdf_worlds/ | n/a (not stated on page) | 2026-11-07 | SDF world structure, `<include>`/`model://`, GZ_SIM_RESOURCE_PATH |
| R04-S95 | ros2_control documentation index (Rolling) | ros-controls | https://control.ros.org/rolling/doc/ros2_control/doc/index.html | n/a (not stated on page) | 2026-11-07 | Mock/async hardware components, update-rate topics listed |

**Sources that could not be inspected (not cited):**

- https://www.ros.org/reps/rep-2000.html and https://docs.ros.org/... pages (Releases, supported-platforms, Windows install for Lyrical, ROS_DOMAIN_ID, URDF/Xacro tutorials, Discovery Server tutorial): bot-protection challenge; not bypassed.
- https://raw.githubusercontent.com/ros2/rclpy/rolling/rclpy/QUALITY_DECLARATION.md and controller_manager/QUALITY_DECLARATION.md: HTTP 404 at the guessed paths.
- https://raw.githubusercontent.com/ament/ament_lint/rolling/README.md: HTTP 404.
- https://raw.githubusercontent.com/cra-ros-pkg/robot_localization/rolling-devel/README.md: contained only a stub (full documentation lives elsewhere).
- Nvidia "Isaac Sim Additional Software and Materials License" and Cyberbotics ROS documentation page: not opened or contentless.
