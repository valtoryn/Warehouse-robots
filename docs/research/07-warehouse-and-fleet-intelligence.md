# R07 — Warehouse Automation and Fleet Intelligence
> **Status:** Research document — proposed findings, nothing here is implemented.
> **Workstream:** R07 · **Last verified:** 2026-11-07 · **Evidence legend:** see below

## Evidence legend

- **[FACT]** established by a cited source, always followed by a source ID such as [R07-S01].
- **[CALC]** derived by a shown calculation from cited or labelled inputs.
- **[EST]** engineering estimate or assumption (basis stated).
- **[REC]** Valtoryn recommendation or proposal (engineering judgement, not established fact).
- **[UNRESOLVED]** could not be established; what would resolve it is stated.

Nothing in this document describes an implemented Valtoryn capability. No Valtoryn hardware exists and nothing here was tested on hardware. Paywalled standards (ISO, ANSI/A3) were read only at catalogue/abstract level or through secondary public summaries; their full text was **not** inspected.

---

## 1. Scope and method

**Scope.** Warehouse material-transport patterns; docking and charging; pallet handling; task allocation; multi-robot coordination, traffic management and deadlock handling; facility graph representations; integration with WMS/WES/MES/ERP; heterogeneous fleets and capability-based dispatch; fleet-level failure handling, order lifecycle, idempotency and network partitions. Robot-level safety (including forklift-AMR safety) belongs to R08 and is referenced only. Localisation, mapping and local navigation belong to other workstreams.

**Method.** On 2026-11-07 I read, via fetch tools, the VDA 5050 v3.0.0 specification text (about 207,000 characters, in full for the sections used here), its GitHub release notes, the VDMA Layout Interchange Format (LIF) guideline, the Open-RMF documentation book, the `rmf_ros2` fleet-adapter header, `rmf_task` README and Open-RMF maintainer discourse posts, Nav2 docking and route-server documentation, the Gerkey and Matarić 2004 paper (full text), abstracts of the Korsah et al. 2013, Sharon et al. (CBS), Li et al. (lifelong MAPF, full text), Stern et al. and Čáp et al. papers, public manufacturer datasheets (MiR, Seegrid, OTTO), the EPAL pallet page, ISO/ANSI catalogue pages and a 2026 systematic review of autonomous forklifts. Every source cited was opened in this session; sources that blocked automated reading are listed at the end and are not cited.

**Limits that shape every conclusion.** (a) Vendor datasheets state maximum values under vendor-defined conditions; they are not independent measurements. (b) Several authoritative documents (iTax paper, CBS journal version, ISO/ANSI texts) were not available in full. (c) The Open-RMF documentation book partly predates current releases; where it conflicts with the code header or maintainer posts I say so.

---

## 2. Findings

### 2.1 AGV versus AMR: what credible sources actually say

| Source | Position | Tag |
|---|---|---|
| ISO 3691-4:2023 catalogue abstract | Treats "automated guided vehicle", "autonomous mobile robot", "automated guided cart", "tunnel tugger", "under cart" and similar as examples of one class, the driverless industrial truck. Excludes rail/mechanically guided and remotely controlled trucks. Contains no safety requirements for towed trailers. Edition 2, 2023-06; a draft revision (ISO/DIS 3691-4) is listed. | [FACT] [R07-S28] |
| ISO 3691-4:2020 (withdrawn) | Same naming-equivalence text; withdrawn and replaced by the 2023 edition. | [FACT] [R07-S29] |
| ANSI/A3 R15.08 (as quoted in a SICK article; full text not inspected) | An AGV follows predefined guide paths (virtual or physical) with collision avoidance and some adjustment; an AMR navigates by computing an obstacle-free path through free space. The series then defines "industrial mobile robot" types: A (platform only), B (platform plus passive/active attachments such as roller tables, conveyors, linear lifts, excluding manipulators), C (platform plus manipulator). | [FACT] [R07-S31], secondary |
| ANSI blog on R15.08 | Part 1 (design, edition reaffirmed 2026), Part 2 (2023, integration incl. fleets of IMRs), Part 3 (2026, user responsibilities). | [FACT] [R07-S30] |
| MHI blog (authored by a vendor employee) | The generally accepted AGV/AMR definitions are blurring; AGVs generally handle larger loads and high accurate lifting; mixed AGV+AMR operation is expected, connected through standards such as VDA 5050. | [FACT] [R07-S32], weak (opinion) |
| VDA 5050 v3.0.0 | Avoids the split: the single term "mobile robot" is a driverless transport system per ISO 3691-4, then divides into *line-guided* (follows predefined trajectories) and *freely navigating* (plans its own trajectory). | [FACT] [R07-S01] |
| ISO/TC 299 | Has a working group titled "Industrial mobile robot interoperability and communication" (WG 10). Outputs not inspected. | [FACT] [R07-S47]; outputs [UNRESOLVED] |

**Implication.** The standards world does not draw a hard AGV/AMR line; the useful engineering axes are *who plans the path* (fleet or robot), *what is the load interface*, and *what can be assumed about the floor*. [REC] Valtoryn should not encode "AGV" or "AMR" as a type; it should encode navigation mode (VDA 5050 vocabulary: line-guided vs freely navigating), load-handling interface and kinematics.

### 2.2 Material transport patterns and representative published specifications

Published figures below are vendor maxima; conditions are as stated by the vendor.

| Pattern | Representative product | Published figures | Source |
|---|---|---|---|
| Pallet pick-and-carry, floor-to-floor | MiR1200 Pallet Jack (AMR) | Max payload 1,200 kg; max speed 1.5 m/s at max payload on flat surface; "floor to floor" pick/place until further software release; EUR 1 pallets grade A and B; max fork lift height 1,140 mm; payload may overhang pallet footprint by at most 50 mm per side; max payload height 2,000 mm and not validated by the robot; pick-up up to 40 s / place up to 30 s from front entry, 55 s / 50 s from side entry; floor tilt tolerance for pick/place ±1°; min distance between pallets 300 mm side-to-side and 250 mm end-to-end; 500 mm to obstacles; 3 SICK safety scanners, 5 3D cameras, 1 3D LiDAR, 1 ultrasonic (pallet-seated check); designed to meet EN ISO 3691-4:2023 among others. | [FACT] [R07-S33] (spec sheet dated 2025-01-14) |
| Same product, web spec page | Width 820 mm, height 2,120 mm, weight 750 kg, active time up to 10 h. The dated PDF says 800 mm, 2,130 mm and 810 kg. The two vendor documents disagree; the web page is undated. | [FACT] [R07-S34], [R07-S33]; discrepancy unresolved |
| Pallet lift truck, racking | Seegrid Lift CR1 | 15 ft lift height, 4,000 lb capacity, 5 mph max automatic speed, forks 42 in standard (36–72 in optional); pick from floor or elevated staging up to 6 ft; layered safety with five 2D/3D LiDAR sensors; vendor states VDA 5050 support. | [FACT] [R07-S37] |
| Cart towing | MiR250 Hook (top module) | Cart gripping height 80–350 mm; max payload including cart 500 kg at 1 % incline but 300 kg at 5 % incline; speed 2.0 m/s on product page, 0.5 m/s cap on a 5 % incline at 300 kg; recommended acceleration 40 % of maximum (about 0.4 m/s²) at max payload; cart pick-up 48 s, place 18 s; identifies carts by AprilTags. | [FACT] [R07-S35] (2023-09-13), [R07-S36] |
| Heavy platform with attachments (incl. conveyors/lifts) | OTTO 1500 | Differential drive; "wide range of attachments"; payload up to 4,200 lb per page description (interactive spec values did not render); standards list includes ANSI/ITSDF B56.5, R15.08-1, ISO 3691-4. | [FACT] [R07-S38]; numeric table [UNRESOLVED] (datasheet PDF unreachable) |
| Conveyor-top | no product datasheet obtained | R15.08 Type B lists conveyors and roller tables as attachments; VDA 5050 has a `CONVEYOR` robot class and `stationType` values for passive/active conveyors. | [FACT] [R07-S31], [R07-S01]; product figures [UNRESOLVED] |

**Calculations from the published numbers.**

