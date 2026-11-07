# Modularity specification — Valtoryn platform

> **Status:** Proposed specification. Nothing is implemented.
> **Basis:** R02 (primary), R03 §15, R06 §8, R07 §4. Resolves the R06/R07 facility-model split noted in
> [RESEARCH_AUDIT.md](../RESEARCH_AUDIT.md).

## 1. Three levels of modularity

| Level | What varies | Mechanism | Phase |
|---|---|---|---|
| Software | Algorithms, drivers, task logic, process layout | Composable lifecycle nodes + pluginlib + ros2_control | First (now) |
| Mechanical | Chassis, wheels, payload deck, sensor mounts, power, compute | Mount frames in robot config; catalogued mount types; later a Valtoryn module interface spec | Progressive, after first robot |
| System | Heterogeneous robots sharing warehouse apps and fleet intelligence | Capability manifest + facility model + fleet gateways | With fleet layer |

Rule (R02 §4, R1): **compatibility is declared per layer; no layer infers compatibility from another.** A lidar
"fits" only if the mechanical mount declaration, the electrical interface, the driver and the capability manifest
all agree — each checked at its own gate.

## 2. Module taxonomy

A **module** is the unit of configuration, identification and compatibility checking. Module kinds:

| Kind | Examples | ros2_control type | Lifecycle owner |
|---|---|---|---|
| Chassis/locomotion | Differential-drive base, future omni/swerve | System | Resource Manager |
| Actuator | Wheel motor+drive, steering module, lift actuator | Actuator | Resource Manager |
| Sensor | 2D safety LiDAR, nav LiDAR, IMU, depth camera | Sensor | Resource Manager |
| Compute | Jetson Orin, Pi 5, MCU bridge | (not a ros2_control component; declared in config) | Supervisor |
| Power | Battery pack, BMS, charger interface | System/GPIO where applicable | Supervisor + safety domain |
| Payload | Conveyor top, shelf carrier, tugger hitch, forks | System + declared interfaces | Supervisor |
| Software-only | Perception node, task BT library, fleet gateway | Composable node | Lifecycle manager |

## 3. Robot configuration (source of truth)

One declarative, schema-versioned file per robot variant containing (R02 R5, adapted):

```yaml
schema_version: "1.0"                # manifest/config schema, SemVer
robot: { id, serial, variant }
modules:
  - type: "com.valtoryn.chassis.differential"   # reverse-domain type name
    version: "^1.0"                    # SemVer range (REP-149 style)
    instance: "base"
    parent_frame: "base_link"
    pose: { xyz: [0,0,0], rpy: [0,0,0] }
    parameters: { wheel_radius: ..., wheel_separation: ..., ... }
    safety_evidence: ["SE-000"]        # references, never claims
target: { profile: simulation|hardware|hil, ros_distro: "lyrical", rmw: "..." }
```

- Generators emit: URDF/xacro (incl. `<ros2_control>`), launch files, controller/Nav2 parameter files,
  module manifests, and (later) VDA 5050 factsheet projection. Generated files are build artifacts; the build
  fails if they differ from generator output (FR-M6).
- Escape hatch: an `unvalidated` module type flag for hardware outside the catalogue (R02 R7); such modules
  cannot pass C3 on motion/safety paths.

## 4. Module manifest

Fields (R02 R9, condensed — full schema is a deliverable of the config-generator work item):

| Field group | Contents |
|---|---|
| Identity | `manifest_schema_version` (SemVer), `module_type` (reverse-domain), `module_version` (SemVer) + optional build identity (VCS hash/image CRC) |
| Interfaces | `provides[]`, `requires[]` with SemVer ranges; ROS interfaces with type names + pinned type hashes; ros2_control interface names, units (REP-103), min/max limits |
| Frames | REP-105 frame declarations; mount declarations (parent frame, mount type, occupied mounts) |
| Hardware identity | Expected vendor/product/firmware range for C3 verification |
| Platform | ROS distro, rmw, dependency ranges |
| Verification | `verified_by`, `verified_at`, `verification_method`; `declared` vs `verified` capability split |
| Safety | References to safety-evidence IDs; explicit "no safety claim" where none; safety-relevant field set is separately hashed (gate C5) |
| Extensibility | Enumerations (kinematics, payload class, actions) are open/extensible per VDA 5050 precedent |

## 5. Compatibility pipeline (gates C1–C5)

