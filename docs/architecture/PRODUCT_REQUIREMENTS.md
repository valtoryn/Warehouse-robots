# Product requirements — Valtoryn Warehouse Robotics platform

> **Status:** Proposed requirements. Nothing described here is implemented.
> **Basis:** audited research R01–R08 ([RESEARCH_AUDIT.md](../RESEARCH_AUDIT.md)); all requirements are proposals for owner approval.
> **Evidence tags:** [FACT]/[CALC]/[EST]/[REC]/[UNRESOLVED] as defined in CONTRIBUTING.md; source citations use the research IDs.

## 1. Product statement

A vendor-neutral, open-source, **fully modular autonomous warehouse robotics platform**: one software platform that
runs on different robot chassis, locomotion types, sensor sets and payload modules, from simulation through
hardware-in-the-loop to physical deployment. The first reference implementation is a modular differential-drive AMR.
Software modularity is delivered first; mechanical modularity is introduced progressively.

## 2. Scope

**In scope (proposed):**

- Robot-side autonomy software: hardware abstraction, locomotion control, localisation, mapping, navigation,
  task logic, diagnostics, fleet-facing interfaces.
- A robot configuration and capability-manifest layer enabling multiple robot variants from one platform.
- A simulation/digital-twin environment using the same software stack as hardware.
- Fleet-facing interoperability: a VDA 5050 v3 gateway and an internal facility model with exporters.
- Fleet coordination: a minimal reservation-based baseline coordinator plus an optional Open-RMF integration path.
- Warehouse task/order model and a WMS-facing API.
- Diagnostics, lifecycle management, configuration and version management.

**Out of scope (explicitly):**

- Safety certification or safety-rated software. Safety functions live in separate certified hardware; the platform
  consumes safety state only (R08 §4). No requirement here may be read as a safety claim.
- A new middleware, navigation stack, simulator, or safety layer (R01 §8 "do not build").
- Commercial fleet-manager feature breadth (R01 §7 implication).
- Physical hardware production: this milestone defines requirements and specifications, not a product.

## 3. Functional requirements

### 3.1 Modularity

| ID | Requirement | Basis |
|---|---|---|
| FR-M1 | The platform shall run unmodified on at least two robot configurations (chassis/sensor/payload variants) selected by configuration, not code forks. | R02 §6, §7.2 [REC] |
| FR-M2 | Locomotion shall be a pluggable chassis module; differential drive is the first implementation; omnidirectional and other kinematics must be addable without changing planner interfaces. | R03 §15.1–15.2, R04 §4.1 [REC] |
| FR-M3 | Every module shall expose a lifecycle contract (configure/activate/deactivate/cleanup, error state) and a capability manifest. | R02 R3, R9 [REC] |
| FR-M4 | The capability manifest shall be generated or validated against the robot description, never solely hand-written. | R02 §5.2 M3, F2 [REC] |
| FR-M5 | Compatibility shall be checked at four gates: schema (C1), static resolution (C2), bring-up identity (C3), runtime monitoring (C4); safety-relevant changes pass a re-validation gate (C5). | R02 §5.4, R12 [REC] |
| FR-M6 | Robot configuration shall be the single source of truth; URDF/xacro, launch files, controller parameters and manifest exports are generated artifacts. | R02 R5–R6, Clearpath/Husarion precedent [FACT R02-S47..S51] |
| FR-M7 | Software modularity shall use only ROS-native mechanisms (composable lifecycle nodes, pluginlib, ros2_control). No custom plugin runtime. | R02 §5.5 P3, R15 [REC] |

### 3.2 Autonomy (reference robot)

| ID | Requirement | Basis |
|---|---|---|
| FR-A1 | The reference robot shall navigate autonomously in a structured warehouse environment using Nav2 (planners, controllers, costmaps, behaviour trees, docking) behind a Valtoryn navigation interface. | R01 §3, R04 §4.1, R06 §8.1 [REC] |
| FR-A2 | Localisation and mapping shall be swappable (`map→odom` provider interface); SLAM Toolbox preferred for map building; AMCL or slam_toolbox localisation mode for operation. | R04 §4.1, R06 §8.5 [REC] |
| FR-A3 | Payload state (identity, mass, geometry) shall be a first-class input that can switch footprint, costmap filters, speed limits and collision-monitor zones. | R06 §8.7, R07 §4.1 [REC] |
| FR-A4 | Facility assets (map, filter masks, route graph, dock database) shall be versioned independently of software releases. | R06 §8.6 [REC] |

### 3.3 Warehouse operations and fleet

| ID | Requirement | Basis |
|---|---|---|
| FR-F1 | The platform shall maintain one internal facility model (nodes, edges, zones, docks, keep-out/speed rules) with exporters to LIF, RMF graph and Nav2 GeoJSON formats. | R07 §4.3.5 [REC]; reconciles R06/R07 split per RESEARCH_AUDIT |
| FR-F2 | Fleet-to-robot communication shall support VDA 5050 v3 as an optional external gateway, never as the internal architecture. | R01 §5.3, R07 §4.3 [REC] |
| FR-F3 | The robot shall complete an accepted order's released "base" safely with no network connectivity (store-and-forward semantics per VDA 5050 order model). | R07 §4.2 [REC] |
| FR-F4 | Fleet coordination shall have a minimal built-in baseline (resource reservation, queueing, deadlock avoidance) usable without Open-RMF; Open-RMF shall be an optional backend. | R01 §8, R07 §4.3 [REC] |
| FR-F5 | Task allocation shall use capability matching with default-deny semantics: type profile, instance state and task requirements, fail-closed on unassignable. | R07 §4.1 [REC] |
| FR-F6 | Task/order lifecycle shall support idempotency keys and an explicit `NEEDS_VERIFICATION` state for ambiguous pick/drop outcomes. | R07 §4.4 [REC] |
| FR-F7 | A WMS-facing task/order API shall exist; no open equivalent was found (R01 §8 "Build"). | R01 §8 [REC] |