- Pallet overhang envelope: EUR pallet 1,200 × 800 mm [R07-S39] plus 50 mm per side [R07-S33] gives a maximum load footprint of 1,300 × 900 mm. [CALC]
- Deceleration implied by the MiR Hook braking table for the 558 kg cart [R07-S35]: a = v²/(2d). At 2.00 m/s with d = 2.95 m, a ≈ 0.68 m/s²; at 1.20 m/s with d = 1.06 m, a ≈ 0.68 m/s². For the 10 kg cart at 2.00 m/s with d = 1.28 m, a ≈ 1.56 m/s². Braking distance (and thus zone size and reservation margin) is strongly load-dependent. [CALC]
- Illustrative pallet cycle bound: 60 m one-way, loaded and empty both at 1.5 m/s (empty speed is not stated in the sources, so this is a conservative assumption), front-entry handling 40 s + 30 s: 2 × 60 / 1.5 = 80 s travel + 70 s handling = 150 s, about 24 cycles per hour per robot **before** traffic waits, charging, and failed picks. [CALC from R07-S33 inputs; empty speed [EST]]
- Unit conversions for Seegrid CR1: 4,000 lb × 0.45359 ≈ 1,814 kg; 5 mph × 0.44704 ≈ 2.24 m/s; 15 ft × 0.3048 ≈ 4.57 m. [CALC]

**Observed property of the datasheets that matters for dispatch.** Capability is conditional, not scalar: MiR Hook payload depends on incline; MiR1200 handling depends on pallet grade, overhang, floor tilt, adjacent clearances and "floor to floor" only. [FACT] [R07-S33][R07-S35]. A dispatcher that only knows "payload = 1,200 kg" would over-accept tasks.

### 2.3 Docking and charging

**Nav2 `opennav_docking` (now part of Nav2).**
- Docking server targets charging docks and also non-charging docking locations such as the end of a conveyor belt or a pallet; it uses plugin dock implementations and a database of dock instances to serve a heterogeneous environment. [FACT] [R07-S15]
- Procedure: look up dock and plugin, navigate to staging pose if outside the pre-staging tolerance (default 0.5 m L2 in x, y, theta), detect dock, run a vision-control loop on a refined dock pose, stop on contact or charging, wait for charging, retry up to `max_retries` (default 3). Timeouts: 5 s initial perception, 5 s charge confirmation, 30 s approach. [FACT] [R07-S15][R07-S16]
- Defaults worth knowing: `docking_threshold` 0.05 m (pose threshold at which `isDocked()` becomes true when stall detection is off), staging offset −0.7 m, approach speed 0.1–0.24 m/s, `fixed_frame` recommended as odometry rather than `map` so localisation error does not enter the final approach. These are software defaults, not measured docking accuracy. [FACT] [R07-S15][R07-S17]
- The tutorial states that a demo achieved a 100 % success rate; that is the package sponsor's demonstration, not a reliability measurement. [FACT] [R07-S17], weak evidence for reliability.
- The documentation states a docking server should be called by an application behaviour tree or autonomy application, not inside navigate-to-pose. [FACT] [R07-S15]
- Dock plugin API: `getStagingPose`, `getRefinedPose`, `isDocked`, `isCharging`, `disableCharging`, `hasStoppedCharging`; the docs recommend real dock detection, battery state and motor-effort feedback for production. [FACT] [R07-S16][R07-S17]

**VDA 5050 v3.0.0 charging and load actions.**
- `startCharging`/`stopCharging` are instant or node actions, idempotent; overcharge protection is stated to be the robot's responsibility; charging may occur at a spot (robot stopped) or on a charging lane (while driving). `pick`/`drop` are node or edge actions and are **not idempotent**; they carry optional `lhd`, `stationType`, `stationName`, `loadType`, `loadId`, `height`, `depth`, `side`. `finePositioning`, `detectObject` and `waitForTrigger` exist as node/edge/zone actions. [FACT] [R07-S01]
- Fleet-control duties include "energy management: charging orders can interrupt transfer orders". Factsheet `batteryCharging` carries critical low level (at or below which fleet control should only send orders to a charger), min/max desired level and minimum charging time. [FACT] [R07-S01]
- Charging area purpose in LIF is defined only by the presence of a charging action on the station's interaction node. [FACT] [R07-S43]

**Open-RMF.** A traffic-editor vertex can be flagged `is_charger`; `dock_name` makes the fleet adapter send a docking-mode request as the robot approaches (for custom docking sequences). Historically each robot needed its own dedicated charger; "dynamic charging" (changeable charger per robot) was announced in 2024. [FACT] [R07-S08][R07-S05][R07-S11]

**Contact versus inductive.** I found no neutral comparison. One manufacturer page for an inductive system states a position tolerance of 40 mm in every direction, start in under one second, and 93 % efficiency; these are vendor claims for that product. [FACT] [R07-S48], weak. For contact docks, the only quantified documentation I read is the Nav2 default thresholds above and the MiR1200 note that a charging manoeuvre needs a 3,500 mm operational corridor width [R07-S33]. Documented charge-station docking accuracy for specific contact stations: [UNRESOLVED]; resolve with the charger vendor's datasheet and a physical docking test series.

### 2.4 Pallet handling

- EPAL Euro pallet (EPAL 1): 800 × 1,200 × 144 mm, about 25 kg, safe working load 1,500 kg, 11 boards, 9 blocks, 78 nails; bottom pallet in a stack limited to 5,500 kg on solid even surface; non-exchangeable damage criteria include missing boards, split blocks, twisted blocks protruding over 10 mm. [FACT] [R07-S39]
- ISO 6780:2003 (flat pallets for intercontinental handling) specifies principal dimensions and tolerances and handling features (openings, clearances, chamfers); status confirmed 2026. The dimension table itself is behind the paywall: [UNRESOLVED], resolve by purchasing the standard. [FACT] [R07-S40]
- Perception requirements reported by a 2026 systematic review (122 papers, laboratory-dominated): lateral deviations beyond 2–3 cm or yaw beyond 1–2° can cause docking failure; pose estimation should reach 1–2 cm and 0.5–1.0° at 2–3 m approach; end-to-end latency below 150 ms; difficulty from up to 15° pallet skew, occlusion by overhanging loads, shrink-wrap texture and reflective floors; terminal docking is almost always visual servoing. The review also notes autonomous forklifts remain deployed at small scale (2–50 vehicles) and that validation is mostly laboratory scale. [FACT] [R07-S27] (secondary review; thresholds are its synthesis, not a standard)
- Product-level mitigation seen in the MiR1200 sheet: five 3D cameras for pallet and obstacle detection, ultrasonic check that the pallet is seated, explicit list of materials the robot cannot detect reliably (transparent, translucent, glossy, reflective, light-emitting), tilt and spacing limits. [FACT] [R07-S33]
- Nav2 docking supports pallets as "dynamic docking" non-charging targets via `SimpleNonChargingDock`. [FACT] [R07-S17]
- Forklift-AMR safety requirements: out of scope here, see R08. ISO 3691-4 excludes towed trailers from its requirements [R07-S28], so tugger/cart safety needs separate treatment in R08.

### 2.5 Facility mapping: graph and roadmap representations

| Representation | What it holds | Key semantics | Source |
|---|---|---|---|
| VDA 5050 order graph | Nodes and edges sent per order; full graph and per-robot restrictions stay in fleet control; `released` flag partitions "base" and "horizon"; `sequenceId` shared by nodes and edges. | Robot must not traverse unreleased elements; stops at the last released node (decision point); base cannot be changed. | [FACT] [R07-S01] |
| VDMA LIF 1.0.0 (March 2024) | JSON layout exchange from a vehicle integrator to a third-party fleet controller: nodes, edges, stations, per-vehicle-type node and edge properties, `loadRestriction` (loaded/unloaded allowed, allowed load-set names), actions with `requirementType` REQUIRED/CONDITIONAL/OPTIONAL, NURBS trajectories. | Does not describe route planning or traffic logic; one integrator per file; assumes VDA 5050 factsheet accompanies. | [FACT] [R07-S43][R07-S44] |
| Open-RMF navigation graph (traffic editor `.building.yaml`) | Per-fleet graph (nine graphs by default) of waypoints and lanes; vertex flags `is_holding_point`, `is_parking_spot`, `is_passthrough_point`, `is_charger`, `dock_name`, pickup/dropoff handler names; lane flags `bidirectional`, `orientation`; doors, lifts. | Lanes assumed effectively straight; pixel-origin editor frame with transform to robot map required. | [FACT] [R07-S08] |
| Open-RMF limitations (maintainer, 2026) | No curved lanes in the current-generation traffic system; a "next generation" traffic system is planned; SLAM maps can contain regional distortion that a linear transform does not correct, with no committed resources. | | [FACT] [R07-S12] (discourse post by a core maintainer) |
| Nav2 Route Server | Graph (GeoJSON default loader) used for routing instead of free-space planning; edge scorers (distance, time, penalty, semantic, dynamic edges via service to close or reprice edges), route operations on node/edge events (speed limits, collision monitor, rerouting, trigger external services such as doors/elevators). Docs reference tooling for LIF-based graph generation. | The dynamic-edges service is described as usable to close or reprice edges, e.g. when other robots occupy them; I read no multi-robot reservation semantics in the page. | [FACT] [R07-S18] |