| Gate | When | Check | Failure behaviour |
|---|---|---|---|
| C1 Schema | Authoring/CI | Manifest conforms to schema; units; required fields | Reject at CI |
| C2 Static resolution | Config build | All `requires` satisfied; version ranges; frames exist; mounts occupied once; interface names unique | Build fails |
| C3 Bring-up | Each start | Observed hardware identity == declared; firmware in range; type hashes match | **Fail closed** on motion/safety path; degrade-with-warning allowed for informational payloads |
| C4 Runtime | While running | Liveness bonds, diagnostics, command-limit enforcement | Degrade → safe-state request |
| C5 Safety re-validation | On config change | Hash of safety-relevant subset vs hash recorded at last validation | Block activation until re-validation recorded |

## 6. Identity model

- **Unit identity:** per-unit serial/UUID (assigned at manufacture).
- **Type identity:** reverse-domain module type name + semantic version.
- **Electrical-layer identity** (future, Valtoryn-designed modules): boot-readable ID with UUID + type +
  version + CRC, patterned on HAT EEPROM / Cyphal GetInfo (R02 §5.1 I3). Until hardware exists, rely on bus-level
  identity (USB descriptors, CAN/EtherCAT, driver-reported IDs) — option I1+I2.
- No dynamic plug-and-play node-ID allocation (Cyphal-style) until a concrete need exists (R02 I4 deferred).

## 7. Reconfiguration tiers

| Tier | Scope | Policy |
|---|---|---|
| 0 Cold | Everything on motion/safety path | Default. Stop → change config → regenerate → restart |
| 1 Warm | Non-safety payloads, robot stationary in maintenance state | Lifecycle cycle of the module |
| 2 Hot | Non-safety, non-motion, identity-verifiable modules only | Allowed only if C3 identity check passes at attach |
| 3 Prohibited | Anything on safety path | Never hot-plug; requires future safety architecture |

## 8. Locomotion as a module

- Chassis module declares kinematics type (extensible enum: DIFFERENTIAL, OMNIDIRECTIONAL, ACKERMANN,
  TRICYCLE, SWERVE, …), wheel geometry, and provides a `Chassis` kinematics interface
  (forward/inverse twist mapping, per-chassis odometry covariance, calibration routine, limits).
- Controller selection is per-configuration: `diff_drive_controller` first; `mecanum_drive_controller`,
  `omni_wheel_drive_controller`, `steering_controllers_library` exist for other kinematics (R04 §2.2).
- No kinematics other than differential drive is claimed implemented; the interface must not assume it.

## 9. Facility model (reconciles R06/R07)

One internal, versioned facility model owned by fleet intelligence (L6), containing:

- **Topology:** nodes and directed edges (lanes, allowed areas) — superset of VDA 5050 node/edge, LIF, RMF
  graph and Nav2 GeoJSON semantics.
- **Zones & constraints:** keep-out, speed-limit, preferred-lane, blocked/release — including the semantics of
  Nav2 costmap filters and VDA 5050 zone types (this absorbs R06's filter-mask assets).
- **Assets:** docks (charging/non-charging), charging stations, doors/lifts hooks, pick/drop stations.
- **Versioning:** each asset class versioned independently (R06 §8.6); the model as a whole carries a
  facility-map version exchanged with fleet control.

Exporters: LIF, RMF navigation graph, Nav2 route-server GeoJSON, VDA 5050 order/horizon segments.
The internal model is never serialized in an external format internally (FR-F1).

## 10. Versioning rules

- SemVer 2.0.0 for: platform release, config schema, manifest schema, module packages, Valtoryn interfaces.
- No major bump inside a released Valtoryn line (ROS rule adopted, R02 §5.5).
- Valtoryn-defined types: same name + same major = semantically compatible; released definitions immutable
  except whitespace/comments/deprecation markers (Cyphal rule).
- Type hashes (RIHS01) used as runtime tripwires, not compatibility oracles (R02 §5.3).
- Dependency ranges in manifests use `version_gte`/`version_lt` semantics (REP-149).

## 11. What modularity does NOT do

- It does not make modules safety-rated; safety evidence is referenced, not provided (R02 R21).
- It does not permit undeclared capability use: fleet dispatch defaults to deny on undeclared predicates
  (R07 §4.1).
- It does not require every module to be hot-swappable; Tier 0 cold reconfiguration is the norm.
- It does not fix the catalogue bottleneck: new module *types* require generator/catalogue work; the escape
  hatch is visible but flagged unvalidated.