### 3.4 Simulation and validation

| ID | Requirement | Basis |
|---|---|---|
| FR-S1 | The same robot software stack shall run unchanged in simulation and on hardware; only the hardware-abstraction backend differs. | R02 §5.6, R05 §5.1, Husarion precedent [FACT R02-S50] |
| FR-S2 | Simulation parameters shall carry provenance (datasheet/measured/assumed) and uncertainty; results carry an evidence level (E0–E4). | R05 §5.3–5.4, §7 [REC] |
| FR-S3 | Regression testing shall use statistical gates (N repeats, fixed seeds), never bitwise determinism. | R05 §3.12, §5.7 [REC] |
| FR-S4 | Fault injection (sensor loss, comms outage, low battery, payload change, drive faults) shall be a first-class scenario capability. | R05 §8 F-series, R06 §8.8 [REC] |
| FR-S5 | HIL testing shall exercise real compute/firmware/drives against a simulated plant. | R05 §6 [REC] |

### 3.5 Diagnostics, lifecycle, configuration

| ID | Requirement | Basis |
|---|---|---|
| FR-D1 | Every module shall expose lifecycle state, diagnostics and a liveness bond to its supervisor. | R02 R3, Nav2 bond precedent [FACT R02-S13] |
| FR-D2 | The platform shall record rosbag2/MCAP of simulation and field runs, with snapshot capture for faults. | R04 §4.4 [REC] |
| FR-D3 | Configuration changes to safety-relevant fields shall fail a re-validation gate (C5) until a person records re-validation. | R02 R21, §5.4 C5 [REC] |
| FR-D4 | Module identity shall distinguish unit identity (serial/UUID) from type identity (reverse-domain name + version); bring-up verifies observed vs declared identity and fails closed on motion/safety paths. | R02 §5.1 I1+I2, §5.4 C3 [REC] |

## 4. Non-functional requirements

| ID | Requirement | Basis |
|---|---|---|
| NFR-1 | Licence: Apache-2.0 platform; dependency licence audit (Nav2 mixed LGPL/Apache/BSD; SLAM Toolbox LGPL-2.1) before any release. | README, R01 §3.5 [FACT] |
| NFR-2 | Determinism where required: motor control loop at fixed rate via ros2_control RT settings; ROS graph is not the real-time path for safety functions. | R04 §2.2, R08 §4 |
| NFR-3 | Versioning: SemVer for platform, manifest schema and Valtoryn-defined interfaces; no breaking change within a released line; record ROS distro + rmw in every manifest. | R02 §5.3, R13 [REC] |
| NFR-4 | Security: documented TLS/mTLS profile for fleet MQTT links; DDS-Security available via SROS2; no VDA 5050 security assumptions (spec has none). | R01 §8 security row, R01-S20 [FACT] |
| NFR-5 | Quality: REP-2004-style quality declarations for Valtoryn packages; target Level 3 initially, Level 2 for core interface packages. | R04 §4.4 [REC] |
| NFR-6 | Portability: Linux/Ubuntu primary; Windows 11 host supported via WSL2/dev container; native Windows not a target for Gazebo/ros2_control. | R04 §4.5 [REC] |
| NFR-7 | Safety posture: platform is "safety-ready" — it must not impede a separate certified safety layer, must consume its state, and must never claim safety function. | R08 §3–§5 [REC] |

## 5. Constraints and dependencies

| ID | Constraint | Basis |
|---|---|---|
| C-1 | Primary ROS 2 distribution: **Lyrical Luth** (LTS to May 2031) with **Jazzy** as documented fallback — conditional on R04 Gates A–C. Not yet decided by owner. | R04 §4.1, §4.3; RESEARCH_AUDIT A-1 |
| C-2 | Gazebo Jetty (LTS to May 2031) paired with the chosen ROS distro via `ros_gz`/`gz_ros2_control`. | R04 §4.1, R05 §5.2 |
| C-3 | ros2_control hardware set is static per configuration (no URDF reload documented) → cold reconfiguration is the default tier. | R02 §3.2, §5.6 |
| C-4 | Nav2 collision monitor and all ROS components are explicitly not safety-certified. | R04 §2.3 [FACT R04-S44] |
| C-5 | Open-RMF Lyrical support unconfirmed; do not depend on it. | R01 §5.1 [UNRESOLVED] |
| C-6 | No hardware exists; all performance numbers in engineering specs are [EST]/[CALC] until measured. | Project status |

## 6. Success criteria for the architecture milestone

1. Every requirement above traceable to audited research (done via basis column).
2. Architecture documents define all layers, interfaces, data ownership and lifecycle rules without inventing
   requirements (see SYSTEM_ARCHITECTURE, MODULARITY_SPECIFICATION).
3. Reference-robot and hardware-interface specs contain only sourced/calculated/estimated values, each labelled.
4. `python tools/check_docs.py` passes with 0 errors.