**Observation.** Four incompatible graph models are in play (VDA node/edge-with-actions, LIF layout, RMF waypoints/lanes, Nav2 GeoJSON). None encodes physical aisle widths, rack geometry or floor flatness as first-class traffic constraints; VDA 5050 edges carry `maximumMobileRobotHeight` and `minimumLoadHandlingDeviceHeight` (renamed in v3) and a corridor attribute. [FACT] [R07-S01][R07-S03] [REC] Valtoryn needs one internal layout model with exporters (see §4).

### 2.6 Task allocation

**Taxonomies.**
- Gerkey and Matarić (2004) classify multi-robot task allocation (MRTA) along three axes: single-task vs multi-task robots (ST/MT), single-robot vs multi-robot tasks (SR/MR), instantaneous vs time-extended assignment (IA/TA). ST-SR-IA is an instance of the Optimal Assignment Problem, solvable centrally by the Hungarian method in O(mn²) or by distributed auction; ST-SR-TA is a strongly NP-hard scheduling problem. The paper assumes tasks are independent and ordering constraints are out of scope, and it encodes "robot cannot do task" as utility zero. [FACT] [R07-S19]
- Korsah, Stentz and Dias (2013), iTax: abstract states the earlier taxonomy handles independent tasks and does not cover interrelated utilities and constraints; iTax adds these and maps problem classes to operations-research models. Only the abstract was inspected; I do not describe iTax category names. [FACT] [R07-S20]
- Market-based coordination: robots act as self-interested agents trading tasks in a virtual economy; claimed benefits flexibility, robustness, scalability (survey abstract). [FACT] [R07-S21]

**Warehouse relevance.** A pick-then-drop transport task is two interrelated sub-tasks with precedence and a shared load; charging is a resource-constrained interrupt. That is outside Gerkey's independent-task assumption and inside iTax's motivation. [EST] (my mapping from the abstracts; not a claim made by the papers).

**Open-RMF dispatcher.** Since release 21.04 tasks are awarded by bidding: the dispatcher node broadcasts `BidNotice`, fleet adapters answer with `BidProposal` containing a cost computed by `rmf_task` `TaskPlanner`, then a `DispatchRequest` names the winner; evaluation criteria include fastest to finish and lowest cost. Battery recharge tasks are injected by the planner. The `TaskPlanner` plans among robots of **one fleet that share physical and kinematic traits**; heterogeneity is handled by multiple fleets. [FACT] [R07-S05][R07-S10]

**Task categories and capability in Open-RMF.** Task V2 categories are `clean`, `delivery`, `patrol`, `compose`; a `delivery` task has pickup/dropoff with a handler and SKU payload list (not pallet types). A fleet opts in per category through `FleetUpdateHandle::consider_delivery_requests`, `consider_cleaning_requests`, `consider_patrol_requests`, `consider_composed_requests`, `consider_zone_requests`, and `add_performable_action(category, consider)`; delivery and cleaning are off by default, patrol and compose on. Callbacks receive the task description and accept or reject (with error messages). `add_robot` takes a footprint profile which "should account for the largest possible payload". [FACT] [R07-S06][R07-S09] I found capability filtering at **fleet** level in the API header; whether per-robot filtering exists elsewhere in the stack is [UNRESOLVED] (resolve by reading `rmf_fleet_adapter` implementation and the task API server).

**Failure and re-allocation.** Open-RMF has a fleet-level `reassign_dispatched_tasks`, a commissioning feature that stops a robot taking new tasks and reassigns pending tasks within the fleet, but tasks already started cannot be transferred. [FACT] [R07-S09][R07-S11]

### 2.7 Multi-robot coordination, traffic management, deadlock and livelock

**MAPF background.**
- MAPF: paths for several agents from distinct starts to goals without collisions; NP-hard to solve optimally. [FACT] [R07-S23]
- CBS (Sharon, Stern, Felner, Sturtevant): two-level algorithm, a high-level search over a tree of conflicts and low-level single-agent searches; optimal; reported up to an order of magnitude speed-up over earlier optimal solvers (AAAI 2012 abstract; the 2015 journal version was not accessible). [FACT] [R07-S22]
- MAPF papers make differing assumptions (e.g. whether agents may traverse the same road at the same time) and objectives; Stern et al. propose unifying terminology and benchmarks. [FACT] [R07-S25]
- Lifelong MAPF, RHCR (Li et al., AAAI 2021): decompose into windowed MAPF instances resolving conflicts only inside a bounded horizon and replanning periodically; produces plans for up to 1,000 agents in simulated warehouse instances. It assumes drive units execute plans perfectly and points to Hönig et al. execution frameworks for kinematic realism; a too-small horizon can create deadlocks, mitigated by a potential-function check that enlarges the horizon until enough agents make progress; the authors note the mechanism remains incomplete because a minority agent can be starved (they choose throughput over completeness). [FACT] [R07-S23][R07-S24]
- Prioritised planning (Čáp et al.): widely used, in general incomplete; a revised version provably solves a characterised class of instances and an asynchronous decentralised variant exists. [FACT] [R07-S26]
- Review of autonomous forklifts: centralised coordination can be globally better but suffers single-point failure and poor scaling; decentralised "private zone" methods give O(KN) cost and deadlock avoidance through conservative space allocation, reducing throughput in dense traffic. [FACT] [R07-S27], secondary.

**Open-RMF traffic.** Fleets report itineraries to a centralised traffic schedule database; when the schedule detects a conflict it notifies the participants and a negotiation starts: each fleet submits preferred itineraries and alternatives, and a third-party "judge" selects among proposals (a judge can always favour an emergency task). Fleet adapter control categories: **Full Control** (live status plus control of paths, replaceable at any time), **Traffic Light** (pause/resume only), **Read Only** (status only; at most one such fleet per shared space), **No Interface** (not compatible; expected to deadlock). Mutex groups (presented in April 2024 as a recent feature) let a graph element group be exclusive to one robot at a time "regardless of whether the traffic conflict system believes there is room", intended for areas where conflict prevention cannot anticipate deadlocks; manual mutex release and release on starting to charge appear in the Jazzy changelog. `is_holding_point` marks waypoints where a robot may wait indefinitely. [FACT] [R07-S04][R07-S08][R07-S11][R07-S14]

**VDA 5050 traffic semantics.** The specification excludes traffic-management logic (routing, prioritisation, congestion handling, deadlock resolution) from its scope, yet lists deadlock detection and resolution, traffic control with buffer routes and waiting positions, and communication-error handling among minimum fleet-control functions. Mechanisms it does provide: base/horizon release; zones (`BLOCKED`, `RELEASE`, `COORDINATED_REPLANNING`, `SPEED_LIMIT`, `PRIORITY`, `PENALTY`, `DIRECTED`, `BIDIRECTED`, `ACTION`, `LINE_GUIDED`); a generic request/response channel where a robot requests, fleet control answers GRANTED/QUEUED/REJECTED/REVOKED with an optional `leaseExpiry`, and a robot that gets no timely response must behave as though not granted; freely navigating robots publish `intermediatePath` (polyline with ETAs) and `plannedPath` (NURBS) in state. [FACT] [R07-S01]

**Contested characterisation.** A 2021 Open-RMF maintainer post (about VDA 5050 before v2.1/v3.0) described VDA 5050 free-navigation vehicles as RMF "Read Only", generic AGVs as "Traffic Light", and said VDA 5050 had no "Full Control" equivalent. [FACT] [R07-S13] This is dated: v3.0.0 added planned-path sharing, zones with leases and corridors, and releases are the mechanism by which the fleet limits movement. Whether v3.0.0 is equivalent to RMF "Full Control" is [UNRESOLVED]; the base cannot be rerouted once sent, which is weaker than RMF's "replace the path at any time". [FACT] [R07-S01]

**Deadlock and livelock: what the sources provide.**

