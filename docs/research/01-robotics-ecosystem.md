# R01 — Robotics Ecosystem and Competitive Landscape
> **Status:** Research document — proposed findings, nothing here is implemented.
> **Workstream:** R01 · **Last verified:** 2026-11-07 · **Evidence legend:** see below

## Evidence legend

- **[FACT]** established by a cited source, always followed by a source ID such as [R01-S07]
- **[CALC]** derived by a shown calculation from cited or labelled inputs
- **[EST]** engineering estimate or assumption (basis stated)
- **[REC]** Valtoryn recommendation or proposal (engineering judgement, not established fact)
- **[UNRESOLVED]** could not be established; the text says what would resolve it

All statements about Valtoryn are proposals. Nothing in the Valtoryn platform is implemented and no hardware exists or has been tested.

---

## 1. Scope and method

**Question.** What open and commercial robotics software already exists that a modular, open-source, warehouse-oriented robotics platform (Valtoryn) could reuse, interoperate with, or must compete against; where are the real gaps?

**Method.** Primary documents were opened and read in this session on 2026-11-07: ROS 2 release documentation sources, REP-2000, the ROS 2 and Nav2 papers (arXiv manuscripts), Nav2 documentation, the Open-RMF book source, the VDA 5050 v3.0.0 specification text, Gazebo release and `ros_gz` documents, and vendor pages. Repository activity (last push, latest tag or release, licence, stars, open issues) was read from the GitHub REST API on 2026-11-07 (source R01-S29). Where the official HTML documentation sites sat behind a proof-of-work bot challenge (docs.ros.org, ros.org/reps, ojs.aaai.org), the challenge was not bypassed; the underlying GitHub source files were read instead, or the document is listed under "Sources that could not be inspected".

**Evidence tiers used.** Official documentation and specification text, then original papers, then official repositories, then vendor marketing pages (labelled "vendor claim"), then trade press (labelled weak).

**Not covered here.** Safety standards (ISO 3691-4 etc.), simulation fidelity, localisation algorithm benchmarking and battery/charging design belong to other workstreams. They are mentioned only where they change the reuse-versus-build decision.

---

## 2. Findings: the ROS 2 foundation

### 2.1 What ROS 2 is and how it is structured

- **[FACT]** ROS 2 is an Apache-2.0 licensed robotics SDK made of middleware ("plumbing"), algorithms, and developer tools, organised as a federated ecosystem of packages rather than one codebase. [R01-S06]
- **[FACT]** The runtime is layered: language client libraries sit on a common C library `rcl`, which sits on the ROS middleware abstraction `rmw`. Each middleware vendor implements `rmw`, so the transport can be swapped without application code changes. Interfaces are defined in IDL (`.msg` or OMG `.idl`) and code-generated per language. [R01-S06]
- **[FACT]** Communication patterns are topics (asynchronous pub/sub), services (request/response, non-blocking for the client) and actions (goal, feedback, result, cancel) for long-running tasks such as navigation. [R01-S06]
- **[FACT]** Lifecycle (managed) nodes expose a state machine (Unconfigured, Inactive, Active, Finalized) so an integrator controls when each node becomes active. Nodes written as components can be placed in any process by configuration, including intra-process communication. [R01-S06]
- **[FACT]** Security uses DDS-Security (authentication, access control, AES-GCM encryption), with the SROS2 tooling to generate keys and policies. [R01-S06]
- **[FACT]** The paper states the design trade-off openly: asynchrony and distribution can make deterministic execution harder, and a special-purpose monolith can be more efficient for one well-defined problem. [R01-S06]

**Measured limits quoted by the ROS 2 authors.** The paper's own benchmark (one publisher, one subscriber, 1,000 messages/s, CycloneDDS, 6-core i7-6800K, Fedora 34, Rolling as of 2021-09-23) reports intra-process 95th-percentile latency below 1 ms for messages under 8 MB, but the multi-process path rises to 7.85 ms at 8 MB and the sustained rate falls from 1000 Hz (up to 2 MB) to 213 Hz at 8 MB. [FACT] [R01-S06] The same paper says default DDS configuration is "not particularly effective" above 1 MB and recommends composition and intra-process transport for large messages. [FACT] [R01-S06] These numbers are from a single desktop configuration in 2021 and are not a prediction for a warehouse Wi-Fi network. [EST]

### 2.2 Distributions and support status (as of 2026-11-07)

| Distribution | Release date | End of support | Notes | Source |
|---|---|---|---|---|
| Humble Hawksbill | 2022-05-23 | May 2027 | LTS | [R01-S02] [R01-S01] |
| Jazzy Jalisco | 2024-05-23 | May 2029 | LTS; Tier 1 Ubuntu 24.04 (amd64, arm64), Windows 10 | [R01-S02] [R01-S01] |
| Kilted Kaiju | 2025-05-23 | Dec 2026 (releases table) or Nov 2026 (REP-2000) | Non-LTS; `rmw_zenoh_cpp` became Tier 1 | [R01-S02] [R01-S01] [R01-S05] |
| Lyrical Luth | 2026-05-22 | May 2031 | LTS, "twelfth release"; Tier 1 Ubuntu 26.04 "Resolute" (amd64, arm64) and Windows 11 | [R01-S02] [R01-S03] [R01-S04] |
| Makoa Mata-mata | planned May 2027 | planned Dec 2028 | Future | [R01-S02] |
| Rolling | continuous | n/a | Can include breaking in-place updates | [R01-S02] |

- **[FACT]** The two sources disagree on the Kilted end of life: the REP-2000 file read gives "May 2025 - November 2026", the distributions table gives December 2026. [R01-S01] [R01-S02] Either way Kilted ends within weeks of this document's date, so it is not a target.
- **[FACT]** The REP-2000 copy read (repository `master`) stops at Kilted Kaiju and does not list Lyrical, so it is behind the distributions page. [R01-S01] [R01-S02] Lyrical platform tiers therefore come from the Lyrical supported-platforms page. [R01-S04]
- **[FACT]** A new distribution is released each year on 23 May; LTS and non-LTS releases alternate. LTS targets one Ubuntu LTS at Tier 1 and is supported for five years. [R01-S01] [R01-S02] (The Lyrical release date in the table is 22 May 2026, so "23 May" is a stated intent, not an invariant. [R01-S02])
- **[FACT]** Nodes built against different distributions are not guaranteed to interoperate. [R01-S02] This matters for any robot and fleet server on different ROS releases.
- **[FACT]** Tier 1 RMW implementations on Lyrical are Fast DDS (default), Cyclone DDS, RTI Connext (not arm64) and Zenoh. [R01-S04] The Lyrical notes also add features relevant to a robot platform: a callback-group events executor reported as using 10 to 15 percent less CPU than the single and multithreaded executors, zero-copy style `rosidl::Buffer` for GPU data (Fast DDS and Zenoh RMWs), runtime tracing controls, and rosbag2 recorder services. [R01-S03] The CPU claim is the ROS project's own statement; its test conditions were not stated on the page. [UNRESOLVED]

**Implication [REC].** Treat ROS 2 as the mandatory middleware and plan for Lyrical (supported to May 2031) as the long-term anchor. Because third-party stacks lag a new distribution (Section 6.2), keep Jazzy (supported to May 2029) as a compatibility target for the first reference implementation until the dependencies Valtoryn needs are confirmed on Lyrical. Do not choose a non-LTS release.

### 2.3 Hardware abstraction: ros2_control

