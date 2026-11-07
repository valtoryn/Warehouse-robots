# System architecture — Valtoryn Warehouse Robotics platform

> **Status:** Proposed architecture. Nothing is implemented. All names below are proposals.
> **Basis:** audited research R01–R08. Every layer decision cites its research basis; open items are marked.

## 1. Design goals and constraints

1. **One platform, many robots.** Robot variants are data (configuration + modules), not forks (FR-M1, R02 §7.4).
2. **ROS-native first.** Reuse ROS 2 composable lifecycle nodes, pluginlib, ros2_control, Nav2, BehaviorTree.CPP.
   No parallel module runtime, no custom plugin loader (R02 R2, R15).
3. **Simulation is a backend, not a fork.** The same robot software runs against real hardware or a simulator
   through the hardware-abstraction boundary (FR-S1).
4. **Safety boundary is absolute.** The safety domain never depends on ROS 2; autonomy may request but never
   command safety states (R08 §4, FR safety boundary).
5. **External interoperability is a projection.** VDA 5050, LIF, RMF graphs and Nav2 GeoJSON are exports of one
   internal facility model, never the internal format (FR-F1, FR-F2).

## 2. Layered architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ L7  Warehouse applications & operator interfaces                │
│     WMS/task-order API · fleet-facing gateway (VDA 5050) · UI   │
├─────────────────────────────────────────────────────────────────┤
│ L6  Fleet intelligence                                           │
│     Facility model · task allocation · traffic coordination     │
│     (baseline coordinator; Open-RMF optional backend)           │
├─────────────────────────────────────────────────────────────────┤
│ L5  Shared robotics core                                         │
│     Behaviour trees · task primitives · diagnostics ·           │
│     lifecycle supervisor · configuration & manifest services    │
├─────────────────────────────────────────────────────────────────┤
│ L4  Autonomy stack                                               │
│     Nav2 (nav) · AMCL/SLAM Toolbox (localisation) ·             │
│     robot_localization (fusion) · payload-aware state           │
├─────────────────────────────────────────────────────────────────┤
│ L3  Hardware abstraction                                         │
│     ros2_control (controllers, hardware components) ·           │
│     Valtoryn chassis kinematics · motor/drive/sensor drivers ·  │
│     Valtoryn capability & manifest layer                        │
├─────────────────────────────────────────────────────────────────┤
│ L2  Physical robot configurations                                │
│     URDF/SDF + <ros2_control> · module manifests · mounts ·     │
│     safety hardware (separate, outside ROS)                     │
├─────────────────────────────────────────────────────────────────┤
│ L1  Backends                                                     │
│     Real hardware · Gazebo (gz_ros2_control) · mock hardware ·  │
│     HIL plant                                                    │
└─────────────────────────────────────────────────────────────────┘
         ▲ diagnostics/safety-state read-only link
┌─────────────────────────────────────────────────────────────────┐
│ S   Safety domain (NOT ROS 2): certified safety controller,     │
│     safety scanners, STO/brakes, BMS protection. ROS consumes   │
│     its state; never commands it.                               │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1 Layer responsibilities

| Layer | Owns | Must not own | Basis |
|---|---|---|---|
| L7 Applications | Order intake, WMS API, VDA 5050 gateway translation, operator UI | Robot kinematics, safety decisions | R01 §5.3, R07 §4.4 |
| L6 Fleet intelligence | Facility model, task allocation (capability matching), traffic coordination, fleet state | On-robot control loops, safety functions | R07 §4.1–4.3 |
| L5 Robotics core | Behaviour-tree orchestration of robot tasks, lifecycle supervision, diagnostics aggregation, config/manifest services, fault-reaction policies | Navigation algorithms (Nav2 owns), hardware protocols | R02 R3, R06 §8.8 |
| L4 Autonomy | Path planning, control, costmaps, localisation, docking | Fleet decisions, safety functions, task semantics | R01 §3, R04 §4.1 |
| L3 Hardware abstraction | Joint/actuator/sensor command & state interfaces, chassis kinematics, odometry, motor/drive models, capability declarations | Application logic, fleet logic | R02 §3.2, R03 §15.1 |
| L2 Robot configurations | URDF, mounts, sensor placement, `<ros2_control>` blocks, module manifests, parameters | Platform code | R02 R5–R8 |
| L1 Backends | Physics, sensor simulation, actuator response, network emulation | Any robot logic | R05 |
| S Safety | Protective fields, safe stop, STO, brakes, safe state per mode | Everything else; never on ROS | R08 §4 |