| Mechanism | Prevents | Source |
|---|---|---|
| Release-based extension of the base only when resources are free | Entering contested edges without permission | [R07-S01] |
| Exclusive zones with lease and loss behaviour (`RELEASE`, `releaseLossBehavior`) | Two robots in a pinch point; stale permissions | [R07-S01] |
| Mutex groups on graph elements | Deadlocks the schedule cannot foresee | [R07-S11] |
| Holding points / parking spots | Robots waiting in corridors | [R07-S08] |
| Negotiation with a judge and priority | Conflicting itineraries | [R07-S04] |
| Progress potential function enlarging planning horizon | Deadlock from short horizon | [R07-S23] |
| Revised prioritised planning | Instances where classic prioritised planning fails | [R07-S26] |
| Conservative private zones | Deadlock at throughput cost | [R07-S27] |

Livelock proper (agents moving but making no progress) is not named or analysed in the sources I read; the closest is the starvation case described by Li et al. [R07-S23]. Dedicated sources on livelock in physical AGV fleets: [UNRESOLVED].

### 2.8 Heterogeneous fleets: how capabilities and load types are expressed, and the gaps

**What VDA 5050 v3.0.0 can express (factsheet and actions).**
- `typeSpecification`: kinematics (`DIFFERENTIAL`, `OMNIDIRECTIONAL`, `THREE_WHEEL`, extensible), class (`FORKLIFT`, `CONVEYOR`, `TUGGER`, `CARRIER`, extensible), `maximumLoadMass`, localisation types, navigation types (`PHYSICAL_LINE_GUIDED`, `VIRTUAL_LINE_GUIDED`, `FREELY_NAVIGATING`), `supportedZones`.
- `physicalParameters`: min/max speed, angular speed, acceleration and deceleration at maximum load, min/max height, width, length.
- `protocolFeatures`: supported optional parameters; `mobileRobotActions` with action type, allowed scopes (INSTANT/NODE/EDGE/ZONE), typed parameters, blocking types, `pauseAllowed`, `cancelAllowed`.
- `loadSpecification`: `loadPositions` (load handling devices) and `loadSets` (name, `loadType` such as EPAL or XLT1200, bounding box and dimensions, max weight, handling height/depth/tilt ranges, max speed/acceleration/deceleration per load, pick and drop times).
- `mobileRobotGeometry`: wheels, 2D/3D envelopes, and safety-field envelopes.
- Edge-level: LIF `loadRestriction` (loaded/unloaded, allowed load-set names) per vehicle type; order edges carry height limits.
[FACT] [R07-S01][R07-S43]

**Gaps (each is a design obligation for a capability model).**

| Needed for correct dispatch | Present in standards? | Evidence |
|---|---|---|
| Controlled vocabulary for load carrier and station types | No. `loadType`, `stationType` are free strings; the spec's own examples use `EPAL`, `XLT1200` and `pallet_eu` for the same concept family. | [FACT] [R07-S01] |
| Station-side requirements (fork depth, rack height, conveyor side, entry direction) matched to robot capability | Only as optional action parameters (`height`, `depth`, `side`) and factsheet handling ranges; no formal "station requires X" declaration. | [FACT] [R07-S01] |
| Conditional limits (payload vs incline, speed vs load vs braking) | Partial: per-load-set speed and acceleration limits; no incline, floor, or pallet-grade conditions as in MiR datasheets. | [FACT] [R07-S01][R07-S33][R07-S35] |
| Runtime capability state (fork fault, attachment missing, battery too low for task) | Indirectly via errors, operating mode, and battery thresholds; no capability-state message. | [FACT] [R07-S01] |
| Per-robot vs per-type capability | Factsheet is per robot (manufacturer + serial) and "type series"; instance-specific load sets are filled at integration. | [FACT] [R07-S01] |
| Towed-trailer geometry and cart height range | Class `TUGGER` exists; hitch and cart parameters are manufacturer-defined actions. | [FACT] [R07-S01]; MiR gripping height 80–350 mm [R07-S35] |
| Task-level requirements | VDA 5050 has orders (routes plus actions), not tasks. Open-RMF has task categories but fleet-level acceptance. | [FACT] [R07-S01][R07-S09] |
| Environmental suitability (aisle width, floor flatness, lighting, undetectable materials) | Only footprint/geometry and corridor attributes. Datasheets state these as prose and tables. | [FACT] [R07-S33] |

**MassRobotics interoperability standard** (v1.0, May 2021): lets robots report location, destination, identifier, manufacturer/model/dimensions, operational state, speed and direction; deliberately not task management, fleet management, navigation, safety, power management or shared chargers; compliance is voluntary; a v2 mission API was under discussion in 2022. Material is a vendor-authored explainer on the MassRobotics site plus the repository description; the JSON schema itself was not opened. It is a visibility feed and does not address capabilities beyond state. [FACT] [R07-S41][R07-S42]

### 2.9 External system integration

- **Roles (weak sources).** A vendor article describes WMS (inventory and warehouse processes: receiving, put-away, fulfilment, shipping), WCS (directs automated material-handling equipment including AGVs) and WES (orchestrates automation- and human-driven tasks, sitting between or replacing parts of WMS/WCS). Vendor definitions vary, and I did not find a neutral standard defining these boundaries. [FACT] [R07-S45], weak. MES and ERP role definitions: [UNRESOLVED] (no source read).
- **No standard northbound interface.** VDA 5050 explicitly excludes interfaces to peripheral equipment, infrastructure and external IT systems. MassRobotics excludes task management. [FACT] [R07-S01][R07-S41]
- **Open-RMF northbound.** Tasks are submitted as JSON `ApiRequest` messages on `/task_api_requests` (unique `request_id`), with `robot_task_request` (named robot) or `dispatch_task_request` (best fleet); cancel and skip-phase requests exist. Southbound integration is through "fleet adapters" in C++/Python, including EasyFullControl with user callbacks (`navigate`, `stop`, `execute_action`, position, battery) over REST or any protocol. [FACT] [R07-S06][R07-S07]
- **Open-RMF with VDA 5050.** I found an experimental adapter repository and a 2026 community thread where an integrator speaks VDA 5050 over MQTT and migrates from waypoint-by-waypoint commanding to whole-path commands to give the robot trajectory context; the repository and thread are community material, not a maintained official bridge. The repository itself was not opened. [FACT] [R07-S12]; official bridge [UNRESOLVED].
- **ID and message mapping issues (from the specs).** VDA 5050 serial numbers allow only `A–Z a–z 0–9 _ . : -`; topic levels must avoid `/`, `+`, `#`, `$`; the factsheet can declare `idNumericalOnly`, maximum ID length, maximum nodes/edges/actions per order and message size; timestamps are ISO 8601 UTC with millisecond precision. Open-RMF requires named waypoints to use them as task destinations, and tasks use `request_id`. A WMS location code therefore needs a lossless mapping to a graph node, a station name, and a robot-acceptable ID. [FACT] [R07-S01][R07-S12][R07-S06]
- **OPC UA.** OPC 40010-1 "OPC UA for Robotics – Vertical Integration" is at version 1.02 (2025-09-08) on the OPC Foundation site. I did not read its content; whether it covers mobile-fleet orders is [UNRESOLVED]. [FACT] [R07-S49] (existence/version only)
- **Layout hand-over.** VDMA LIF exists precisely because VDA 5050 does not make participants interpret layouts the same way; the VDMA article states it separates layout definition from master-control tasks. [FACT] [R07-S44]

### 2.10 Order lifecycle, idempotency, partitions and fleet-level failure handling

**VDA 5050 order lifecycle and rules (v3.0.0).**
- An order has `orderId` (string) and `orderUpdateId` (uint32, starts at 0). Updates extend the horizon; the first node of an update must be the last base node already sent (the stitching node), and the decision point's contents must be resent unchanged. [FACT] [R07-S01]
- A new order is accepted only when the robot is idle (empty `nodeStates` and `edgeStates`, all actions FINISHED or FAILED). Updates are accepted while running. [FACT] [R07-S01]
- Duplicate handling: same `orderId` and `orderUpdateId` with identical content is ignored; different content raises `SAME_ORDER_UPDATE_ID`; a lower id raises `OUTDATED_ORDER_UPDATE`; a different `orderId` while one is active raises `OTHER_ORDER_ACTIVE`; unsupported action raises `INVALID_ORDER_ACTION`; unreachable node raises `NO_ROUTE_TO_TARGET`; unknown map raises `UNKNOWN_MAP_ID`. Rejection errors persist in state until a new order is accepted. [FACT] [R07-S01]
- `cancelOrder` is best-effort and unreliable over the network; a cancelled order cannot be updated; `orderId` and `orderUpdateId` are kept, so retry needs a new `orderId`. Scheduled actions become FAILED; actions that cannot be cancelled run to completion. [FACT] [R07-S01]
- Action states: INITIALIZING, RUNNING, PAUSED, FINISHED, FAILED, RETRIABLE; a `retry`/`skipRetry` pair exists. Predefined idempotency: `pick`/`drop` are marked **not** idempotent; every other predefined action in the table (including `startCharging`, `stopCharging`, `cancelOrder`) is marked idempotent. [FACT] [R07-S01]
- Operating modes: AUTOMATIC, SEMIAUTOMATIC, INTERVENED, MANUAL, STARTUP, SERVICE, TEACH_IN; MANUAL, SERVICE and TEACH_IN clear the order (SERVICE and TEACH_IN always blank `lastNodeId`; MANUAL only if the order cannot be continued); fleet control may send orders in INTERVENED mode but only `cancelOrder` as instant action. [FACT] [R07-S01]