- **[FACT]** `ros2_control` separates a Controller Manager (loads, activates and updates controllers, matches the interfaces they require) from a Resource Manager that abstracts hardware as plugin "hardware components" of type System, Sensor or Actuator, described in the robot URDF through `<ros2_control>` tags. The control loop runs `read()`, controller `update()`, `write()`. [R01-S26]
- **[FACT]** Repository metadata on 2026-11-07: Apache-2.0, last commit 2026-11-06, 1,053 stars, 155 open issues, build jobs listed for Lyrical. [R01-S29] [R01-S26]
- **[REC]** This is the closest existing match to Valtoryn's "hardware abstraction" requirement and should be reused for actuators and sensors rather than reinvented. It describes joints and sensors, not locomotion class, payload, or capability to a fleet layer; that capability description (compare the VDA 5050 factsheet, Section 5.3) is a gap Valtoryn would fill.
- **[UNRESOLVED]** Whether the `ros2_controllers` set includes a controller adequate for every Valtoryn chassis type (differential, omnidirectional, steered) was not verified; the documentation page read only names the `ros2_controllers` repository. Resolution: read that repository's controller list.

---

## 3. Navigation: Nav2

### 3.1 Architecture

- **[FACT]** Nav2 is a behaviour-tree-orchestrated set of lifecycle-managed ROS 2 action servers: the BT Navigator calls planner, controller, smoother, behavior and route servers through action interfaces; each server hosts runtime-selected plugins (pluginlib) and shares one costmap representation, which avoids duplicating the expensive environmental model. [R01-S08] [R01-S07]
- **[FACT]** Navigation logic is an XML behaviour tree executed with BehaviorTree.CPP V4; a stock tree contains planning, control and a contextual recovery ladder (clear costmap, spin, wait, back up). Nav2 can itself be a subtree inside a larger BT. [R01-S08] [R01-S07]
- **[FACT]** A lifecycle manager brings servers up and, through a bond connection, takes the system down if a server crashes. [R01-S08]
- **[FACT]** Environmental representation is a layered 2D costmap with plugin layers (voxel, obstacle, static, inflation, spatio-temporal voxel, range, and others) and costmap filters for keep-out zones, speed-limit zones and preferred lanes. The footprint can be a circle or polygon and can change at runtime, for example after picking a pallet. [R01-S08] [R01-S09]
- **[FACT]** The state-estimation contract is the REP-105 frame tree (`map`, `odom`, `base_link`); `amcl` and SLAM Toolbox are the supplied localisation and mapping options, and lidar is not mandatory. [R01-S08]
- **[FACT]** A `nav2_waypoint_follower` exists with task-executor plugins. The Nav2 documentation describes two fleet philosophies, "dumb robot, smart dispatcher" and "smart robot, dumb dispatcher", and states that for the first the waypoint follower is sufficient on the robot, treating a request as one unit of work such as one pick. [R01-S08]
- **[FACT]** A route server computes routes over a pre-defined navigation graph of nodes and directional edges (lanes, allowed areas, teach-and-repeat), with edge scorers, route operations (speed-limit adjustment, collision monitor, rerouting service, event triggers) and only GeoJSON graph parsing at present. [R01-S08] [R01-S09] There are also docking and undocking BT actions. [R01-S09]

### 3.2 Kinematic coverage (relevant to "not only differential drive")

[FACT] The plugin tables list controller and planner support by drivetrain: [R01-S09]

| Component | Drivetrains listed |
|---|---|
| DWB controller | Differential, omnidirectional, legged |
| TEB controller | Ackermann, legged, omnidirectional, differential |
| Regulated Pure Pursuit | Ackermann, legged, differential |
| MPPI controller | Differential, omni, Ackermann |
| SmacPlannerHybrid | Ackermann, differential, omnidirectional, legged |
| SmacPlannerLattice | Differential, omnidirectional, Ackermann, legged, "arbitrary / custom" via pre-generated control sets |
| NavFn, SmacPlanner2D | Differential, omnidirectional, legged (holonomic-particle assumption) |

The original paper stated the early A* planner produced infeasible paths for non-circular non-holonomic robots and flagged this as future work; the plugin table above shows the project later added kinematically feasible planners. [FACT] [R01-S07] [R01-S09]

### 3.3 Evidence of performance, with a caution

The Nav2 paper reports a campus "ultra-marathon" with two differential-drive research robots (Tiago and RB-1): 37.4 miles in 22.8 hours, 168 recoveries, zero collisions and zero emergency stops, with both robots capped at 0.45 m/s for safety. [FACT] [R01-S07] The paper's table has internal inconsistencies:

- **[CALC]** Average speed implied by the table: 37.4 mi x 1609.344 m/mi = 60,190 m; 22.8 h x 3600 s/h = 82,080 s; 60,190 / 82,080 = 0.73 m/s. The paper states 0.37 m/s average and 0.45 m/s maximum. [R01-S07] The implied value exceeds the stated maximum, so either distance, duration or speed is mis-stated. (Inputs and reported speeds are from [R01-S07]; the conversion factor is a standard constant.)
- **[CALC]** Recoveries per mile: 168 / 37.4 = 4.49, against 4.3 reported in the total column. [R01-S07]

**Implication [REC].** Use the marathon as qualitative evidence that Nav2 runs for long periods around people on differential robots, not as a quantitative benchmark. Valtoryn must run its own navigation validation (simulation and, later, hardware) rather than cite this.

### 3.4 Limitations relevant to a warehouse platform

- **[FACT]** The Nav2 pages read describe single-robot navigation and an interface for a dispatcher; they do not describe inter-robot traffic coordination, reservation of shared aisles, or deadlock resolution. [R01-S08] [R01-S09] (An absence in the pages read, not a proven absence in the code base.)
- **[FACT]** The primary environment model is a 2D costmap; other representations (3D costmaps, gradient maps, meshes) are listed as "other forms" rather than the supported path. [R01-S08]
- **[FACT]** The paper notes that long repetitive corridors with many people degraded AMCL localisation confidence and triggered spin recoveries. [R01-S07] Warehouse aisles are repetitive; this is a known risk for 2D lidar localisation. [EST]

### 3.5 Licence and activity

- **[FACT]** The repository is multi-licensed per package: LGPL-2.1-or-later, Apache-2.0, BSD-3-Clause, and Apache-2.0 AND BSD-3-Clause; unmarked files default to Apache-2.0; each `package.xml` states the licence. [R01-S10] GitHub's API reports the licence as "other / NOASSERTION". [R01-S29]
- **[FACT]** Observed 2026-11-07: last push 2026-11-05, 5,012 stars, 2,015 forks, 109 open issues, latest release 1.5.3 published 2026-10-17 with target branch `lyrical` (release note "Lyrical sync Oct 16"). [R01-S29]
- **[FACT]** Project leadership, maintenance and professional support are provided by a company, Open Navigation LLC, funded by named sponsors including Dexory (a warehouse inventory robotics company), Nvidia, AMD, Polymath Robotics and Stereolabs. [R01-S10] This is a sustainability signal (a funded maintainer) and also a concentration risk. [EST]
- **[UNRESOLVED]** Which individual Nav2 packages are LGPL (versus Apache-2.0) was not checked. Resolution: read each package's `package.xml`.
- **[FACT]** SLAM Toolbox, the default SLAM option, is LGPL-2.1 per repository metadata (last push 2026-11-02, release 2.10.0 on 2026-07-21). [R01-S29]

