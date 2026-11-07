# Architecture decision records — Valtoryn platform

> **Status:** Proposed decisions (status = *proposed*, not implemented). Each ADR follows:
> context/requirements → alternatives → evidence → trade-offs → recommendation → risks → unresolved.
> Numbering continues across the project; these are the architecture-phase ADRs.

---

## ADR-001 — ROS 2 as the robotics middleware

**Status:** Proposed · **Date:** 2026-11-07

**Requirements.** Vendor-neutral platform; multiple chassis/locomotion; simulation=hardware parity; fleet
interoperability; long support horizon; active ecosystem.

**Alternatives.** ROS 2; ROS 1; custom middleware; Zenoh-only; micro-ROS-only.

**Evidence.** ROS 2 is Apache-2.0, federated, with lifecycle nodes, composition, pluginlib, ros2_control,
Nav2, SROS2 security, and the only open fleet ecosystem (Open-RMF) built on it [FACT R01-S06, R01-S13].
OTTO's public case study reports ROS 2 scaled where ROS 1 multi-master could not [FACT R01-S06].

**Trade-offs.** DDS complexity and Wi-Fi discovery issues are real [FACT R01-S06]; determinism is weaker than a
monolith (ROS authors state this). Mitigations: Discovery Server or Zenoh routers; RT path kept in ros2_control/MCU.

**Recommendation.** Adopt ROS 2. Do not build a parallel middleware.

**Risks.** Cross-distribution interop not guaranteed [FACT R01-S02]; third-party driver lag on new LTS.

**Unresolved.** Final distribution pin (see ADR-002).

---

## ADR-002 — ROS 2 distribution: Lyrical primary, Jazzy fallback

**Status:** Proposed — conditional on gates · **Date:** 2026-11-07

**Requirements.** Support horizon ≥ product effort; Tier-1 platform for robot compute and dev host; ecosystem
maturity for Nav2/ros2_control/Gazebo pairing.

**Alternatives.** Humble (EOL May 2027), Jazzy (EOL May 2029), Kilted (EOL ~Dec 2026, non-LTS), Lyrical
(EOL May 2031, LTS), Rolling (never for deployment).

**Evidence.** Release/EOL dates verified against `rosdistro` and documentation sources [FACT R04-S01, R04-S11].
Lyrical is the only LTS pairing with Gazebo Jetty LTS (both to May 2031) [FACT R04-S14, R04-S15]. Lyrical is
~5.5 months old at decision date — third-party driver lag is the principal risk [FACT R04-S01].

**Trade-offs.** Lyrical maximises support life and pairs with Jetty LTS; Jazzy is more mature but ends May 2029
and pairs with Harmonic (EOL May 2029). Ubuntu 26.04 Tier-1 requirement may conflict with embedded BSPs
(Lyrical on Noble is Tier 3/source-build) [FACT R04-S03].

**Recommendation.** Target Lyrical; keep Jazzy as a documented fallback; avoid Lyrical-only features in core
code until Gates A–C pass (R04 §4.8). Record distro+rmw in every manifest.

**Risks.** Driver availability; BSP/OS mismatch; Nav2 plugin API churn (`nav2_ros_common` migration).

**Unresolved.** Gate A (compute BSP), Gate B (driver availability), Gate C (spike) — see TECHNOLOGY_DECISIONS §3.

---

## ADR-003 — ros2_control as the hardware-abstraction framework

**Status:** Proposed · **Date:** 2026-11-07

**Requirements.** Swap hardware/simulator backends without forking robot software; standard interfaces;
real-time control loop; lifecycle-managed hardware.

**Alternatives.** ros2_control; custom HAL; micro-ROS-centric design; direct driver nodes.

**Evidence.** ros2_control provides Resource Manager + Controller Manager, pluginlib hardware components
(System/Sensor/Actuator), URDF `<ros2_control>` declarations, named command/state interfaces, enforced limits,
mock components for hardware-free testing, and documented simulator integrations incl. Gazebo [FACT R04-S25,
R02-S05..S12]. Nav2 and MoveIt-style stacks assume this boundary.

**Trade-offs.** Static hardware set per configuration (no URDF reload documented on Rolling docs — re-verify on
Lyrical, audit A-4); FINALIZED recovery needs process restart; safety-critical interfaces only planned
[R02-S08]. These constraints are accepted: they enforce the cold-reconfiguration (Tier 0) policy.

**Recommendation.** Adopt ros2_control; add the Valtoryn Chassis kinematics contract above it
(HARDWARE_ABSTRACTION §3); treat FINALIZED-restart as a tested recovery path.