**Transport and partition behaviour.** MQTT 3.1.1 minimum with JSON; QoS 0 for `order`, `instantActions`, `state`, `factsheet`, `zoneSet`, `responses`, `visualization`, QoS 1 for `connection`. Each robot sets a last-will `CONNECTION_BROKEN` on the retained `connection` topic. On disconnect the robot keeps order information and completes the order up to the last released node. Because delivery is best effort, fleet control must infer receipt from the robot's `state` echo and resend. Protocol security is left to broker configuration and cybersecurity measures are listed as out of scope, although an `updateCertificate` action exists to rotate TLS certificates on the robot. A request with no timely response is treated as not granted. [FACT] [R07-S01]

**Fleet-level failure handling in Open-RMF.** Core RMF documents a centralised traffic schedule; a 2021 maintainer post described hot-standby schedule nodes as close to done, with task-dispatch failover still to be designed; I could not confirm current status. [FACT] [R07-S04][R07-S13]; current failover [UNRESOLVED].

**Version status.** VDA 5050 3.0.0 was released on 2026-03-18 (UTC; GitHub release metadata, cross-checked via the GitHub API on 2026-11-07, the release page may display 2026-03-19 in other time zones), with major changes (freely navigating robots, zones, planned-path sharing, reworked operating modes, action states and breaking parameter renames) and a topic prefix version change (`v3`). Prior releases are 2.1.0 and 2.0.0; the repository milestones list V3.0.1 (typos), V3.1.0 (backward compatible), and V4.0.0 "currently not planned". If the markdown and VDA PDF differ, the PDF on the VDA site is declared valid; I read the markdown. [FACT] [R07-S02][R07-S03][R07-S01]

---

## 3. Comparison and trade-off analysis

### 3.1 Fleet-side options

| Option | Strengths | Weaknesses / unknowns | Evidence |
|---|---|---|---|
| Adopt Open-RMF as the fleet layer | Open source, traffic schedule + negotiation + task bidding + lifts/doors; adapter model for third-party fleets; Apache-2.0 repositories. | ROS 2 coupled; per-fleet homogeneity assumption in task planner; straight-lane graph, no curves in current generation; map-distortion issue; capability expressed as fleet-level callbacks; documentation book partly old. | [R07-S04][R07-S05][R07-S09][R07-S10][R07-S12] |
| Native Valtoryn fleet manager + VDA 5050 southbound | Capability model and order lifecycle designed around Valtoryn needs; one external contract for third-party robots. | Must build traffic management (not specified by VDA 5050); v3 adoption in installed base unknown. | [R07-S01][R07-S03] |
| Hybrid: native planner for Valtoryn robots, RMF adapter for building infrastructure and other fleets | Reuses RMF door/lift integrations. | Two traffic authorities must not both own the same lanes; RMF "Read Only" limit of one such fleet. | [R07-S04] |

### 3.2 Allocation approaches

| Approach | Fits | Limit | Evidence |
|---|---|---|---|
| Centralised assignment (Hungarian) over capable robots | Independent single-robot tasks, instantaneous | Ignores precedence, routes, charging, congestion | [R07-S19] |
| Auction/bidding (Open-RMF style) | Heterogeneous fleets with per-fleet cost models; incremental task arrival | Cost is only as good as each bidder's planner; one-by-one award is not globally optimal | [R07-S05][R07-S21] |
| Time-extended scheduling | Task queues, precedence | Strongly NP-hard in general; needs heuristics | [R07-S19] |

### 3.3 Traffic approaches

| Approach | Strength | Weakness | Evidence |
|---|---|---|---|
| Release/reservation on a roadmap (VDA-style) | Predictable, robot-side simple, partition-safe stops | Needs conservative reservations; no rerouting of released base | [R07-S01] |
| Schedule + negotiation (RMF) | Handles multi-vendor | Needs live itineraries from every fleet | [R07-S04] |
| MAPF/lifelong replanning | Throughput at scale in simulation | Assumes near-perfect execution; deadlock/starvation caveats | [R07-S23] |
| Mutex/exclusive zones | Robust at pinch points | Throughput loss | [R07-S11][R07-S27] |

---

## 4. Implications and recommendations for Valtoryn (all [REC])

### 4.1 Capability-matching model for dispatch