**Implication [REC].** Reuse Nav2 as the on-robot navigation layer for all chassis types it supports, behind a Valtoryn interface so that planners, controllers and behaviour trees stay swappable. Track the licence of every Nav2 and SLAM dependency in a bill of materials, because the platform will mix Apache-2.0, BSD and LGPL components.

---

## 4. Simulation: Gazebo and ros_gz

- **[FACT]** Gazebo releases are named, alphabetical, and made of semantically versioned libraries: Jetty (Sep 2025, LTS, end of life May 2031), Ionic (Sep 2024, EOL Dec 2026), Harmonic (Sep 2023, LTS, EOL May 2029), Fortress (Sep 2021, LTS, EOL May 2027), and a planned "M" release in March 2027. There is also a nightly rolling stream named Rotary, marked experimental. [R01-S11]
- **[FACT]** `ros_gz` provides the bridge (Gazebo Transport to ROS), image transport bridge, simulation launch helpers and point-cloud plugins. The compatibility table pairs Lyrical with Jetty (binaries on packages.ros.org), and Lyrical with Harmonic or Ionic (source only); Jazzy pairs with Harmonic (binaries) and Kilted with Ionic. [R01-S12]
- **[FACT]** Observed 2026-11-07: `gz-sim` Apache-2.0, last push 2026-11-06, latest release tag `gz-sim10_10.0.0` published 2025-10-14, 675 open issues; `ros_gz` Apache-2.0, last push 2026-11-05, 81 open issues. [R01-S29]
- **[FACT]** Nav2 itself uses Gazebo in continuous integration for system tests across robot kinematics. [R01-S07]
- **[UNRESOLVED]** Gazebo's suitability for warehouse-scale multi-robot throughput, wheel-floor contact fidelity and sensor noise realism was not evaluated here. That is the simulation workstream's question.

**Implication [REC].** Use Gazebo (Jetty with Lyrical, or Harmonic with Jazzy) as the default open simulator through `ros_gz`, behind a simulator abstraction, because the ROS release and Gazebo release pairing determines binary availability. Prefer an LTS Gazebo release.

---

## 5. Fleet and interoperability layer

### 5.1 Open-RMF

**What it is.** [FACT] Open-RMF (Robotics Middleware Framework) is a set of conventions, tools and ROS 2 software for letting multiple fleets, including from different vendors, share traffic space and building infrastructure such as doors and lifts. [R01-S13] The "RMF Core" consists of `rmf_traffic` (scheduling and traffic management), `rmf_traffic_ros2`, `rmf_task` (task planner), `rmf_battery`, `rmf_ros2` (adapters, nodes, Python bindings) and `rmf_utils`. [R01-S13]

**Architecture pattern.**

- **[FACT]** A centralised Traffic Schedule Database holds the intended trajectories of all participants. Each fleet manager must report itineraries; compliant fleets plan routes that avoid conflicts. When a conflict is detected the schedule notifies the fleets and a negotiation starts: each fleet proposes itineraries and a third-party "judge" chosen by the integrator selects among them. [R01-S13]
- **[FACT]** Each fleet connects through a fleet adapter. Four control categories are defined: Full Control (RMF commands paths), Traffic Light (RMF can only pause and resume), Read Only (status only; at most one such fleet is allowed per shared space), and No Interface (not compatible). A reusable C++ API with Python bindings exists for Full Control; Traffic Light has no reusable API. [R01-S13]
- **[FACT]** The Full Control adapter API centres on four classes (`Adapter`, `FleetUpdateHandle`, `RobotUpdateHandle`, `RobotCommandHandle`), and an `EasyFullControl` helper builds an adapter from YAML configuration plus user callbacks. The adapter plans only along an integrator-supplied route map (navigation graph). [R01-S16]
- **[FACT]** Tasks are bid out: a dispatcher node sends `BidNotice` to fleet adapters, adapters return `BidProposal` costs from an `rmf_task` task planner, and the dispatcher awards the task. Out-of-the-box task types are Clean, Delivery and Loop; charging tasks are inserted automatically using battery estimates, assuming one dedicated charger per robot. [R01-S14]
- **[FACT]** The shipped path planner targets vehicles that behave like AGVs following predetermined routes on a grid; the book states the intent to add similar support for AMRs with ad hoc free-space planning later. [R01-S13] The roadmap still lists "free space traffic negotiation", a reservation system, queuing, hierarchical planning and Zenoh as work items, with the stated reason that DDS discovery and the lack of message keys in ROS 2 make Open-RMF's communication inefficient over Wi-Fi at large agent counts. [R01-S15]
- **[FACT]** `free_fleet` is a Python Open-RMF fleet adapter for robots without their own fleet manager. It uses Zenoh bridges to reach robots running ROS 2 Nav2 (via the `navigate_to_pose` behaviour only for now) or ROS 1 Navigation; the older DDS-based client/server version is marked legacy. Verified-support statement in its README: Ubuntu 24.04, Jazzy, `rmw_cyclonedds_cpp`. [R01-S17]

**Deployment evidence.** A peer-reviewed field test integrated Open-RMF at Tartu University Hospital with a PAL TIAGo using `free_fleet`; blood samples were carried from ICU to lab through two doors in a crowded corridor. [FACT] [R01-S19] Its authors call RMF "yet to reach full maturity" and list limits: RMF could not wait out corridor congestion, there is no emergency-stop handling model for staff, and legacy doors needed retrofits. [FACT] [R01-S19] Heterogeneous robots grouped under one fleet adapter hide per-robot characteristics from RMF and can cause undefined behaviour. [FACT] [R01-S19] Two robots (TIAGo and a Jackal) were demonstrated together only in a test environment, not in the hospital. [FACT] [R01-S19] I did not verify other claimed production deployments (for example Singapore healthcare programmes); only search snippets were seen. [UNRESOLVED]

**Does not do (per the sources).**

- **[FACT]** No inventory, order, or pick logic; the tasks are building-logistics tasks (clean, deliver, loop). [R01-S14]
- The Open-RMF text read does not claim any safety function; by its design it coordinates intended trajectories and building resources and does not replace on-robot safety. [EST] (Absence of a claim in [R01-S13], not an explicit disclaimer.)
- **[FACT]** Eleven Open-RMF book chapter files that were downloaded and searched contain no mention of VDA 5050 (RMF core, integration, fleets, free fleet, read-only fleets, nav maps, tasks, task planner, FAQ, roadmap, introduction). [R01-S13] [R01-S14] [R01-S15] [R01-S16] A migration guide from an Open-RMF fleet adapter to a VDA 5050 adapter exists in the `vda5050_core` repository (Section 5.3). [R01-S22]

**Licence and activity (observed 2026-11-07).** [FACT] All Open-RMF repositories read are Apache-2.0. [R01-S29] Last pushes: `rmf_ros2` 2026-11-05 (tag 2.14.0, 91 open issues, 122 stars), `rmf_traffic` 2026-11-02 (tag 3.9.0), `rmf_task` 2026-11-02 (tag 2.11.0), `free_fleet` 2026-10-21 (release 1.3.0 on 2024-12-31), `rmf-web` 2026-11-06 (release 0.3.0 on 2025-08-05), `rmf_site` (experimental visualiser, 99 open issues) 2026-11-06. The umbrella `rmf` repository's last GitHub release is `release-jazzy-240617` (2024-06-17) and its last push is 2026-08-25. [R01-S29] The `rmf` README lists Humble, Jazzy, Kilted and Rolling as supported distributions and does not list Lyrical. [FACT] [R01-S18] (The README text was summarised by the fetch tool; see Limitations.) Lyrical support is therefore **[UNRESOLVED]**; resolution is to check the `rmf` repository branches or discourse announcements.