**Risks.** Doc-version drift; plugin ABI per distro; CiA 402 stack immaturity for drive backends.

**Unresolved.** A-4 re-verification; swerve controller availability; drive-interface conformance.

---

## ADR-004 — Nav2 as the navigation stack, behind a Valtoryn interface

**Status:** Proposed · **Date:** 2026-11-07

**Requirements.** Multi-kinematics planning/control; behaviour-tree orchestration; costmaps; docking; route
graphs; active maintenance; plugin extensibility.

**Alternatives.** Nav2; custom planner/controller; MoveIt (manipulator-oriented); BehaviourTree-only custom stack.

**Evidence.** Nav2 covers differential/omni/Ackermann/legged across DWB, TEB, RPP, MPPI, Smac planners;
behaviour trees with recovery ladder; costmap filters for keep-out/speed/lanes; docking server; route server over
GeoJSON graphs; Collision Monitor for non-safety stopping [FACT R01-S08..S09, R04-S38..S45]. Funded maintainer
(Open Navigation LLC) [FACT R01-S10].

**Trade-offs.** Single-robot scope — no inter-robot traffic coordination (fleet layer's job); 2D costmap-centric;
plugin API churn between distros; LGPL/BSD/Apache mixed licences require BOM tracking.

**Recommendation.** Adopt Nav2 behind a thin Valtoryn navigation interface so planners/controllers/BTs stay
swappable; per-distro plugin branches.

**Risks.** Repetitive-aisle localisation degradation observed in the Nav2 marathon paper [FACT R01-S07];
warehouse validation required (R05 F14).

**Unresolved.** Route-server vs VDA 5050 node/edge mapping; aisle localisation performance; per-plugin licence audit.

---

## ADR-005 — Gazebo Jetty + ros_gz as the default simulator

**Status:** Proposed · **Date:** 2026-11-07

**Requirements.** ROS 2-native integration; physics fidelity adequate for AMR validation; LTS alignment;
headless CI; sensor simulation.

**Alternatives.** Gazebo Jetty/Harmonic; Isaac Sim; Webots; MuJoCo; custom.

**Evidence.** Gazebo is the only simulator with an official ROS-distribution pairing table, vendor binaries,
`ros_gz` bridge and `gz_ros2_control` [FACT R04-S13..S22]. Jetty is LTS to May 2031, pairs with Lyrical
[R04-S14, R04-S15]. Alternatives: Isaac Sim needs RTX GPU and its licence terms were not fully read
[R04-S83..S86]; Webots/MuJoCo lack the ROS pairing depth [R04-S87..S90].

**Trade-offs.** Gazebo's wheel-ground fidelity is unvalidated for AMRs; an open determinism issue exists
(gz-sim #3349) → statistical gates required [FACT R05-S31]; native Windows unsupported → WSL2/dev container.

**Recommendation.** Gazebo Jetty default; keep simulator behind the HAL seam; author own warehouse world;
statistical regression gates; evaluate a second engine as model-form sensitivity check.

**Risks.** Fidelity gaps (F1–F20 thresholds all "no hardware data"); Open-RMF demo compatibility with Jetty
unresolved (R05 U5).

**Unresolved.** Jetty↔RMF/`gz_ros2_control` compatibility; DART friction-element behaviour (R05 U1–U3).

---

## ADR-006 — Fast DDS default RMW; Zenoh evaluated as fleet-scale option

**Status:** Proposed · **Date:** 2026-11-07

**Requirements.** Multi-robot Wi-Fi fleets; discovery that survives warehouse WLAN; ROS 2 Tier-1 support.

**Alternatives.** Fast DDS (default); Cyclone DDS; Connext; rmw_zenoh; Zenoh-native without DDS.

**Evidence.** Default multicast discovery scales poorly and may fail on Wi-Fi [FACT R01-S06]; Fast DDS Discovery
Server and Zenoh router bridging are documented remedies [FACT R04-S62, R04-S57]. rmw_zenoh is Tier 1 since
Kilted/Lyrical but has documented QoS gaps and an SHM issue [FACT R04-S57..S59]. No official latency benchmark was
read [UNRESOLVED].

**Trade-offs.** Fast DDS is the best-supported default; Zenoh's router model suits WAN/multi-host but adds a
router dependency and QoS limitations.

**Recommendation.** Ship `rmw_fastrtps_cpp` as default; run an `rmw_zenoh` spike focused on multi-host bridging,
Wi-Fi behaviour and QoS gaps before any fleet-scale commitment.

**Risks.** Zenoh gaps (deadline/lifespan, TRANSIENT_LOCAL semantics); mixing RMWs is forbidden; domain-ID
management required.

**Unresolved.** Measured comparison on representative warehouse traffic — no benchmark exists in sources.

---

## ADR-007 — VDA 5050 v3 as external fleet protocol; internal facility model as source of truth

**Status:** Proposed · **Date:** 2026-11-07

**Requirements.** Vendor-neutral fleet interoperability; heterogeneous robots sharing traffic space; future
WMS/fleet-control integration.

**Alternatives.** VDA 5050 internal; VDA 5050 external-only; MassRobotics AMR Interop; Open-RMF-native; custom protocol.

**Evidence.** VDA 5050 v3.0.0 (2026-03-18) defines order/state/factsheet topics over MQTT/JSON with node-edge
orders, corridors, zones, requests [FACT R01-S20, R02-S27]. It explicitly excludes safety and traffic-management
logic and has no security [FACT R01-S20]. Open libraries lag (vda5050_core supports v2.0.0) [FACT R01-S22].
MassRobotics standard is dormant/unlicensed [FACT R01-S25]. Open-RMF has no VDA 5050 support in the book read
[R01-S13..S16].

**Trade-offs.** VDA 5050 gives vendor neutrality but QoS 0, no security, order-graph semantics that must map to
the internal facility model; building a v3 gateway is real work.

**Recommendation.** Adopt VDA 5050 v3 as an *optional external gateway*; define one internal facility model
(SYSTEM_ARCHITECTURE §L6, MODULARITY_SPECIFICATION §9) with exporters; evaluate/contribute to `vda5050_core`;
build robot-side v3 gateway only if upstream stalls.

**Risks.** No conformance suite exists; library version lag; MQTT security profile must be built (NFR-4).

**Unresolved.** G-E gate; which VDA versions shipping robots actually speak; RMF↔VDA migration path maturity.

---

## ADR-008 — Fleet coordination: minimal baseline + optional Open-RMF

**Status:** Proposed · **Date:** 2026-11-07

**Requirements.** Multi-robot traffic without collisions/deadlock; usable without heavyweight infrastructure;
path to Open-RMF for building-infrastructure coordination.

**Alternatives.** Open-RMF core; custom reservation coordinator; VDA 5050-only (fleet control external); MiR-style
resource locking.

**Evidence.** Open-RMF implements traffic scheduling with negotiation and fleet adapters but targets AGV-grid
fleets, is DDS-centred, Lyrical support unconfirmed, and showed maturity limits in a hospital field test
[FACT R01-S13..S19]. R07 finds no single deadlock mechanism suffices — combination of release/reservation,
mutexes, negotiation needed [FACT R07 §4.3]. Commercial systems use resource-based or MAPF-based coordination
[R01 §7].

**Trade-offs.** RMF gives building-infrastructure integration (doors/lifts) at the cost of DDS coupling and
unconfirmed distro support; a minimal coordinator is cheaper but less capable.

**Recommendation.** Define a Valtoryn fleet-coordination interface; implement a minimal reservation/queue
baseline; treat Open-RMF as an optional backend adapter. Never make robot-side software depend on RMF's runtime
(R01 §5.1 implication).

**Risks.** Deadlock/livelock in dense fleets; coordination scaling over Wi-Fi (R04 §4.6).

**Unresolved.** RMF Lyrical support; coordination algorithm choice for baseline (R07 §4.3 open items).

---

## ADR-009 — Declarative robot configuration + capability manifest (thin layer on ROS)

**Status:** Proposed · **Date:** 2026-11-07

**Requirements.** Multiple robot variants without code forks; compatibility checking before runtime; fleet-visible
capability declaration; change control for safety-relevant config.

**Alternatives.** Per-robot forks; ROS-native only (xacro+launch+params); model-driven composition (RobMoSys);
runtime self-describing modules; layered config+manifest+HAL (candidate C in R02 §6).

**Evidence.** Clearpath `robot.yaml` and Husarion `components.yaml` converge on "one declarative config →
generated description+launch" [FACT R02-S47..S51]. VDA 5050 factsheet is the domain precedent for capability
manifests [FACT R02-S27]. CiA 402 shows declared≠verified conformance risk [FACT R02-S40]. ros2_control is
static per configuration [FACT R02-S06].

**Trade-offs.** Adds a generator+schema to maintain; drift risk if manifests are hand-written (mitigated by
generation); catalogue bottleneck for new module types.

**Recommendation.** Adopt candidate C as a *thin* layer on ROS-native artifacts (option B as foundation):
config source → generators → URDF/launch/params/manifests; C1–C5 compatibility gates; SemVer everywhere;
escape hatch flagged unvalidated.

**Risights.** Manifest/description drift; schema governance; quantified benefit unproven (R02 U6 — pilot
measurement planned).

**Unresolved.** Manifest schema v1 fields freeze; who approves schema changes; pilot measurement of integration effort.

---

## ADR-010 — Safety architecture boundary: certified safety domain outside ROS 2

**Status:** Proposed · **Date:** 2026-11-07

**Requirements.** Personnel safety per applicable machinery standards; modularity must not weaken the safety
case; ROS software must never be the protective path.

**Alternatives.** Safety functions in ROS 2 nodes; custom safety MCU; certified safety controller + pre-certified
components (R08 Option B); ROS as safety channel via ros2_control "safety interfaces".

**Evidence.** R08 recommends a certified safety controller (Option B), pre-certified third-party scanners and
safety controllers, no first-party certification target, evidence ladder L0–L4 [REC R08 §3–§5]. ros2_control
documents safety-critical interfaces as planned, not delivered [FACT R02-S08]. Nav2 Collision Monitor explicitly
is not safety-certified [FACT R04-S44]. ISO 3691-4:2023 scope/verification applies to driverless trucks
[FACT R02-S56]; full text not inspected.

**Trade-offs.** Separate safety hardware adds cost and integration complexity; buys a defensible safety case
and keeps ROS free of RT-safety requirements.

**Recommendation.** Safety domain = certified controller + pre-certified scanners/STO/brakes/BMS protection;
ROS consumes safety state read-only; autonomy may request safe states but never command protective functions;
per-chassis safety case with reusable method/templates; "safety-ready" posture.

**Risks.** Cost; interface definition between safety domain and ROS (HA-6); tugger/trailer hazard analysis gap
(RESEARCH_AUDIT A-6); ISO 3691-4 normative content unread (A-5).

**Unresolved.** Safety-case ownership; which standards apply per deployment jurisdiction; trailer/towing analysis.

---

## ADR-011 — Languages: C++20 core, Python periphery, no Rust on robot path

**Status:** Proposed · **Date:** 2026-11-07

**Requirements.** Real-time control code; broad ROS 2 ecosystem compatibility; maintainability by small team.

**Alternatives.** C++ only; Python only; Rust (rclrs); mixed.

**Evidence.** rclcpp is Quality Level 1 with ABI/API stability rules [FACT R04-S65]; rclrs has no stability
guarantee and is not a released ROS package [FACT R04-S66, R04-S11]; Lyrical requires C++20/Python 3.12–3.14
[FACT R04-S03]; real-time guidance centres on C++ allocation-free loops [FACT R04-S70..S71].

**Trade-offs.** C++ verbosity vs Python's unsuitability for RT loops; Rust's immaturity in ROS 2 today.

**Recommendation.** C++20 for hardware interfaces, controllers, Nav2 plugins, anything in the CM loop;
Python for launch, tools, tests, non-RT orchestration; Rust excluded from robot control path until rclrs matures.

**Risks.** Team C++ skill requirement; binding generation for interfaces.

**Unresolved.** None blocking.

---

## ADR-012 — Simulation evidence discipline: E0–E4 levels, statistical gates, no safety claims

**Status:** Proposed · **Date:** 2026-11-07

**Requirements.** Defensible simulation-to-hardware validation; no overclaiming; CI practicality.

**Alternatives.** Bitwise-determinism gates; single-run pass/fail; evidence-labelled levels; NASA-STD-7009B-aligned ladder.

**Evidence.** Gazebo run-to-run divergence reported (issue #3349) [FACT R05-S31]; NASA-STD-7009B provides the
validation vocabulary [FACT R05-S47]; R05 defines E0–E4 and F1–F20 fidelity dimensions; R08 defines L0–L4;
all consistent (RESEARCH_AUDIT).

**Trade-offs.** Statistical gates cost CI time (N repeats); labelled evidence reduces misleading dashboards but
requires discipline.

**Recommendation.** Adopt E0–E4 evidence levels on every simulation result; N-repeat statistical regression
gates; parameter provenance registry; simulation never cited as safety evidence; HIL and hardware campaigns
produce the referent data for E2+.

**Risks.** Over-reliance on simulation before hardware data exists; threshold-setting deferred to measurement.

**Unresolved.** All F-dimension thresholds pending hardware data (R05 §8 note).