**[REC] Principles.**
1. **Default deny.** A task is dispatchable to a robot only if every requirement is explicitly satisfied by declared capability. "Unknown" counts as not capable. (This matches Gerkey's utility-zero idea [R07-S19] but makes the rule a hard filter before any cost ranking.)
2. **Three layers.** (a) *Type capability profile* (static, per robot model/configuration; imported from or exportable to a VDA 5050 factsheet [R07-S01]); (b) *instance capability state* (installed attachment, calibration status, faults, battery, operating mode; dynamic); (c) *task requirement* (derived from task and from the stations it touches).
3. **Capabilities are predicates with conditions, not scalars.** Encode limits as functions: payload(incline, speed), handling(load class, height, entry side), speed(load). The MiR Hook and MiR1200 sheets show why [R07-S33][R07-S35].
4. **Two-stage dispatch.** Stage 1 hard filter on capability and station compatibility; stage 2 cost ranking (travel time from route planner, queue, battery, congestion). Allocation algorithm stays pluggable (greedy/auction/assignment) behind this interface.
5. **Capability atoms** (proposed minimum set): kinematics and loaded/unloaded footprint; load mass; load carrier classes (controlled vocabulary mapped to VDA `loadType` strings, with explicit alias table, because VDA does not control the vocabulary); handling mode per station interface (floor, rack at height range, conveyor active/passive and side, tow-hitch with cart gripping-height range); docking/charging interface types; environment envelope (min aisle, floor tilt, lighting/surface exclusions); supported protocol features (VDA zones, planned path, specific actions).
6. **Task requirements derive from stations.** Each station/dock in the facility model declares required interface class, geometry limits and allowed load classes; the matcher intersects robot capability with station requirements for both pick and drop, plus every edge on the route (LIF-style `loadRestriction` per vehicle type and edge [R07-S43]).
7. **Fail closed on edge cases.** If no robot is capable, the task goes to a visible "unassignable" state with the failing predicate named; it must never be silently downgraded to a task the robot can do.

**[REC] Mapping to existing standards.** Import: factsheet `mobileRobotActions`, `loadSets`, `loadPositions`, `mobileRobotClass`, kinematics, `supportedZones`; LIF `loadRestriction`. Export: same fields from Valtoryn robots. Valtoryn extensions (namespaced, optional) cover the gaps in §2.8: conditional limits, station requirements, environment envelope, instance capability state. Open-RMF mapping: one Valtoryn *capability-homogeneous group* per RMF fleet if RMF is used, because the RMF planner assumes shared traits [R07-S10].

### 4.2 Fleet manager versus on-robot autonomy

| Concern | Fleet manager owns | Robot owns |
|---|---|---|
| Task intake, allocation, queue, priorities | Yes | No |
| Route-level reservations (lanes, zones, stations, chargers, lifts/doors) | Yes (release extends base only after reservation) | Obeys releases; requests when entering interactive zones |
| Local path, obstacle avoidance, in-corridor deviation | Provides corridor bounds | Yes; stops if it leaves the corridor (VDA behaviour [R07-S01]) |
| Localisation | Receives pose/confidence | Yes |
| Docking terminal phase, pallet pick/drop execution, retry of the physical operation | Authorises start, observes result | Yes |
| Safety functions (protective stop, speed limiting) | No dependency | Yes — must not depend on fleet link (R08) |
| Charging decision | Schedules by thresholds and demand | Enforces charge protection |
| Behaviour on link loss | Treats robot as still executing released base | Completes up to last released node, then holds (VDA behaviour [R07-S01]) |
| Order/update validity checks and rejection errors | Retries sensibly | Validates per the acceptance procedure |
| Deadlock detection and resolution | Yes (centralised wait-for view) | Reports blocked state, replans locally within corridor |

**[REC]** Keep the robot able to complete an accepted base safely with no network, keep reservations lease-based with expiry on both sides, and keep every safety function local.

### 4.3 Interface choices and VDA 5050 conformance

**What conformance would actually require (from the v3.0.0 text).**
- There is **no defined conformance level, profile or certification scheme** in the specification; use is declared optional and non-binding, and it disclaims safety, traffic logic, cybersecurity and commissioning. My search of the text for conformance/certification terms found none apart from interoperability wording and TLS certificate handling. [FACT] [R07-S01] A vendor press release describes "certification" as pairing with specific VDA 5050-compliant software vendors, not a neutral test programme. [FACT] [R07-S46] A neutral conformance test suite: [UNRESOLVED].
- Mandatory topics: `order`, `instantActions`, `state`, `connection`, `factsheet`. Optional: `visualization`, `zoneSet`, `responses`. Mandatory behaviours for every robot: support `cancelOrder`, `startPause`, `stopPause`; the order acceptance flow; the predefined error types and reporting durations; idle definition; operating-mode table; last-will and retained connection messages; factsheet publication; planned-path sharing if freely navigating (v3 text says "shall"). [FACT] [R07-S01]
- Because "mobile robot manufacturer shall use predefined actions if capabilities map to them" and may add custom actions, interoperability for loads rests on bilateral agreement of action parameters. [FACT] [R07-S01]

**[REC] Proposed target, evaluated.**
1. **Do not make VDA 5050 the internal architecture.** It describes a robot–fleet wire contract, not tasks, capabilities or traffic.
2. **Build a separate VDA 5050 gateway component** with two roles: *robot-side* (Valtoryn robot appears to a third-party fleet controller) and *fleet-side* (Valtoryn fleet manager commands third-party robots). Both are optional modules.
3. **Define a Valtoryn VDA 5050 profile in tiers and publish it as a self-declared profile**, with automated checks, since no official programme exists:
   - *Tier V0 (protocol core)*: schema-valid messages; topics and QoS; connection/last-will; order acceptance flow; cancel/pause; idle; errors; factsheet.
   - *Tier V1 (warehouse actions)*: `pick`, `drop`, `startCharging`, `stopCharging`, `finePositioning`, `detectObject`, `waitForTrigger`/`trigger`, factsheet load sets.
   - *Tier V2 (free navigation)*: `intermediatePath`/`plannedPath`, corridors, zones with request/response and leases.
   The honest cost: V0 is a bounded implementation effort; V1 requires the Valtoryn load/station vocabulary mapping (§4.1); V2 depends on Valtoryn's own planned-path output and a fleet traffic manager. Estimates of effort are not given because no source supports them.
4. **Version policy.** Target v3.0.0 first (current, released 2026-03-18 UTC [R07-S03]); decide on v2.1 support for fleet-side adapters only when a concrete third-party robot demands it; the installed base's version distribution is [UNRESOLVED]. v3 changed names and semantics (breaking) [R07-S03], so a dual-version gateway is real work.
5. **Layout.** One internal facility model; exporters to LIF (for VDA ecosystems), Open-RMF navigation graph, Nav2 route GeoJSON. This avoids maintaining four hand-drawn graphs and handles the coordinate-transform issue in one place (SLAM distortion remains a risk [R07-S12]).
6. **Open-RMF.** Treat as an optional integration target and a reference for traffic-schedule design; do not depend on it for the core until the capability and curved-lane limits are resolved with its maintainers.
7. **Northbound (WMS/WES).** Define a small Valtoryn task API with client-supplied idempotency keys, explicit task lifecycle events, and mappings from WMS location codes to facility nodes/stations. Do not claim a standard for it (none found). MassRobotics telemetry is optional visibility feed only [R07-S41].
8. **Docking.** Use the Nav2 docking server (plugin per dock type) as the starting design for charging and non-charging docks, with docking executed on the robot (odometry-frame final approach) and the fleet seeing only dock reservation and result. Charge contact type (contact vs inductive) must be a dock-plugin and capability attribute, not a hard-coded assumption.

### 4.4 Order and task lifecycle, idempotency, failure handling

**[REC] Task lifecycle** (distinct from VDA orders): `RECEIVED → VALIDATED → ASSIGNABLE/UNASSIGNABLE → ASSIGNED → DISPATCHED (orders issued) → EXECUTING → COMPLETING → COMPLETED`, with `FAILED`, `CANCELLING`, `CANCELLED`, `SUSPENDED`. A task maps to one or more VDA orders; chaining orders requires the fleet manager to hold the task queue because VDA robots take a new order only when idle [R07-S01].

**[REC] Idempotency rules.**
- Every northbound request carries a client idempotency key; replays return the original result.
- Every VDA order uses a fresh `orderId`; resending an update with the same `orderUpdateId` and identical content is safe by spec; never reuse an `orderId` after cancel.
- Non-idempotent physical actions (`pick`, `drop`) are never blindly resent. After an ambiguous outcome (link loss, timeout), query `state` (`loads`, `actionStates`) and, if still ambiguous, mark the task `NEEDS_VERIFICATION` and require a sensor check or operator confirmation before retry.

**[REC] Failure matrix (design obligations, none implemented).**

| Failure | Expected handling |
|---|---|
| Link loss (robot) | Robot finishes released base, holds; fleet keeps reservations until lease expiry plus margin; then marks the robot unreachable, reroutes others around it, escalates |
| Broker failover | Retained `connection` state; robots reconnect with unchanged `headerId` semantics checked; fleet re-requests state (`stateRequest`) |
| Robot restarts mid-order | Treat as MANUAL/STARTUP-equivalent; order cleared; task becomes `NEEDS_VERIFICATION` |
| Pick failure | Retry policy via RETRIABLE/`retry`/`skipRetry`; bounded; escalate |
| Charger unavailable | Dynamic charger reassignment; do not strand low battery robots |
| Fleet manager failure | Robots complete base and hold; recovery reloads task state from durable store; leader election needed for HA (design not sourced) |
| Deadlock | Wait-for-graph detection; timeout; priority escalation; manual intervention path |
| Starvation | Aging priority so a minority flow cannot wait forever (cf. [R07-S23]) |

### 4.5 What must be validated physically versus in simulation

| Item | Simulation adequate? | Physical validation required |
|---|---|---|
| Allocation logic, capability matching, queueing | Yes (deterministic and randomised scenarios) | Only for cost-model calibration (real travel/handling times) |
| Traffic reservation logic, deadlock and starvation scenarios (incl. RHCR-style intersections) | Yes | Pinch points with real footprints and braking distances; brake distance depends on load [R07-S35] |
| VDA 5050 message flows, duplicates, loss, reorder, version skew | Yes (MQTT fault injection) | Against at least one third-party fleet controller or robot |
| Network partition behaviour | Logic yes | Wi-Fi dead zones, roaming latency, AP failure in the real building |
| Pallet detection and fork insertion | No | Real pallets: grade, damage, shrink-wrap, reflective floors, skew, lighting; acceptance criteria set from §2.4 reviewed thresholds, to be measured, not assumed |
| Docking and charging contact/inductive alignment | Sim for logic only | Success rate over long repeated trials, contact wear, dirt; accuracy numbers from this campaign |
| Tow-hitch coupling, cart variability, incline limits | No | Real carts across the cart population, slopes |
| Localisation vs graph transform; SLAM distortion | No | Survey-grade checks across the whole floor |
| Lift/door/elevator handshakes | Mock only | Real devices |
| Safety functions, human interaction | No | R08 programme |
| Throughput claims | Relative comparisons only | Measured on site; sim numbers must not be marketed as results |

---

## 5. Limitations of this research

- VDA 5050 was read as the GitHub markdown for v3.0.0; the repository states the VDA PDF is authoritative on conflict. JSON schemas were not opened; message-level details come from the markdown tables.
- iTax, CBS (journal), Dias et al. (full text) and all ISO/ANSI standards were read at abstract/catalogue level only.
- Vendor datasheets give maxima, with undated web pages disagreeing with dated PDFs in one case. No independent measurements were obtained. Docking accuracy and charging reliability of specific stations are not established.
- The Open-RMF book includes pre-2024 content; the 2021 maintainer comparison with VDA 5050 predates v2.1 and v3.0.
- WMS/WES/WCS definitions come from a vendor article; MES/ERP not covered by a source.
- No hardware or simulation experiments were run by me; all numbers are from sources or shown calculations.
- The ISO 6780 dimension table, the OTTO 1500 numeric table and ISO TC 299 WG 10 outputs were not obtainable.

## 6. Unresolved questions

1. Does any neutral VDA 5050 conformance test suite or certification programme exist? Resolve with VDMA/VDA contacts and the repository's discussions.
2. Which VDA 5050 versions do shipping robots and fleet controllers actually speak in 2026 (v2.0/2.1/3.0)? Resolve by vendor survey.
3. Does Open-RMF support per-robot capability filtering inside a fleet, and what is the status of its failover and next-generation traffic system? Resolve by reading `rmf_fleet_adapter` and asking maintainers.
4. Is the Open-RMF "Full Control" level achievable over VDA 5050 v3.0 (planned path, leases, base/horizon)? Resolve by prototype or maintainer statement.
5. Documented docking accuracy for contact charging stations, and comparative contact vs inductive reliability. Resolve with charger datasheets plus a test campaign.
6. ISO 6780 dimensions and tolerances. Resolve by purchasing the standard.
7. Conveyor-top AMR datasheet figures and transfer-height tolerances.
8. What ISO/TC 299 WG 10 is producing for mobile-robot interoperability.
9. Livelock-specific literature for physical fleets.
10. OPC UA robotics specification coverage of mobile-fleet orders.
11. Real-world cost of fork-and-pallet retry strategies (pick failure rates); no source read.

---

## 7. Sources

| ID | Title | Organization / author | URL | Published / revision date | Accessed | What it supports |
|---|---|---|---|---|---|---|
| R07-S01 | VDA 5050 – Interface for the Communication between Mobile Robots and a Fleet Control, v3.0.0 (VDA5050_EN.md) | VDA / VDMA / KIT-IFL | https://raw.githubusercontent.com/VDA5050/VDA5050/main/VDA5050_EN.md | v3.0.0, released 2026-03-18 UTC (per R07-S03) | 2026-11-07 | Order/update rules, actions, factsheet, zones, requests, errors, operating modes, QoS, scope exclusions |
| R07-S02 | VDA5050/VDA5050 repository README | KIT-IFL / VDA / VDMA | https://github.com/VDA5050/VDA5050 | n/a (not stated on page) | 2026-11-07 | Current version, PDF authority, milestone policy |
| R07-S03 | VDA5050 Releases (3.0.0, 2.1.0, 2.0.0) | KIT-IFL | https://github.com/VDA5050/VDA5050/releases | 3.0.0 released 2026-03-18 UTC | 2026-11-07 | Release dates, v3 changes, breaking renames |
| R07-S04 | RMF Core Overview | Open Robotics / OSRF (ros2multirobotbook) | https://osrf.github.io/ros2multirobotbook/rmf-core.html | n/a (not stated on page) | 2026-11-07 | Traffic schedule, negotiation, fleet adapter categories |
| R07-S05 | Tasks in RMF | Open Robotics / OSRF | https://osrf.github.io/ros2multirobotbook/task.html | n/a (not stated on page) | 2026-11-07 | Bidding dispatcher, charge task injection |
| R07-S06 | Supporting a new Task in RMF | Open Robotics / OSRF | https://osrf.github.io/ros2multirobotbook/task_new.html | n/a (not stated on page) | 2026-11-07 | Task V2 categories, task API requests |
| R07-S07 | Mobile Robot Fleets (Integration) | Open Robotics / OSRF | https://osrf.github.io/ros2multirobotbook/integration_fleets.html | n/a (not stated on page) | 2026-11-07 | Fleet adapter APIs, EasyFullControl |
| R07-S08 | Traffic Editor | Open Robotics / OSRF | https://osrf.github.io/ros2multirobotbook/traffic-editor.html | n/a (not stated on page) | 2026-11-07 | Navigation graph attributes, coordinate frames |
| R07-S09 | rmf_fleet_adapter FleetUpdateHandle.hpp | open-rmf / rmf_ros2 | https://raw.githubusercontent.com/open-rmf/rmf_ros2/main/rmf_fleet_adapter/include/rmf_fleet_adapter/agv/FleetUpdateHandle.hpp | n/a (not stated on page) | 2026-11-07 | Fleet-level capability callbacks, task planner params, reassign |
| R07-S10 | rmf_task README | open-rmf | https://github.com/open-rmf/rmf_task | n/a (not stated on page) | 2026-11-07 | TaskPlanner semantics (one fleet shares traits) |
| R07-S11 | Interoperability Interest Group April 4, 2024: Recent feature developments in Open-RMF | Open Robotics discourse | https://discourse.openrobotics.org/t/interoperability-interest-group-april-4-2024-recent-feature-developments-in-open-rmf/36909 | 2024-03-29 | 2026-11-07 | Mutex groups, dynamic charging, commissioning |
| R07-S12 | Open-RMF Questions from a real integration with a DIFF robot + VDA5050 | Open Robotics discourse (community + core maintainer reply) | https://discourse.openrobotics.org/t/open-rmf-questions-from-a-real-integration-with-a-diff-robot-vda5050/54057 | 2026-04 (per search listing; exact date not on fetched text) | 2026-11-07 | No curved lanes, next-gen traffic plan, SLAM distortion, VDA 5050 experiences |
| R07-S13 | Vda5050 (#23) – Open-RMF General | Open Robotics discourse (maintainer post) | https://discourse.openrobotics.org/t/vda5050-23/44699 | 2021-04-02 (per search listing) | 2026-11-07 | 2021 RMF-vs-VDA characterisation; failover plans |
| R07-S14 | Releases · open-rmf/rmf (Open-RMF on Jazzy Jalisco) | open-rmf | https://github.com/open-rmf/rmf/releases | released "17 Jun" (year not shown on fetched text) | 2026-11-07 | Jazzy changelog items (mutex release, commissioning) |
| R07-S15 | Docking Server (Nav2 configuration guide, rolling) | Nav2 / ros-navigation | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/configuring_docking_server/ | n/a (not stated on page) | 2026-11-07 | Docking server behaviour, parameters and defaults |
| R07-S16 | Open Navigation's Nav2 Docking Framework (opennav_docking) | Open Navigation LLC | https://github.com/open-navigation/opennav_docking | n/a (not stated on page) | 2026-11-07 | Docking procedure, plugin API, migration into Nav2 |
| R07-S17 | Using Docking Server (Nav2 tutorial, Jazzy) | Nav2 / ros-navigation | https://docs.nav2.org/jazzy/tutorials/general_tutorials/using_docking/ | n/a (not stated on page) | 2026-11-07 | Non-charging pallet/conveyor docking, odom frame rationale, demo claim |
| R07-S18 | Route Server (Nav2 configuration guide, rolling) | Nav2 / ros-navigation | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/route_server/configuring_route_server/ | n/a (not stated on page) | 2026-11-07 | Graph routing, edge scorers, route operations |
| R07-S19 | A formal analysis and taxonomy of task allocation in multi-robot systems | B. P. Gerkey, M. J. Matarić; IJRR 23(9) | https://cse-robotics.engr.tamu.edu/dshell/cs689/papers/gerkey04formal.pdf | 2004-09 | 2026-11-07 | ST/MT, SR/MR, IA/TA taxonomy; assignment complexity |
| R07-S20 | A comprehensive taxonomy for multi-robot task allocation (iTax) – abstract page | G. A. Korsah, A. Stentz, M. B. Dias; CMU RI | https://publications.ri.cmu.edu/a-comprehensive-taxonomy-for-multi-robot-task-allocation | 2013-10 (IJRR 32(12)) | 2026-11-07 | iTax motivation (abstract only) |
| R07-S21 | Market-Based Multirobot Coordination: A Comprehensive Survey and Analysis – abstract page | Kalra, Dias, Zlot, Stentz; CMU-RI-TR-05-16 | https://publications.ri.cmu.edu/market-based-multirobot-coordination-a-comprehensive-survey-and-analysis | 2005-12 | 2026-11-07 | Market-based coordination overview (abstract only) |
| R07-S22 | Conflict-Based Search For Optimal Multi-Agent Path Finding | G. Sharon, R. Stern, A. Felner, N. Sturtevant; AAAI-12 | https://ojs.aaai.org/index.php/AAAI/article/view/8140 | Proceedings vol. 26 (2012); page lists online date 2021-09-20 | 2026-11-07 | CBS two-level algorithm (abstract; journal version not accessible) |
| R07-S23 | Lifelong Multi-Agent Path Finding in Large-Scale Warehouses (HTML v2) | J. Li, A. Tinka, S. Kiesel, J. Durham, T. K. S. Kumar, S. Koenig | https://arxiv.org/html/2005.07371v2 | revised 2021-03-12 | 2026-11-07 | RHCR, execution assumption, deadlock avoidance |
| R07-S24 | arXiv:2005.07371 abstract page | arXiv | https://arxiv.org/abs/2005.07371 | v2 2021-03-12; AAAI 2021 | 2026-11-07 | Publication data, 1,000-agent claim |
| R07-S25 | Multi-Agent Pathfinding: Definitions, Variants, and Benchmarks | R. Stern et al.; SoCS 2019 | https://arxiv.org/abs/1906.08291 | 2019-06-19 | 2026-11-07 | MAPF assumption variability |
| R07-S26 | Prioritized Planning Algorithms for Trajectory Coordination of Multiple Mobile Robots | M. Čáp, P. Novák, A. Kleiner, M. Selecký | https://arxiv.org/abs/1409.2399 | 2014-09-08 | 2026-11-07 | Prioritised planning incompleteness, revised variant |
| R07-S27 | Autonomous Forklifts for warehouse automation: A comprehensive review | A. D. Patil, S. Farzan; Robotics 15(2):30 | https://www.mdpi.com/2218-6581/15/2/30 | 2026 | 2026-11-07 | Pallet perception thresholds, coordination trade-offs, deployment scale (secondary review) |
| R07-S28 | ISO 3691-4:2023 | ISO | https://www.iso.org/standard/83545.html | 2023-06 | 2026-11-07 | Driverless truck scope, AGV/AMR naming, trailers excluded (catalogue only) |
| R07-S29 | ISO 3691-4:2020 (withdrawn) | ISO | https://www.iso.org/standard/70660.html | 2020-02 | 2026-11-07 | Superseded edition (catalogue only) |
| R07-S30 | ANSI/A3 R15.08-1-2020 (R2026): Industrial Mobile Robots Safety | ANSI Blog (A. Schirn) | https://blog.ansi.org/ansi/ansi-a3-r15-08-1-2020-r2026-mobile-robot-safety/ | 2026-09-10 | 2026-11-07 | R15.08 series parts and scope |
| R07-S31 | Revolutionizing Robotics: The Introduction of the R15.08 Safety Standard for IMRs | SICK North America | https://sickconnect.com/revolutionizing-robotics-the-introduction-of-the-r15-08-safety-standard-for-industrial-mobile-robots/ | 2024-03-11 | 2026-11-07 | AGV vs AMR wording in R15.08; IMR types A/B/C (secondary quote) |
| R07-S32 | The Evolution of AGVs and AMRs | MHI (author from Balyo) | https://www.mhi.org/blog/126101/the-evolution-of-agvs-and-amrs | 2025-04-08 | 2026-11-07 | Blurring AGV/AMR definitions (opinion, weak) |
| R07-S33 | MiR1200 Pallet Jack Specifications (PDF, mirrored) | Mobile Industrial Robots | https://jk.de/media/3d/g0/27/1739198074/42010140_MiR1200_Pallet_Jack_Specifications.pdf?ts=1739198074 | 2025-01-14 | 2026-11-07 | Pallet AMR payload, speed, pallet type, clearances, sensors |
| R07-S34 | MiR1200 Pallet Jack specifications (web) | Mobile Industrial Robots | https://mobile-industrial-robots.com/products/robots/mir1200-pallet-jack/specifications | n/a (not stated on page) | 2026-11-07 | Web specs, differing dimensions/weight |
| R07-S35 | MiR Hook 250 Specifications (PDF, mirrored) | Mobile Industrial Robots | https://shelley.com/wp-content/uploads/2024/07/MiR-Hook-250-Specifications-2.51.pdf | 2023-09-13 | 2026-11-07 | Cart towing payload vs incline, gripping height, braking table |
| R07-S36 | MiR250 Hook | Mobile Industrial Robots | https://mobile-industrial-robots.com/products/applications/mir250-hook | n/a (not stated on page) | 2026-11-07 | Max speed 2.0 m/s, 500 kg, AprilTag cart ID |
| R07-S37 | Seegrid Lift CR1 AMR | Seegrid | https://seegrid.com/autonomous-mobile-robots/lift-cr1-amr/ | 2024-02-12 (page metadata) | 2026-11-07 | Autonomous lift truck figures, VDA 5050 claim |
| R07-S38 | OTTO 1500 Autonomous Mobile Robot | OTTO by Rockwell Automation | https://ottomotors.com/1500/ | n/a (not stated on page) | 2026-11-07 | Heavy AMR, attachments, standards compliance list |
| R07-S39 | EPAL Euro Pallet (EPAL 1) | European Pallet Association (EPAL) | https://www.epal-pallets.org/eu-en/load-carriers/epal-euro-pallet | 2025-04-09 | 2026-11-07 | EUR pallet dimensions, load, exchange criteria |
| R07-S40 | ISO 6780:2003 | ISO | https://www.iso.org/standard/30524.html | 2003-12 (confirmed 2026) | 2026-11-07 | Flat pallet dimensions standard scope (catalogue only) |
| R07-S41 | What Is the MassRobotics AMR Interoperability Standard? | MassRobotics (author from BlueBotics) | https://www.massrobotics.org/what-is-the-massrobotics-amr-interoperability-standard/ | 2023-06-19 | 2026-11-07 | MassRobotics scope and exclusions (vendor-authored) |
| R07-S42 | MassRobotics AMR_Interop_Standard repository | MassRobotics | https://github.com/MassRobotics-AMR/AMR_Interop_Standard | n/a (not stated on page) | 2026-11-07 | Standard contents (schema, PDF, sample code) |
| R07-S43 | LIF – Layout Interchange Format v1.0.0 | VDMA | https://www.vdma.eu/documents/34570/3317035/FuI_Guideline_LIF_GB.pdf | 2024-03 | 2026-11-07 | Layout exchange, load restrictions, action requirement types |
| R07-S44 | Layout Interchange Format (news article) | VDMA | https://vdma.eu/en/viewer/-/v2article/render/89847487 | n/a (search listing 2025-04-04) | 2026-11-07 | Purpose of LIF alongside VDA 5050 |
| R07-S45 | WMS vs. WCS vs. WES: Warehouse Control & Execution Systems Explained | Made4net (vendor) | https://made4net.com/knowledge-center/wms-vs-wcs-vs-wex-warehouse-control-execution-system-explained/ | 2025-01-09 | 2026-11-07 | WMS/WCS/WES role descriptions (weak, vendor) |
| R07-S46 | OTTO adds VDA 5050 certifications to support mixed-fleet deployments | NAiSE / OTTO press release | https://naise.eu/otto-adds-vda-5050-certifications-to-support-mixed-fleet-deployments/ | 2026-04-09 | 2026-11-07 | Market practice of pairwise VDA 5050 "certification" (vendor PR, weak) |
| R07-S47 | Global Robotics Standards | A3 Robotics | https://www.automate.org/robotics/robotic-standards/global-robotic-standards | n/a (not stated on page) | 2026-11-07 | ISO/TC 299 WG list incl. WG 10, R15.08 subcommittee |
| R07-S48 | Wireless charging for AGV | Wiferion (vendor) | https://www.wiferion.com/en/applications/wireless-charging-agv-automated-guided-vehicle-systems/ | 2021-02-03 (page metadata) | 2026-11-07 | Inductive charging vendor figures (weak) |
| R07-S49 | OPC-40010-1 – OPC UA for Robotics Part 1: Vertical Integration | OPC Foundation | https://reference.opcfoundation.org/specs/OPC-40010-1 | 2025-09-08 (v1.02) | 2026-11-07 | Existence and version only |

### Sources that could not be inspected (not cited)

- Sharon et al., CBS journal version (Artificial Intelligence, ScienceDirect) — blocked automated reading.
- Korsah et al. 2013 full text (SAGE, Semantic Scholar, SciSpace) — blocked; only the CMU abstract page was read.
- Hönig et al. 2019, "Persistent and Robust Execution of MAPF Schedules in Warehouses" (IEEE) — fetch failed; known here only through the citation in R07-S23.
- Digani et al. 2015 (IEEE T-ASE, ADS page) — blocked.
- OTTO 1500 datasheet PDF (Rockwell Automation) — unreachable.
- Nav2 docs URLs guessed for a route-server page — 404; the correct page was found by search.
- MassRobotics `standard_interoperability` URL — 404; the correct repository was read.