**Implication [REC].** Open-RMF is the only maintained open-source system found that implements multi-fleet traffic scheduling with negotiation and building-infrastructure adapters. It targets a different problem (heterogeneous fleets sharing spaces with doors and lifts) from a single-operator warehouse fleet with an inventory system. Valtoryn should (a) define its own fleet-coordination interface so Open-RMF can be one implementation, and (b) not make Valtoryn's robot-side software depend on RMF's DDS-centred runtime. Its centralised-schedule model and fleet-adapter categories are worth borrowing even if the code is not used.

### 5.2 Other open fleet components seen

- **[FACT]** NVIDIA Isaac Mission Dispatch is an Apache-2.0 cloud service (database microservice with REST API plus dispatch microservice) that talks to robots with VDA 5050 over MQTT. Its README says it does not handle task allocation or conflict resolution. Observed: release v5.0.0 on 2026-09-16, 106 stars. [R01-S24] [R01-S29] The VDA 5050 version it implements was not stated in the text read. [UNRESOLVED]
- **[FACT]** InOrbit's `ros_amr_interop` (BSD-3-Clause, last commit 2026-11-02, 117 stars) hosts ROS 2 packages to connect robots to interoperability standards; its README lists a MassRobotics AMR Interop sender for ROS 2 and related initiatives. [R01-S23] [R01-S29] The Isaac Mission Dispatch README points to a VDA 5050 ROS 2 connector from OTTO Motors and InOrbit AI as a compatible robot-side client. [R01-S24]
- **[FACT]** `tum-fml/vda5050_connector` (BSD-3-Clause) is another ROS-side VDA 5050 connector; repository metadata: last commit 2024-04-04, last release `v1.0.0-beta` on 2023-11-20, so it looks dormant. [R01-S29] The VDA 5050 version it implements was not established. [UNRESOLVED]

### 5.3 VDA 5050

**What it is.** [FACT] VDA 5050 is a vendor-neutral interface between a central fleet control and mobile robots, developed by the VDA and VDMA with the Karlsruhe Institute of Technology's IFL, which manages the repository. Use is "optional and non-binding". [R01-S20] The current release is 3.0.0, published 2026-03-18; the previous releases are 2.1.0 (2024-08-19) and 2.0.0 (2021-11-25). [FACT] [R01-S21] [R01-S29] The repository's last push was 2026-10-29, licence MIT, 536 stars. [R01-S29] The README states that where GitHub and the VDA's published PDF differ, the PDF is authoritative, and that the maintainers owe no support. [FACT] [R01-S21] The PDF was not opened; the GitHub markdown was. [UNRESOLVED differences, if any]

**Transport and topics.** [FACT] [R01-S20]

| Topic | Direction | Status | Purpose |
|---|---|---|---|
| `order` | fleet control to robot | mandatory | Node/edge graph segment plus actions |
| `instantActions` | fleet control to robot | mandatory | Immediate actions (pause, cancel, signals, map handling) |
| `state` | robot to fleet control | mandatory | Order progress, actions, errors, load, battery, position, requests |
| `connection` | broker/robot to fleet control | mandatory | Online/offline via MQTT last-will, retained |
| `factsheet` | robot to fleet control | mandatory | Robot type, kinematics, limits, geometry, load |
| `visualization` | robot to viewers | optional | High-rate position and planned path |
| `zoneSet` | fleet control to robot | optional | Zone sets (blocked, release, speed limit, etc.) |
| `responses` | fleet control to robot | optional | Replies to robot-initiated requests |

- **[FACT]** Messages are JSON over MQTT (3.1.1 minimum). QoS 0 is specified for all topics except `connection`, which uses QoS 1. Topic levels are suggested as `interfaceName/majorVersion/manufacturer/serialNumber/topic`. [R01-S20]
- **[FACT]** The order model is a node/edge graph with a "base" (released, must be driven) and a "horizon" (planned, not released). The robot stops at the end of the base unless the fleet control extends it. The base cannot be changed, because messages are asynchronous and wireless links are unreliable. [R01-S20]
- **[FACT]** Version 3 adds features that bridge toward free-navigating AMRs: edge corridors that let a robot deviate within bounds after requesting release, a generic request/response mechanism with leases and revocation, zone types, map download/enable/delete via actions, and robot-shared planned paths (NURBS and polyline) in `state`. [R01-S20]
- **[FACT]** Predefined actions include pause, charging, position initialisation, map and zone-set handling, `pick`, `drop`, `detectObject`, `finePositioning`, `waitForTrigger`, certificate update and others; `cancelOrder`, `startPause` and `stopPause` are mandatory for every robot. [R01-S20]
- **[FACT]** The factsheet declares kinematics (`DIFFERENTIAL`, `OMNIDIRECTIONAL`, `THREE_WHEEL`, extensible), class (forklift, conveyor, tugger, carrier, extensible), localisation types, navigation types (physical line, virtual line, freely navigating), supported zones, speeds, accelerations and geometry. [R01-S20]

**Explicitly out of scope.** [FACT] Safety requirements (it "shall not be regarded or applied as a safety standard"), traffic management logic (routing, prioritisation, deadlock resolution), interfaces to peripherals and external IT systems, project procedures, operational responsibilities and cybersecurity measures. [R01-S20] The specification does list what a fleet control should do (order assignment, route calculation, deadlock resolution, energy management, communication with doors and elevators) but does not define how. [FACT] [R01-S20]

**Ecosystem maturity and gaps.**

- **[FACT]** `ros-industrial/vda5050_core` (Apache-2.0, created 2025-06-25, first release 0.1.0 on 2026-10-30, 15 stars) offers C++ and Python client and master libraries with an MQTT abstraction, validation, Layout Interchange Format (LIF) support and an Open-RMF migration guide. Its README says it supports VDA 5050 v2.0.0. [R01-S22] [R01-S29]
- **[CALC]** The spec release of 3.0.0 on 2026-03-18 and the library's support of 2.0.0 imply the open library is at least one major version behind the current standard as of 2026-11-07 (versions taken from [R01-S21] and [R01-S22]). The semantic versioning statement in the spec says major versions "typically involve breaking changes". [FACT] [R01-S20]
- **[FACT]** OTTO states that its AMRs are certified with VDA 5050 fleet software from Idealworks, NAiSE and SYNAOS, that it open-sourced its connector in 2023, and that VDA 5050 works best in standardised facilities with predictable routes; it recommends orchestration middleware for dynamic environments. [R01-S32] This is a vendor press release.
- **[FACT]** The MassRobotics AMR Interoperability Standard (JSON schema, PDF description, sample sender and receiver) covers sharing of location, speed, direction, health and tasking information. Its repository has release 1.0 on 2021-05-17, last commit 2021-10-08, and no licence detected by GitHub. [R01-S25] [R01-S29] The PDF and message semantics were not read. [UNRESOLVED]

**Implication [REC].** Adopt VDA 5050 (target 3.0.x) as the external fleet-to-robot protocol. Do not make it the internal architecture: it is an MQTT/JSON edge-graph interface with QoS 0 and no security, so Valtoryn needs its own internal contracts (ROS 2 actions, state model). Contributing a v3.0 implementation to an existing open library is likely cheaper than writing a separate stack; evaluate `vda5050_core` first. A VDA 5050 gateway on each robot (translating orders to Nav2 or BT goals, and state back) is a bounded piece of work.