## 3. Interfaces and communication contracts

All intra-robot contracts use ROS 2 (topics/services/actions) unless stated. External contracts are versioned.

| Interface | Type | Producer → Consumer | Contract |
|---|---|---|---|
| `cmd_vel` | topic `geometry_msgs/TwistStamped` | Nav2/controller → diff_drive (or chassis) controller | Stamped velocity; `cmd_vel_timeout` enforced; per-axis limits from URDF (R04 §2.3, §4.2) |
| Joint command/state | ros2_control interfaces | Controllers ↔ hardware components | Named interfaces, units per REP-103, limits enforced by CM (`enforce_command_limits`) (R02 §3.2) |
| `map→odom` transform + pose | TF + topic | Localiser (swappable plugin) → Nav2 | Health state published; failure triggers Nav2 recovery ladder (R06 §8.5) |
| Nav goals / docking | actions | Task BT → Nav2 servers | Nav2 action interfaces; docking via `opennav_docking` (R04 §2.3) |
| Diagnostics | `diagnostic_updater` topics | Every module → aggregator | Standard ROS diagnostics; liveness bond per module (R04 §2.10) |
| Safety state | dedicated non-ROS channel (hardware) | Safety controller → robot compute (read-only) | State only: safe/unsafe, protective-field status, STO status. ROS never writes (R08 §4) |
| Robot → fleet | ROS topics internally; VDA 5050 MQTT externally | Robot → fleet control | Internal: state model. External: VDA 5050 v3 topics (order/state/factsheet/…) (FR-F2) |
| Fleet → robot | same | Fleet control → robot | VDA 5050 order model: released base + horizon; robot completes base autonomously (FR-F3) |
| Facility model | internal store + exporters | L6 → L7 gateways, Nav2 route server, RMF adapter | One model; exports to LIF, RMF graph, Nav2 GeoJSON (FR-F1) |
| Module manifest | generated file (JSON/YAML, schema-versioned) | Config generator → bring-up, fleet factsheet export | SemVer schema; provides/requires; identity expectations; verification block; safety-evidence refs (R02 R9) |

## 4. Data ownership

| Data | Owner | Consumers | Notes |
|---|---|---|---|
| Robot configuration (source of truth) | Robot config package | Generators, bring-up, fleet factsheet | Generated artifacts never hand-edited (FR-M6) |
| URDF/SDF, `<ros2_control>` tags | Generated artifacts | ros2_control, Nav2, Gazebo | Inputs to CM limit enforcement |
| Capability manifest | Generated + small hand-authored part | Compatibility gates C1–C5, fleet capability matching | Must not contradict description (F2 mitigation) |
| Facility model | Fleet intelligence (L6) | Nav2 route server (export), VDA/RMF gateways | Versioned independently of software (FR-A4) |
| SLAM map, filter masks, dock DB | Versioned facility assets | Localiser, costmaps, docking | Separate versioning per R06 §8.6 |
| Safety state | Safety domain (S) | Robot compute read-only, fleet status | Never written by ROS |
| Telemetry/bags | Diagnostics (L5) | Fleet status, twin synchronisation, validation | MCAP default; snapshot mode (R04 §2.10) |
| Battery/power model | L3 power module + L1 backend model | Energy management, low-battery behaviours | Gazebo battery insufficient alone (R05 §3.7) |

## 5. Configuration management

- **Source:** one declarative robot configuration per variant (schema-versioned): module instances
  (type, version range, name, parent frame, pose, parameters), communication endpoints, sim/hardware profile,
  safety-evidence references (R02 R5).
- **Artifacts:** URDF/xacro, `<ros2_control>` sections, controller/Nav2 parameter files, launch files, manifest
  exports — all generated; build fails on drift (FR-M6).
- **Hashes:** full config hash at commissioning; separate hash over the safety-relevant subset for gate C5
  (R02 §5.6).
- **Profiles:** `simulation` and `hardware` are profiles of the same configuration; swap happens at L3 backend
  selection, not by forking code (FR-S1).