---

## 6. Open-source AMR platforms and projects

### 6.1 What exists

| Project | What it is | Licence | Last activity seen | What it tells Valtoryn |
|---|---|---|---|---|
| TurtleBot 4 | ROS 2 education/research robot: iRobot Create 3 base, Raspberry Pi 4B, RPLIDAR A1M8, OAK-D camera, 9 kg payload, 0.31 m/s (safe mode) | Apache-2.0 (`turtlebot4` repo) | last commit 2025-09-09 | A reference for packaging a ROS 2 robot; far from warehouse payload or speed [R01-S27] [R01-S29] |
| Husarion ROSbot 3 | 4-wheel mecanum/standard indoor AMR, Raspberry Pi 5, Husarion OS (Ubuntu 24.04, ROS 2 Jazzy) with snap drivers and a web UI, up to 5 kg | Apache-2.0 (`rosbot_ros`) | last commit 2026-11-06 | Shows a vendor shipping an OS image plus snaps; small payload [R01-S28] [R01-S29] |
| Open-RMF + `free_fleet` | Fleet coordination, Section 5.1 | Apache-2.0 | Section 5.1 | Closest to a fleet layer |
| Isaac Mission Dispatch | VDA 5050 mission service | Apache-2.0 | 2026-09-16 release | Mission layer without allocation [R01-S24] |
| Nav2 + SLAM Toolbox + ros2_control | Navigation, mapping, hardware abstraction | mixed / LGPL / Apache-2.0 | Section 2 to 3 | Reusable core |

- **[FACT]** I found no open-source repository combining warehouse order management, fleet traffic scheduling, VDA 5050 3.x, digital twin and robot software in one maintained stack. Searches surfaced hobby and research repositories (a "multi-robot fleet" monorepo, a CPU-only planner demo, a web fleet system posted to the ROS discourse in 2026, an ACM architecture paper), none of which I opened. [UNRESOLVED] Absence of evidence from search is not proof of absence; resolution would be a systematic survey of GitHub topics `amr` and `fleet-management`.
- **[FACT]** The two reference robots read (TurtleBot 4 and ROSbot) are small research and education robots (9 kg and 5 kg payload), not warehouse carriers. [R01-S27] [R01-S28] They are useful as low-cost software-development targets for navigation and HIL-style bring-up, not as design references for load-carrying chassis. [REC]

### 6.2 Dependency lag

- **[FACT]** ROS 2 Lyrical was released 2026-05-22; Nav2 published a Lyrical-targeted release on 2026-10-17; `ros_gz` and `ros2_control` list Lyrical; the Open-RMF README read does not. [R01-S02] [R01-S29] [R01-S12] [R01-S26] [R01-S18]
- **[REC]** Valtoryn should maintain a dependency compatibility matrix (ROS release, Gazebo release, Nav2 version, RMF version, VDA 5050 library version) as a first-class artifact and decide the primary distribution only after verifying every must-have dependency.

---

## 7. Commercial and industrial architectures (public information only)

Public architecture detail is thin for every vendor below; proprietary robot internals are not published. What follows is limited to statements the vendors or papers make, labelled as vendor claims.

| Vendor / system | Publicly documented structure | Scale claims (vendor) | Interoperability stance | Thin spots |
|---|---|---|---|---|
| Amazon Robotics | Amazon states it designs, builds and operates its own fleet; robots include Hercules (lifts up to 1,250 lb), Pegasus (conveyor), Proteus (autonomous, open areas); a "DeepFleet" generative model coordinates fleet movement [R01-S37] | 1 millionth robot, more than 300 facilities, 10 percent travel-time improvement claim (2025-07-01) [R01-S37] | Proprietary | The Kiva/Wurman 2008 paper could not be retrieved (Section 9); no architecture or algorithm detail can be cited |
| MiR (Mobile Industrial Robots) | Robots plus web-based MiR Fleet; fleet shares site/map/missions; REST Integration API with webhooks, event subscriptions, snapshots and "serial-orders"; resources (positions, markers, limit-robot and lock zones) have occupancy tracking and robot queues with no stated limit [R01-S30] [R01-S31] | "up to 100" robots (FAQ) and "over 100 AMRs" (scalability text) on the same page [R01-S30] | REST for ERP/MES/WMS; no VDA 5050 statement found on the page read | Documentation states Fleet handles "limited traffic and resource management" and the integrator must define behaviours [R01-S31] |
| OTTO (Rockwell Automation) | Built on ROS 2 from early on; ROS 1 multi-master could not test beyond 25 robots, ROS 2 allowed 100+ per facility; fleet manager software [R01-S06] [R01-S32] | "thousands" of robots, fleets over 100 in one facility (2022 paper); over ten million driving hours (press release) [R01-S06] [R01-S32] | VDA 5050 certification with three fleet vendors; open-sourced connector 2023 [R01-S32] | Fleet manager internals not public |
| Locus Robotics | LocusONE orchestration of robots and people ("System Directed Labor"); mixed fleet of Origin, Vector, Array robots; standard APIs to WMS/WES/WCS [R01-S33] | 22K+ robots, 360+ sites, largest single-site fleet 800+ (page dated 2026-06-21) [R01-S33] | WMS integration, 65+ WMS/ERP | No protocol or algorithm detail |
| Geek+ | Shelf-to-person system: WES + Robot Management System (path planning, scheduling, task allocation, charging, monitoring) + analytics platform; safety by fencing, interlocked doors, light curtains and a safety PLC [R01-S35] | RMS "5,000+ robots" and "10,000 tasks per second" (2024), MAPF-based path planning with 15 percent+ throughput claim [R01-S34] | White/gray/black-box integration with 100+ WMS/ERP [R01-S35] | Figures are marketing claims, no test conditions |
| Zebra / Fetch | Fleet orchestration called Symmetry [R01-S36] | none verified | n/a | Trade press reports Zebra announced in December 2025 it was winding down the unit and Skild AI acquired the division (reported 2026-04-16); unclear if the AMR line continues [R01-S36] (weak source) |

**Observations drawn from the table.**

1. **[FACT]** The commercial pattern is a vendor-owned fleet manager sitting between the customer's WMS/ERP and the robots, exposed through REST or similar APIs, with traffic coordination inside the vendor product. [R01-S31] [R01-S33] [R01-S35]
2. **[FACT]** MiR describes traffic handling as resource-based (positions, zones, queues) rather than trajectory-time scheduling, and calls its traffic and resource management "limited". [R01-S31] Geek+ states multi-agent path finding (MAPF) based planning. [R01-S34] These point to two architecture families: lock/resource-based coordination and path-based coordination. [EST] (Interpretation of the quoted vendor text.)
3. **[FACT]** Geek+ achieves human safety in shelf-to-person systems largely through physical segregation and a safety PLC. [R01-S35] Open software does not provide this; it is a hardware and process decision.
4. **[FACT]** Interoperability is emerging through VDA 5050 in the intralogistics segment (OTTO certification), and the vendor itself says it suits predictable environments. [R01-S32]
5. **[FACT]** Market volatility is real: a former leading AMR vendor line (Fetch) changed hands after a wind-down announcement. [R01-S36] This supports the argument for an open, vendor-independent platform but is a single weakly sourced data point. [EST]

**Implication [REC].** Valtoryn should not try to match proprietary fleet-manager feature breadth. It should offer open, documented interfaces at the points where vendors lock customers in: the WMS/ERP-facing task API, the fleet-to-robot protocol (VDA 5050), and the robot-side hardware abstraction.

---

## 8. Capability gap and opportunity analysis

Legend: **Reuse** = adopt existing open component as-is; **Adapt** = adopt and extend or wrap; **Build** = no adequate open option found; **Evaluate** = not enough evidence. All assignments are [REC].

| Layer | Best open option found | Maturity signal | Gap / risk | Valtoryn action [REC] |
|---|---|---|---|---|
| Middleware, tooling | ROS 2 (Lyrical LTS to 2031; Jazzy to 2029) [R01-S02] | Annual releases, five-year LTS | Cross-distribution interop not guaranteed [R01-S02]; DDS tuning over Wi-Fi [R01-S06] | **Reuse**; pin one LTS per release; evaluate Zenoh RMW (Tier 1 since Kilted) for Wi-Fi fleets [R01-S05] |
| Hardware abstraction | `ros2_control` [R01-S26] | Active, Apache-2.0 | No fleet-visible capability/payload model | **Reuse** for I/O; **Build** a capability descriptor on top |
| Localisation / mapping | Nav2 AMCL, SLAM Toolbox (LGPL) [R01-S08] [R01-S29] | Active | 2D focus; repetitive aisles degraded AMCL in paper [R01-S07] | **Reuse**; **Evaluate** for racks and aisles; keep swappable |
| Local and global navigation | Nav2 planners and controllers, multi-kinematics [R01-S09] | Very active, funded maintainer [R01-S10] | Single-robot scope; warehouse docking and load handling not provided (docking exists) | **Reuse** behind an interface |
| Lane-based routing | Nav2 route server (GeoJSON graph) [R01-S08] [R01-S09] | New component; maturity not assessed | Graph format vs VDA 5050 nodes/edges | **Evaluate** as robot-side lane executor |
| On-robot task logic | BehaviorTree.CPP (MIT, release 4.9.0 on 2026-02-11) [R01-S29]; Nav2 BT nodes [R01-S09] | Active | Warehouse primitives (pick, drop, handshake, dock to conveyor) not shipped | **Reuse** BT engine; **Build** warehouse task library |
| Fleet traffic scheduling | Open-RMF `rmf_traffic` [R01-S13] | Active, thin star count; hospital field test with caveats [R01-S19] | AGV-grid planner; free-space negotiation on roadmap; DDS efficiency; Lyrical not confirmed [R01-S15] [R01-S18] | **Adapt** behind a Valtoryn coordination interface; **Build** a minimal reservation-based baseline |
| Fleet-to-robot protocol | VDA 5050 3.0.0 [R01-S21] | Standards body; vendor adoption | Open libraries lag (v2.0.0) [R01-S22]; no security, QoS 0 [R01-S20] | **Adopt** spec; **Adapt/contribute** to `vda5050_core`; **Build** a robot-side v3 gateway if upstream stalls |
| Mission dispatch | Isaac Mission Dispatch [R01-S24] | Active | No allocation or conflict resolution [R01-S24] | **Evaluate**; likely **Build** thin master control |
| Task/order management and WMS API | None found | n/a | Gap: no open WMS-facing task API linking orders, inventory and robot tasks | **Build** (thin, interface-first) |
| Task allocation | `rmf_task` bidding [R01-S14] | Active | Task types are clean/delivery/loop | **Adapt** pattern; **Build** warehouse costs |
| Simulation | Gazebo via `ros_gz` [R01-S11] [R01-S12] | LTS to 2031 | Fidelity and scale unverified | **Reuse**; **Evaluate** in R-simulation workstream |
| Digital twin / fleet-scale sim | Open-RMF site editor (experimental) [R01-S15] [R01-S29] | Experimental | Planned features still on roadmap | **Build** or **Evaluate** |
| Operator UI | `rmf-web` [R01-S29] | Active, release 0.3.0 | Tied to RMF data model | **Evaluate**; likely **Build** a thin UI over Valtoryn APIs |
| Interop (non-VDA) | MassRobotics standard [R01-S25] | Dormant since 2021 | Unlicensed repo, unverified adoption | **Skip** as primary; consider a read-only exporter later |
| Security | SROS2 / DDS-Security [R01-S06]; VDA 5050 has `updateCertificate` action [R01-S20] | Present | Fleet MQTT profile not specified by VDA [R01-S20] | **Build** a documented TLS/mTLS profile |
| HIL, hardware test | none found in this research | n/a | Gap | Out of R01 scope; assign to HIL workstream |
| Safety | out of scope of every open component above | n/a | Open software offers none [R01-S20] | Hardware and standards workstream |

### Reuse versus build: summary statement [REC]