- **Versioning:** SemVer everywhere; ROS distro + rmw recorded per manifest; dependency ranges reuse REP-149
  `version_gte`/`version_lt` semantics (R02 §5.3).

## 6. Lifecycle and plugin model

- Every Valtoryn module is a composable lifecycle node or ros2_control component: Unconfigured → Inactive →
  Active → Finalized, with error transitions (R02 §3.1).
- Process layout is a deploy-time choice (component containers); fault isolation vs overhead is configurable
  per deployment (R02 §3.1, P3).
- **Reconfiguration tiers** (R02 R16): Tier 0 cold (stop, regenerate, restart) — default for all
  motion/safety-path modules; Tier 1 warm lifecycle cycling for non-safety payloads while stationary;
  Tier 2 hot-plug only for non-safety, non-motion, identity-verifiable modules; Tier 3 prohibited on safety path.
- **Failure handling:** hardware component reaching FINALIZED requires supervisor restart of the control process
  (documented gap: no reload service — verify on Lyrical, RESEARCH_AUDIT A-4). Nav2-style bond takes the system
  down in a controlled way on server crash. Diagnostics surface degraded states; task layer decides recovery.

## 7. Capability declarations

- Each module manifest declares `provides[]`/`requires[]` with version ranges, ROS interfaces + type hashes,
  ros2_control interface names with units and limits, frames (REP-105), mount declarations, hardware identity
  expectations, ROS distro + rmw, verification block, and an explicit safety block ("no safety claim" when none)
  (R02 R9).
- Robot-level manifest aggregates modules and exports projections: VDA 5050 factsheet, capability-matching input
  for fleet dispatch (default-deny, three-layer check per R07 §4.1).
- Declared vs verified capability are distinct fields; verification records who/when/how (R02 §3.3, F1).

## 8. Backend boundaries

| Boundary | Contract |
|---|---|
| L3 ↔ L1 hardware | ros2_control `SystemInterface`/`Sensor`/`Actuator` plugins; command/state interfaces; lifecycle |
| L3 ↔ L1 simulator | `gz_ros2_control` (or equivalent) implementing the same interface set; simulator-only models (motor, battery, latency) live behind this seam (R05 §5.1) |
| L4 ↔ L3 | Standard ROS topics/actions/TF; `TwistStamped` cmd_vel; Nav2 plugin interfaces |
| L6 ↔ L7 external | VDA 5050 v3 MQTT/JSON gateway (optional); REST/WebSocket task API for WMS (proposed); exporters for LIF/RMF/GeoJSON |
| L5 ↔ S safety | Read-only safety-state channel; defined safe states per mode; no command path |

## 9. Error handling and recovery

- **Module level:** lifecycle error state → supervisor policy: retry configure, degrade capability, or take robot
  to safe stop request (never a direct safety command) (R08 boundary).
- **Autonomy level:** Nav2 behaviour-tree recovery ladder (clear costmap, spin, wait, back up) plus
  Valtoryn-level fault-reaction budgets derived from stopping distances (R06 §8.8, R08 worked example).
- **Fleet level:** order state machine with `NEEDS_VERIFICATION` for ambiguous outcomes; robot completes released
  base autonomously on comms loss (FR-F3).
- **Safety level:** protective functions run entirely in domain S; ROS observes and requests only.

## 10. Versioning and extensibility

- Platform releases pinned to one ROS 2 LTS line; non-LTS distros are CI canaries only (R04 §4.8).
- Valtoryn-defined message/service/action interfaces: immutable once released within a major version
  (Cyphal-style rule, R02 §5.5); SemVer + ROS type-hash assertion at runtime.
- New locomotion type = new chassis module (ros2_control System + kinematics + controllers), not platform change
  (FR-M2; VDA 5050 extensible kinematics precedent, R02 §3.3).
- New module type = new manifest schema minor version + catalogue entry; escape hatch exists but is flagged
  "unvalidated" (R02 R7).
- Deprecation: announced one release ahead; removal only at major version.

## 11. Explicit non-goals

- No custom middleware, plugin framework, simulator, safety layer, or fleet protocol (R01 §8).
- No runtime hot-plug of motion/safety modules (R02 R16).
- No claim that simulation results are physical validation (R05 §7).
- No VDA 5050 conformance claim until a neutral conformance suite exists (R07 unresolved).