- **Reuse (do not rebuild):** ROS 2 and its tooling; `ros2_control`; Nav2 (planners, controllers, costmaps, BT navigator, docking, route server subject to evaluation); BehaviorTree.CPP; SLAM Toolbox and AMCL; Gazebo with `ros_gz`; the VDA 5050 specification.
- **Adapt or contribute upstream:** a VDA 5050 3.x client and master library (start from `vda5050_core`); Open-RMF traffic scheduling as an optional coordination backend; `rmf_task`-style bidding.
- **Build (Valtoryn's differentiating layers):** a vendor-neutral capability/payload descriptor above `ros2_control`; warehouse task primitives and a task/order API toward a WMS; a lightweight baseline fleet coordinator (reservation and queue based) usable without full Open-RMF; fleet-scale simulation and digital twin tooling; the security profile for MQTT and ROS 2 fleet links; the compatibility matrix and release process tying these together.
- **Do not build:** a new middleware, a new navigation stack, a new simulator, or a safety layer.

---

## 9. Limitations of this research

- **Bot-blocked official sites.** docs.ros.org, ros.org/reps and ojs.aaai.org returned a proof-of-work challenge; I did not bypass it. ROS release facts come from the ROS 2 documentation source files on GitHub, and the REP-2000 source file there is behind the current distributions page (no Lyrical entry). [R01-S01] [R01-S02]
- **Summarised sources.** Three sources were read through the WebFetch tool, which returns a model-generated summary of the page rather than the text: the Lyrical supported platforms page [R01-S04], the Kilted release notes [R01-S05], and the Open-RMF `rmf` README [R01-S18]. Facts from those three should be re-checked against the originals before being quoted.
- **GitHub metrics are snapshots.** Stars, issue counts and last-push dates were read on 2026-11-07 (some via the authenticated `gh` command line, others via anonymous API and fetch tools). Stars measure attention, not quality. A repository's "last push" can include branch housekeeping.
- **Vendor claims are unverified.** Robot counts, throughput and cost-saving numbers (including the Geek+, Locus, Amazon, MiR and OTTO figures) come from the vendors' own pages. The Amazon page was read; the Kiva paper was not.
- **No hands-on testing.** Nothing was installed, built or run; no capability was tested. Statements about what a package "does" come from its documentation or paper.
- **The Nav2 marathon table is internally inconsistent** (Section 3.3).
- **Commercial detail is thin.** Locus, Geek+ and Zebra architecture beyond marketing descriptions is not public in the pages read; MiR is the only vendor whose integration documentation was read in depth.
- **Safety and cybersecurity** of every component were not assessed.

## 10. Unresolved questions

1. Does Open-RMF support ROS 2 Lyrical, and when? (Check `rmf` branches and release notes.)
2. Which Nav2 packages are LGPL, and what is the combined licence footprint of a Valtoryn reference build? (Read `package.xml` files.)
3. Which VDA 5050 version does Isaac Mission Dispatch v5.0.0 implement, and are there open-source implementations of VDA 5050 3.x? (Read its documentation and search for v3 implementations.)
4. What are the message semantics and transport of the MassRobotics standard, and is anyone using it in production? (Read the PDF; seek adoption evidence.)
5. How does the Kiva/Amazon coordination approach work, per the Wurman et al. 2008 paper? (Retrieve from an unblocked mirror or via library access.)
6. Does Nav2's route server meet warehouse lane requirements, and how does its GeoJSON graph map to VDA 5050 nodes and edges? (Prototype in the planning phase.)
7. Which `ros2_controllers` cover steered, omnidirectional and non-differential chassis adequately? (Read the controller list and their docs.)
8. Is Zenoh as RMW mature enough for 100-robot Wi-Fi fleets? (Needs a measured test; only the Tier 1 declaration and Open-RMF's roadmap statement were seen.)
9. The CPU-saving claim for the Lyrical events executor: test conditions unknown. (Read the linked pull requests.)
10. Is there a maintained open-source warehouse-order-to-robot-task layer I missed? (Systematic GitHub survey.)

---

## 11. Sources

| ID | Title | Organization / author | URL | Published / revision date | Accessed | What it supports |
|---|---|---|---|---|---|---|
| R01-S01 | REP 2000: ROS 2 Releases and Target Platforms (source file, repository master) | Open Robotics / ROS community (M. Arguedas et al.) | https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-2000.rst | Last "Created" entry 10-Nov-2023 (content lists Kilted, not Lyrical) | 2026-11-07 | Release cadence, support policy, Tier definitions, Jazzy and Kilted tiers and dates |
| R01-S02 | ROS 2 "Distributions" page (documentation source `Releases.rst`) | Open Robotics, ros2_documentation repo | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Releases.rst | n/a (not stated on page) | 2026-11-07 | Release dates, EOL dates, Makoa Mata-mata plan, Rolling, cross-distribution note |
| R01-S03 | Lyrical Luth release notes (source `Release-Lyrical-Luth.rst`) | Open Robotics, ros2_documentation repo | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Releases/Release-Lyrical-Luth.rst | May 2026 (release) | 2026-11-07 | Lyrical LTS to May 2031 and new features |
| R01-S04 | Lyrical supported platforms (source `lyrical/supported-platforms.rst`; read via summarising fetch tool) | Open Robotics, ros2_documentation repo | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Releases/lyrical/supported-platforms.rst | n/a (not stated on page) | 2026-11-07 | Lyrical Tier 1 platforms and RMW tiers |
| R01-S05 | Kilted Kaiju release notes (source `Release-Kilted-Kaiju.rst`; read via summarising fetch tool) | Open Robotics, ros2_documentation repo | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Releases/Release-Kilted-Kaiju.rst | May 2025 (release) | 2026-11-07 | `rmw_zenoh_cpp` Tier 1 in Kilted |
| R01-S06 | Robot Operating System 2: Design, Architecture, and Uses In The Wild (arXiv v1 of Science Robotics manuscript) | S. Macenski, T. Foote, B. Gerkey, C. Lalancette, W. Woodall | https://arxiv.org/pdf/2211.07752 | 14 Nov 2022 (arXiv v1; accepted manuscript) | 2026-11-07 | ROS 2 design, layers, QoS, security, benchmarks, OTTO case study |
| R01-S07 | The Marathon 2: A Navigation System (arXiv v2) | S. Macenski, F. Martin, R. White, J. G. Clavero | https://arxiv.org/pdf/2003.00368 | 14 Jul 2020 (arXiv v2) | 2026-11-07 | Nav2 original architecture, plugins, experiment, limitations |
| R01-S08 | Nav2 documentation: Navigation Concepts | Nav2 / Open Navigation | https://docs.nav2.org/rolling/getting_started/navigation_concepts/navigation_servers/ | n/a (not stated on page) | 2026-11-07 | Servers, BT, lifecycle, costmaps, route server, waypoint follower |
| R01-S09 | Nav2 documentation: Navigation Plugins | Nav2 / Open Navigation | https://docs.nav2.org/rolling/configuration_and_development/navigation_plugins/ | n/a (not stated on page) | 2026-11-07 | Plugin catalogue, drivetrain support table, BT nodes, route plugins |
| R01-S10 | navigation2 repository README and LICENSE | Nav2 / Open Navigation LLC | https://raw.githubusercontent.com/ros-navigation/navigation2/main/README.md and .../LICENSE | n/a (not stated on page) | 2026-11-07 | Multi-licensing, sponsors, maintainer organisation |
| R01-S11 | Gazebo Releases | Open Robotics / Gazebo project | https://gazebosim.org/docs/all/releases/ | n/a (not stated on page) | 2026-11-07 | Gazebo release lineage, LTS and EOL dates, Rotary |
| R01-S12 | ros_gz README | Gazebo project | https://raw.githubusercontent.com/gazebosim/ros_gz/ros2/README.md | n/a (not stated on page) | 2026-11-07 | ROS-Gazebo pairing table and package list |
| R01-S13 | Open-RMF book: RMF Core Overview (`rmf-core.md`) | Open Robotics / OSRF, ros2multirobotbook | https://raw.githubusercontent.com/osrf/ros2multirobotbook/master/src/rmf-core.md | n/a (repo last push 2026-08-13) | 2026-11-07 | Traffic schedule, negotiation, fleet adapter categories |
| R01-S14 | Open-RMF book: Tasks in RMF (`task.md`) | Open Robotics / OSRF | https://raw.githubusercontent.com/osrf/ros2multirobotbook/master/src/task.md | n/a (not stated on page) | 2026-11-07 | Bidding dispatcher, task types, charging |
| R01-S15 | Open-RMF book: Roadmap (`roadmap.md`) | Open Robotics / OSRF | https://raw.githubusercontent.com/osrf/ros2multirobotbook/master/src/roadmap.md | n/a (not stated on page) | 2026-11-07 | Planned scalability, Zenoh, free-space negotiation, site tooling |
| R01-S16 | Open-RMF book: Mobile Robot Fleet Integration (`integration_fleets.md`) | Open Robotics / OSRF | https://raw.githubusercontent.com/osrf/ros2multirobotbook/master/src/integration_fleets.md | n/a (not stated on page) | 2026-11-07 | Full Control adapter API classes, route map |
| R01-S17 | Open-RMF book: Free Fleet Adapter, and free_fleet README | Open Robotics / OSRF; open-rmf | https://raw.githubusercontent.com/osrf/ros2multirobotbook/master/src/integration_free_fleet_adapter.md and https://raw.githubusercontent.com/open-rmf/free_fleet/main/README.md | n/a (not stated on page) | 2026-11-07 | free_fleet design, Zenoh, Nav2 integration, supported versions |
| R01-S18 | open-rmf/rmf README (read via summarising fetch tool) | open-rmf | https://raw.githubusercontent.com/open-rmf/rmf/main/README.md | n/a (not stated on page) | 2026-11-07 | Supported ROS distributions, branches, packages |
| R01-S19 | Scalable and heterogenous mobile robot fleet-based task automation in crowded hospital environments: a field test | R. Valner et al., Front. Robot. AI 9:922835 | https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2022.922835/full | 2022-08-23 | 2026-11-07 | Open-RMF field deployment, lessons and limitations |
| R01-S20 | VDA 5050 specification v3.0.0 (`VDA5050_EN.md`) | VDA, VDMA, KIT IFL | https://raw.githubusercontent.com/VDA5050/VDA5050/main/VDA5050_EN.md | Version 3.0.0 (release 2026-03-18) | 2026-11-07 | Scope, topics, MQTT, order model, actions, zones, requests, factsheet |
| R01-S21 | VDA5050 repository README | VDA5050 / KIT IFL | https://raw.githubusercontent.com/VDA5050/VDA5050/main/README.md | Version 3.0.0 | 2026-11-07 | Current version, authority of PDF, support disclaimer |
| R01-S22 | vda5050_core README and design document | ROS-Industrial | https://raw.githubusercontent.com/ros-industrial/vda5050_core/main/README.md and .../docs/design.md | n/a (not stated on page) | 2026-11-07 | Open VDA 5050 libraries, v2.0.0 support, architecture |
| R01-S23 | ros_amr_interop README | InOrbit | https://raw.githubusercontent.com/inorbit-ai/ros_amr_interop/main/README.md | n/a (not stated on page) | 2026-11-07 | MassRobotics sender, related initiatives |
| R01-S24 | Isaac Mission Dispatch README | NVIDIA | https://raw.githubusercontent.com/nvidia-isaac/isaac_mission_dispatch/main/README.md | n/a (not stated on page) | 2026-11-07 | VDA 5050 mission service, scope exclusions |
| R01-S25 | MassRobotics AMR Interoperability Standard README | MassRobotics | https://raw.githubusercontent.com/MassRobotics-AMR/AMR_Interop_Standard/main/README.md | Release 1.0 on 2021-05-17 | 2026-11-07 | Purpose and contents of the MassRobotics standard |
| R01-S26 | ros2_control Getting Started (Rolling documentation) | ros2_control maintainers | https://control.ros.org/master/doc/getting_started/getting_started.html | "Rolling Nov 2026" build | 2026-11-07 | Controller Manager, Resource Manager, hardware component types |
| R01-S27 | TurtleBot 4 User Manual: Features | Clearpath Robotics / Open Robotics (TurtleBot) | https://turtlebot.github.io/turtlebot4-user-manual/overview/features.html | 2025-11-19 | 2026-11-07 | TurtleBot 4 hardware and speed/payload |
| R01-S28 | ROSbot 3 manual | Husarion | https://husarion.com/manuals/rosbot/ | n/a (not stated on page) | 2026-11-07 | ROSbot hardware, software stack, payload |
| R01-S29 | GitHub REST API repository metadata (repos/<owner>/<repo>, releases, tags, commits) for: ros-navigation/navigation2, open-rmf/{rmf, rmf_ros2, rmf_traffic, rmf_task, rmf_traffic_editor, rmf_demos, rmf-web, rmf_site, free_fleet}, VDA5050/VDA5050, ros-industrial/vda5050_core, tum-fml/vda5050_connector, inorbit-ai/ros_amr_interop, MassRobotics-AMR/AMR_Interop_Standard, nvidia-isaac/isaac_mission_dispatch, gazebosim/{gz-sim, ros_gz, gz-physics}, ros-controls/ros2_control, ros2/rmw_zenoh, ros2/ros2, SteveMacenski/slam_toolbox, BehaviorTree/BehaviorTree.CPP, micro-ROS/micro_ros_setup, turtlebot/turtlebot4, husarion/rosbot_ros | GitHub | https://api.github.com/repos/ros-navigation/navigation2 (same endpoint pattern for each repository listed) | Observed 2026-11-07 | 2026-11-07 | Licence, last push/commit, stars, open issues, tags and releases |
| R01-S30 | MiR Fleet (product page) | Mobile Industrial Robots | https://mobile-industrial-robots.com/products/software/mir-fleet | n/a (not stated on page) | 2026-11-07 | MiR Fleet features, REST API, scale statements, IEC 62443 claim |
| R01-S31 | MiR Fleet Enterprise Documentation v1.2 (01/2025) | Mobile Industrial Robots A/S (hosted by reseller jk.de) | https://jk.de/media/a2/50/ce/1738939330/mir_fleet_enterprise_documentation_1.2_en.pdf?ts=1738939330 | 2025-01-20 (v1.2) | 2026-11-07 | Resource handling, Integration API, "limited traffic" statement, networking |
| R01-S32 | OTTO Adds VDA 5050 Certifications to Support Mixed-Fleet Deployments | OTTO by Rockwell Automation (press release on Automate show site) | https://www.automateshow.com/exhibitor-news/otto-adds-vda-5050-certifications-to-support-mixed-fleet-deployments | n/a (not stated on page) | 2026-11-07 | OTTO VDA 5050 certifications, connector open-sourced 2023 (vendor claim) |
| R01-S33 | LocusONE | Locus Robotics | https://locusrobotics.com/platform/locusone/ | 2026-06-21 (page metadata) | 2026-11-07 | LocusONE scope and scale claims (vendor) |
| R01-S34 | Geek+ Launches World's Most Powerful Robot Management System | Geekplus | https://www.geekplus.com/resources/news/geekplus_rms_upgrade | 2024-11-26 | 2026-11-07 | RMS scale and MAPF claims (vendor) |
| R01-S35 | Our Ultimate Shelf-to-Person Solution Guide: From A to Z | Geekplus | https://www.geekplus.com/resources/robotics-blogs/stpintro | 2023-11-28 | 2026-11-07 | Geek+ system structure, safety approach, integration modes |
| R01-S36 | Skild acquires Fetch Robotics assets from Zebra | The Robot Report (M. Oitzman) | https://www.therobotreport.com/skild-acquires-fetch-robotics-assets-from-zebra-automation/ | 2026-04-16 | 2026-11-07 | Zebra/Fetch wind-down and sale; Symmetry (trade press, weak) |
| R01-S37 | Amazon launches a new AI foundation model to power its robotic fleet and deploys its 1 millionth robot | Amazon (S. Dresser) | https://www.aboutamazon.com/news/operations/amazon-million-robots-ai-foundation-model | 2025-07-01 | 2026-11-07 | Amazon robot scale, DeepFleet, robot types (vendor claim) |

### Sources that could not be inspected (not cited)

- Wurman, D'Andrea, Mountz, "Coordinating Hundreds of Cooperative, Autonomous Vehicles in Warehouses", AI Magazine 29(1), 2008. The AAAI OJS site returned a proof-of-work challenge and the ACM, Wiley and Semantic Scholar pages blocked automated reads. No claim about Kiva architecture is made from it.
- docs.ros.org "Distributions" page, ros.org REP-2000 HTML and the docs.ros.org middleware-vendor page (proof-of-work challenge; source files on GitHub used instead).
- The Science Robotics version of record (science.org DOI 10.1126/scirobotics.abm6074): not fetched; the arXiv accepted manuscript was used.
- The VDA's published PDF of VDA 5050 on vda.de (not opened; GitHub markdown used).
- MassRobotics AMR_Interop_Standard.pdf (not opened).
- ISO 3691-4 (paywalled; only a definition quoted inside the VDA 5050 text was seen).
- Search-result-only items, not opened: TUM news item on the VDA 5050 ROS connector, the Changi/ROMI-H pages, the AMRF architecture paper (ACM), LGDXRobot Cloud discourse post, and assorted multi-robot GitHub repositories.
- MiR Academy REST API lesson (page content was not informative) and MiR community REST API reference (closed to partners per search snippet).
