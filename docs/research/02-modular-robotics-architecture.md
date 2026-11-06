# R02 — Modular Robotics Architecture
> **Status:** Research document — proposed findings, nothing here is implemented.
> **Workstream:** R02 · **Last verified:** 2026-11-07 · **Evidence legend:** see below

## Evidence legend

- **[FACT]** established by a cited source (always followed by a source ID such as [R02-S06])
- **[CALC]** derived by a shown calculation from cited or labelled inputs
- **[EST]** engineering estimate or assumption (basis stated)
- **[REC]** Valtoryn recommendation or proposal (engineering judgement, not established fact)
- **[UNRESOLVED]** could not be established; what is needed is stated

Nothing in this document describes a capability of the Valtoryn platform as implemented. No hardware exists, and no hardware has been tested. Every statement about Valtoryn is a proposal.

---

## 1. Scope and method

**Question.** How can Valtoryn support multiple robot configurations (chassis or locomotion types, sensors, payloads) without duplicating the software platform? Which mechanisms for module identity, capability description, versioning, compatibility checking, plugin loading, hot-plug and configuration management have public precedent, and what do they cost?

**Method.** I read primary documentation and specifications on 2026-11-07: ROS 2 documentation sources and design articles, the ros2_control and Nav2 documentation, REPs, the VDA 5050 v3.0.0 specification, the OPC UA for Robotics (OPC 40010-1) reference site, the Cyphal specification, vendor and consortium pages (CiA, EtherCAT Technology Group, USB-IF, Raspberry Pi), robot-vendor configuration repositories (Clearpath, Husarion), and public catalogue pages for ISO/IEC standards. Where a canonical page was blocked by an anti-bot challenge (for example the rendered REP pages at ros.org), I read the same document from its source repository instead and cite that.

**What this document is not.** It does not choose the ROS 2 distribution, middleware, fleet protocol or safety architecture; those belong to other workstreams. Where this document touches them, it flags the dependency.

**Honesty notes.**
- Paywalled standards (ISO, IEC, ANSI/A3) were not read in full text. Only public catalogue pages, abstracts and press descriptions were inspected, and claims are limited to those.
- Several analyses below are reasoning from precedent rather than measurement. They are tagged [REC] or [EST], not [FACT].
- Vendor frameworks (Clearpath, Husarion) are evidence that a pattern is *used*, not that it is *good*; I found no independent evaluation of either.

---

## 2. Summary of key findings

1. **ROS 2 already supplies most of the software-modularity machinery.** Composable nodes loaded into containers at deploy time, lifecycle (managed) nodes with a defined state machine, and pluginlib for runtime-loaded classes are all standard, documented mechanisms [FACT: R02-S01, R02-S02, R02-S03]. ros2_control and Nav2 both build their extension model on pluginlib and lifecycle [FACT: R02-S05, R02-S13].
2. **ros2_control gives a real hardware-abstraction boundary, but a static one.** Hardware is described in the URDF `<ros2_control>` tag (types: system, actuator, sensor), loaded as plugins, and exposed as named command/state interfaces. The Controller Manager documentation states that reloading the URDF is not supported, and a hardware component that reaches FINALIZED after an error cannot be recovered without reloading the plugin, for which there is no service [FACT: R02-S06, R02-S09]. Runtime hot-plug of hardware components is therefore not a supported pattern in the documentation I read.
3. **Two independent robot vendors converge on "one declarative config file, generated description and launch files".** Clearpath's `robot.yaml` generates URDF/xacro, launch and parameter files; Husarion's `components.yaml` places catalogued components on parent links [FACT: R02-S47, R02-S48, R02-S49, R02-S51]. This is the strongest direct precedent for Valtoryn's candidate "robot configuration" layer.
4. **VDA 5050's factsheet is the most complete public precedent for a capability manifest in the warehouse domain.** It is a mandatory, retained, versioned JSON document with type specification, physical parameters, protocol limits, supported optional parameters and actions, geometry, load specification and software/hardware versions [FACT: R02-S27]. Fleet control must send only optional fields the robot declares it supports [FACT: R02-S27].
5. **Declared conformance and real conformance diverge in practice.** CiA's own page says CiA 402's many optional functions limit device exchangeability, and some vendors implement a subset yet claim conformity [FACT: R02-S40]. A ROS Discourse thread notes vendors interpret common message semantics differently [FACT: R02-S53; weak source, forum post]. A capability manifest without verification is therefore a liability.
6. **Versioning precedent is mature at the package level and weak at the interface level.** ROS follows SemVer with extra rules (no major bumps inside a released distribution; ABI is public interface) [FACT: R02-S20]. ROS 2 type hashes (RIHS01) detect interface change but, as of the 2023 slides, automatic translation between versions was long-term, delivery undated [FACT: R02-S24]. Cyphal gives the cleanest published rule set for interface versioning: same name plus same major version must be semantically compatible [FACT: R02-S36].
7. **Runtime plug-and-play identity is well precedented at the electrical layer** (Raspberry Pi HAT ID EEPROM, USB descriptors, EtherCAT SII/ESI, Cyphal GetInfo and plug-and-play node-ID allocation) [FACT: R02-S38, R02-S46, R02-S42, R02-S36]. The Cyphal specification itself says deterministic, robust applications are unlikely to benefit from its plug-and-play feature [FACT: R02-S36].
8. **Modularity increases the safety-validation burden; it does not remove it.** The standards I could inspect (ISO 3691-4:2023 scope, ISO 13849-1:2023 abstract, IEC 61508-1 abstract, ANSI/A3 R15.08-3 press description) frame safety around validated safety functions and management of change [FACT: R02-S56, R02-S57, R02-S58, R02-S59]. ros2_control's own documentation says safety-critical interfaces are only planned and that all command interfaces are currently available in the INACTIVE state [FACT: R02-S08].

**My overall assessment** [REC]: the layered "robot configuration + capability manifest + hardware abstraction" approach is sound and well precedented, *if* it is built on top of ROS-native mechanisms rather than beside them, the manifest is generated or validated against the actual description rather than hand-duplicated, and runtime hot-plug is restricted. Section 6 evaluates it against four alternatives.

---

## 3. Findings

### 3.1 Software component models

| Mechanism | What it does | Key documented properties | Source |
|---|---|---|---|
| ROS 2 composition | Nodes written as "components" (shared libraries) loaded into a container process at deploy time | Process layout becomes a deploy-time decision: separate processes give fault isolation and easier debugging; one process gives lower overhead and optionally more efficient communication. Components register via `rclcpp_components` macros; a `load_node` service can load a component into a running container | [R02-S02] |
| Lifecycle (managed) nodes | Known state machine: 4 primary states (Unconfigured, Inactive, Active, Finalized), 6 transition states, 7 externally exposed transitions | A managed node is a black box with a known interface; Inactive allows reconfiguration without changing behaviour; hardware acquisition belongs in activate but lengthy hardware initialisation should not; error handling returns to Unconfigured or ends in Finalized; the ROS 2 documentation presents lifecycle nodes as the way to initialise cameras, lidars and motor drivers in a controlled order | [R02-S01, R02-S04] |
| pluginlib | Loads classes from shared libraries at runtime without link-time knowledge | Plugin declared in an XML description file, exported with `PLUGINLIB_EXPORT_CLASS`, instantiated through `ClassLoader::createSharedInstance` | [R02-S03] |
| ros2_control | Hardware components and controllers are pluginlib plugins managed by a Resource Manager and Controller Manager | See 3.2 | [R02-S05] |
| Nav2 | Planner, controller, smoother, behavior and route servers host algorithm plugins selected by name and type at runtime | Plugin type is a pluginlib name; the alias namespaces its parameters (example: a controller aliased `FollowPath` takes `FollowPath.<param>`); all servers are lifecycle nodes with a bond to the lifecycle manager so a crashed server causes the system to be brought down in a controlled way | [R02-S13] |
| RobMoSys / SmartSoft | EU H2020 project advocating model-driven composition and separation of roles between component developers and system builders; tooling in Eclipse SmartMDSD and Papyrus for Robotics | Principles: separation of roles and concerns; composability of building blocks "as is" | [R02-S52, R02-S65] |

**Observations.**

- **[FACT]** The Nav2 interface for a controller plugin is a C++ abstract class `nav2_core::Controller` with explicit `configure`, `activate`, `deactivate`, `cleanup`, `newPathReceived`, `computeVelocityCommands` and `setSpeedLimit` methods [R02-S14]. This shows the typical granularity of a plugin interface in the ROS ecosystem: a lifecycle-shaped class with a small number of semantic operations, not a generic "module" interface.
- **[FACT]** The Nav2 documentation states a design goal that new capability should be addable without forking or modifying the Nav2 repository, via new plugins and new action servers plus a new behavior-tree node plugin [R02-S13]. That is the precedent for "extend without duplicating the platform".
- **[FACT]** Nav2 places costmap layers (lidar, depth, etc.) behind pluginlib, so sensor *processing* is modular, while sensor *drivers* are separate nodes outside Nav2 [R02-S13]. Sensor modularity is therefore realised at two different layers.
- **[FACT]** ROS 2 composition trades fault isolation against overhead as a deployment choice [R02-S02]. For Valtoryn this means the process boundary need not be fixed at design time. **[REC]** Keep every module a composable component with a lifecycle interface so the process layout can differ between a laptop, a simulator and a robot computer.
- **[UNRESOLVED]** Adoption and maintenance status of RobMoSys/SmartSoft tooling in 2026 was not established. The sources I read are a 2020 Eclipse newsletter and a CORDIS project page. What would resolve it: current commit activity and release notes for Eclipse SmartMDSD and Papyrus for Robotics, and independent industrial case studies.

### 3.2 Hardware abstraction and robot description

**ros2_control structure [FACT: R02-S05, R02-S07, R02-S10].**
- The Resource Manager abstracts hardware and its drivers ("hardware components"), loads them with pluginlib, and manages their lifecycle and state/command interfaces. Controllers (derived from `ControllerInterface`) are also plugins. The Controller Manager connects the two sides.
- Three hardware component types exist: Actuator, Sensor, System. Each is described by a `<ros2_control name=... type=...>` block in the URDF, containing a `<hardware>` element with a `<plugin>library/Class</plugin>` and `<param>` children, plus `<joint>`, `<sensor>` and `<gpio>` children with `<command_interface>` and `<state_interface>` elements.
- Interfaces default to type `double`; other types (float32, bool, int8 to int32, uint8 to uint32) are supported through a `data_type` attribute.
- The `<gpio>` tag is deliberately generic and has no standard publisher; a custom controller is needed per application. A `<group>` tag lets related hardware components propagate errors to each other; by default actuator errors are isolated.
- A component implements `on_init`, `on_configure`, `on_activate`, `on_deactivate`, `on_cleanup`, `on_shutdown`, `on_error`, `read` and `write`. Interface exports are generated from the URDF tag by default, with optional "unlisted" interfaces for anything not declared [R02-S10].

**Why this matters for modularity [FACT unless tagged].**
- The same controllers run against different hardware or against mock hardware, because the hardware is reached through named interfaces. A `mock_components/GenericSystem` plugin mirrors commands to states and exists to test the whole pipeline (controllers, launch files, MoveIt integration) without hardware [R02-S11]. The ros2_control documentation lists simulator integrations (Gazebo, MuJoCo, Isaac Sim, Webots, Algoryx AGX, and others) [R02-S12].
- Husarion switches one code base between real robot and simulation with an environment variable (`HUSARION_ROS_BUILD_TYPE=hardware` or `simulation`), and most launch arguments are shared between the two [R02-S50]. This is a second published instance of "simulation is a swap of the hardware layer, not a fork".
- The `controller_manager` has a `fallback_controllers` option and an `enforce_command_limits` option (default true) that clamps commands to limits defined in the robot description [R02-S06]. The robot description is therefore not only documentation; it is an enforced input.

**Limitations that bear directly on modular configurations [FACT].**
- "Reloading of the URDF is not supported yet" and all joints in the `<ros2_control>` tag must exist in the URDF supplied to the Controller Manager [R02-S06].
- A hardware error path ends in FINALIZED and "can not be recovered"; the documented only option is reloading the plugin, and the page states there is no Controller Manager service for that [R02-S09].
- In the INACTIVE state, per the lifecycle page, command interfaces for System/Actuator are described as not available in the semantic sense, but the implementation note says all command interfaces are currently available and will be written; the project plans "safety-critical interfaces" [R02-S08]. This is the documented gap between lifecycle semantics and enforced behaviour.
- `hardware_components_initial_state` lets the Controller Manager start some components unconfigured or inactive, and components without an explicit initial state are activated immediately [R02-S06]. This is a start-up mechanism, not a hot-plug mechanism.
- The Controller Manager's loop defaults to 100 Hz (`update_rate`, read-only) [R02-S06].

**Robot description formats.**
- URDF is an XML format for robot structure, geometry and physical properties in ROS [R02-S64]. Xacro is an XML macro language used to build shorter URDF [R02-S63]. SDFormat is a separate specification with its own versioned releases (the spec site lists versions 1.4 to 1.12), whose elements include world, model, link, joint, sensor and others [R02-S60].
- REP-103 fixes SI units and coordinate conventions [R02-S16]. REP-105 defines frames for mobile platforms, including `base_link`, `odom` and `map`, with `base_link` attached rigidly to the robot base in any position and orientation [R02-S17]. Nav2 requires a `map` to `odom` to `base_link` to sensor-frame tree, with sensor frames relative to `base_link` static and defined in the URDF [R02-S13].
- **[REC]** Treat REP-103 units and REP-105 frames as non-negotiable cross-module conventions in any Valtoryn module manifest, because they are the contract every Nav2-style consumer assumes.

**Vendor precedent for a configuration layer [FACT].**

| | Clearpath (`robot.yaml`) [R02-S47, R02-S48] | Husarion (`components.yaml`) [R02-S49, R02-S51] |
|---|---|---|
| Scope | One file for the whole robot: system (hostname, IP, ROS middleware, namespace), platform (attachments, battery, controller), links (URDF primitives), mounts, sensors | A list of components, each with `type`, `parent_link`, optional `name`, `xyz`, `rpy`, plus type-specific fields; a `custom` type points to a user package/file |
| Identity | `serial_number` is used to determine model and version; a configuration `version` field exists for future schema changes | Component selected by name or historical code; `name` prefixes frames so identical devices do not collide |
| Output | Generators emit `setup.bash`, `robot.urdf.xacro`, SRDF, launch files and parameter files under `/etc/clearpath` | Robot description packages read the config and build the URDF |
| Extension | Sensors are chosen from a vendor inventory of supported sensors; extra links, mounts and `extras` for the rest | `custom` component type |
| Per-module parameters | `ros_parameters` pass-through per sensor | Type-specific extra fields |

**[EST]** Both designs make the *catalogue* the extensibility bottleneck: adding a module type means adding a generator or xacro macro. I did not find independent documentation of how often this blocks users in practice. **[UNRESOLVED]** What would resolve it: issue trackers and community threads for the two repositories.

### 3.3 Capability description precedent

| Precedent | What the description covers | Form | Versioning | Source |
|---|---|---|---|---|
| VDA 5050 v3.0.0 factsheet | Robot type series (kinematics, class, max load, localisation and navigation types, supported zones), physical parameters (speed, acceleration, dimensions), protocol limits (string/array lengths, timing), protocol features (supported or required optional parameters, supported actions with scopes, parameters, blocking types), geometry (wheels, 2D/3D envelopes), load specification, software/hardware versions | JSON; topic `factsheet` is mandatory, sent retained; fleet control can request it with a `factsheetRequest` instant action | `version` field in header `[Major].[Minor].[Patch]`; spec uses SemVer-style rules; MQTT topic carries `v3` major version | [R02-S27] |
| OPC 40010-1 (OPC UA for Robotics Part 1) v1.02 | Motion device systems (industrial and mobile robots, per the joint VDMA/OPC working group [R02-S34]): asset management, condition monitoring and supervision use cases [R02-S31]; `MotionDeviceSystemType` as root, subtype of the OPC UA for Devices `ComponentType`; types for motion devices, controllers, axes, motors, gears, power trains, safety states and task controls | OPC UA information model (type definitions, namespaces) | Spec version 1.02 published 2025-09-08; namespace URI carries model version | [R02-S29, R02-S30, R02-S32, R02-S33] |
| MassRobotics AMR Interoperability Standard | Robots share location, speed, direction, health, tasking/availability and other performance characteristics | JSON schema file plus PDF description and example sender/receiver | Not established from the README alone | [R02-S35] |
| Capabilities2 (community ROS 2 package) | "Interfaces", "providers" and "semantic interfaces" stored as YAML, served by a capabilities server | YAML | Not established | [R02-S54] (weak source: single GitHub repository README) |
| CiA 402 | Drive device profile: finite state automaton, operation modes, control/status words, default PDO mappings | Object dictionary entries and profile documents | Parts carry version numbers (for example CiA 402-1 version 5.0.0) | [R02-S40, R02-S41] |
| Cyphal `uavcan.node.GetInfo` | Protocol version, hardware version, software version, VCS revision, 128-bit unique ID, reverse-domain name, optional software image CRC, optional certificate of authenticity | DSDL data type; must be static while node runs | Versioned data type | [R02-S36] |
| EtherCAT SII + ESI | SII is non-volatile device memory with basic features; ESI is an XML file describing process data, mappings, mailbox protocols and sync modes; ENI is a network configuration export | EEPROM + XML | Not examined | [R02-S42] |

**Observations from the VDA 5050 factsheet design** (the closest domain match):
- **[FACT]** The factsheet states that some values can only be specified during system integration (for example project-specific load assignment) and that the document is intended to be both human-readable and machine-processable [R02-S27]. So a manifest has two authors: the vendor and the integrator.
- **[FACT]** Optional protocol features are gated by capability: a robot that cannot process an optional field must reject the order with error type `UNSUPPORTED_PARAMETER` at level `CRITICAL`, and fleet control must only send what the robot supports [R02-S27]. This is a concrete "declare, then refuse mismatch" contract.
- **[FACT]** Several enumerations are *extensible* (for example `mobileRobotKinematics` lists DIFFERENTIAL, OMNIDIRECTIONAL, THREE_WHEEL and permits further values) [R02-S27]. This directly demonstrates that a warehouse-domain standard does not restrict kinematics to differential drive, which aligns with the project's requirement not to limit the product to one chassis.
- **[FACT]** The factsheet has a `mobileRobotConfiguration` object with software and hardware versions as key/value pairs [R02-S27]. Note this is a loose key/value map, not a typed compatibility declaration.
- **[FACT]** VDA 5050 v3.0.0 was released on GitHub on 2026-03-18 [R02-S28]. The document states a SemVer-style policy: major bumps for breaking changes such as new non-optional fields, minor for new features such as an added optional parameter, patch for corrections [R02-S27].

**Observations on conformance reliability.**
- **[FACT]** CiA states that CiA 402 is among the best-specified motion-control profiles, but its multitude of optional functions limits exchangeability, and some vendors implement only a subset while claiming conformity [R02-S40].
- **[FACT]** A 2022 ROS Discourse working-group proposal thread contains a participant's account that hardware vendors often interpret common message semantics in their own way, making integration costly [R02-S53]. This is anecdotal, from one forum participant, and is a weak source.
- **[REC]** A Valtoryn capability manifest should distinguish *declared* capability from *verified* capability, record how and when verification occurred, and fail closed on mismatch (Sections 5.4 and 7.4).

### 3.4 Module identification and plug-and-play

| Mechanism | Identity carried | Discovery / assignment | Notable constraints | Source |
|---|---|---|---|---|
| Raspberry Pi HAT ID EEPROM | EEPROM header signature and version; "atoms": vendor info (UUID, product ID, product version, vendor string, product string), GPIO map, device-tree blob, custom data; CRC-16 per atom | Read over dedicated pins (ID_SC, ID_SD) which must be used only for the EEPROM | Spec marked preliminary; repository is marked deprecated with utilities moved elsewhere; UUID mandated per board "ever made" to detect two identical boards stacked | [R02-S38, R02-S39] |
| USB | Device descriptor: `idVendor`, `idProduct`, `bcdDevice`, `bcdUSB`; class code triple (base class, subclass, protocol) in device or interface descriptors | Enumeration on attach; class codes identify function and nominally select a driver; a vendor-specific class exists | Device descriptor must not change during a connection | [R02-S45, R02-S46] |
| Cyphal | Node-ID (unique in network), GetInfo (128-bit UID, name, versions); reverse-domain node name | Manual node-ID assignment, or optional plug-and-play allocation protocol using anonymous messages, derived from a consensus algorithm | Spec states deterministic/robust applications are unlikely to benefit from plug-and-play; UID all-zeros invalid | [R02-S36] |
| DroneCAN | DNA (dynamic node allocation) for CAN node IDs, inherited from UAVCAN v1 protocol line | Dynamic allocation | Project lists a future "node capability message" so the DNA server can learn hardware and software capabilities; this suggests DroneCAN v1 has no standard one [EST, inference from the roadmap wording] | [R02-S37] |
| EtherCAT | SII EEPROM + ESI XML; MainDevice can address by position at boot and compare actual topology with the planned one; then assigns fixed addresses | Boot-time topology scan; Hot Connect Groups allow segments to be attached/detached during operation | Documented for modular machines and tool changers; cited limit of 65,535 devices per segment | [R02-S42] |
| CANopen | Object dictionary with 16-bit indices: 1000h-1FFFh communication, 2000h-5FFFh proprietary, 6000h-9FFFh standardised parameters; device and application profiles | Profiles enable "plug and play" for conforming devices; manufacturer-specific functions still permitted | See conformance caveat for CiA 402 | [R02-S41, R02-S40] |
| micro-ROS | MCU nodes using rcl + rclc; no dynamic allocation after initialisation; agent bridges to the ROS 2 graph; lifecycle concepts available | Node graph discovery via the agent | Micro XRCE-DDS middleware; project site has moved to micro.vulcanexus.org | [R02-S44] |

**Observations.**
- **[FACT]** Identity precedents split into two kinds: (a) *what is this unit* (UUID, serial number, UID) and (b) *what kind of thing is this and what can it do* (product ID, class codes, device profiles, ESI, GetInfo name). The HAT spec explicitly separates a per-unit UUID from product ID and version [R02-S38]; Cyphal separates UID from name and versions [R02-S36].
- **[FACT]** Several precedents add a *signature* option: Cyphal's GetInfo includes an optional software image CRC and certificate of authenticity [R02-S36]. No precedent I read mandates cryptographic verification of module identity.
- **[UNRESOLVED]** Whether ROS 2 itself offers a standard for hardware-module identity beyond node names and parameters. I found no such standard in the documents inspected. What would resolve it: the ROS Hardware Interface working-group outputs (the 2022 proposal thread is the only trace I read) and REP index review.
- **[EST]** For Valtoryn's first reference robot the practical identity problem is small (a handful of USB/Ethernet/CAN devices on one computer). The HAT EEPROM and Cyphal GetInfo patterns matter once modules are electrically swappable by people other than the integrator.

### 3.5 Versioned APIs and compatibility

**Package and distribution level [FACT].**
- Semantic Versioning 2.0.0: MAJOR for incompatible API changes, MINOR for backward-compatible functionality, PATCH for backward-compatible fixes; 0.y.z is initial development where anything may change [R02-S26].
- ROS 2 Developer Guide adds: no major version increments inside a released distribution; compiled-code ABI is part of the public interface and a change requiring recompilation of dependents is major; deprecations cannot be added after a release [R02-S20]. ROS distributions aim to limit changes after release to bug fixes and non-breaking improvements for core packages, with looser expectations for higher-level packages [R02-S21].
- REP-2004 defines package quality levels; Level 1 requires a version policy, a stable version (>= 1.0.0 for SemVer), a strictly declared public API, and policies for API and ABI stability; Level 3 relaxes these; for Level 4 the version-policy item has no requirements [R02-S15].
- REP-149 package manifests can express dependency ranges with `version_lt`, `version_lte`, `version_eq`, `version_gte`, `version_gt` attributes [R02-S18]. This is a ready-made syntax for compatibility ranges.
- Release cadence and support (REP-2000): new releases every 12 months; LTS releases supported about 5 years, matching Ubuntu LTS [R02-S19]. Current table (ROS 2 documentation): Lyrical Luth released 2026-05-22, supported until May 2031; Kilted Kaiju released 2025-05-23, end of life December 2026; Jazzy Jalisco released 2024-05-23, end of life May 2029; Humble Hawksbill released 2022-05-23, end of life May 2027 [R02-S21]. Lyrical is described as an LTS release [R02-S22].
- **Discrepancy between sources.** REP-2000 labels Kilted as May 2025 to November 2026 [R02-S19], whereas the ROS 2 distribution table gives December 2026 [R02-S21]. REP-2000 as read does not mention Lyrical at all. **[REC]** Treat the distribution table in the ROS 2 documentation as authoritative and the REP text as lagging, but re-check before fixing any support date in a Valtoryn document. **[CALC]** Lyrical support span: May 2026 to May 2031 is about 5 years, consistent with the REP-2000 LTS rule (inputs: R02-S21, R02-S19).

**Interface level [FACT].**
- ROS 2 interfaces (msg, srv, action) are described in an IDL-like text format and generated into several languages [R02-S23]. Since Iron, ROS 2 computes a type hash (RIHS01) from the type description: map description to JSON (skipping default values), SHA-256 of the exact text, prefix "RIHS01_" plus hex, giving a fixed-length 71-character string [R02-S24]. **[CALC]** 71 = 7 (prefix "RIHS01_") + 64 (hex of a 256-bit digest at 4 bits per character); inputs from R02-S24.
- Type hashes are exposed in endpoint discovery and a per-node `get_type_description` service exists, enabled by default in Iron, so peers can detect and inspect mismatches [R02-S24, R02-S25]. The 2023 slides list "automatic hash-mismatch detection" and enum/constant handling as not yet done, and "evolved type translation" as a long-term plan with delivery to be determined [R02-S24]. **[UNRESOLVED]** Current (2026) status of these items; what would resolve it: Lyrical release notes and the rosidl/rcl issue trackers. The Lyrical release notes I read do not mention type-translation features but do add `rosidl::Buffer` zero-copy support for `uint8[]` fields [R02-S22].
- Cyphal's rules for data type evolution are the most explicit I found: each type has major and minor version; all definitions sharing name and major version must be semantically compatible; released definitions are immutable except whitespace/comment/deprecation marker; major version 0 has no compatibility requirement; minor increments follow in sequence [R02-S36]. Cyphal also defines implicit zero-extension and truncation rules so nodes with different minor versions can interoperate [R02-S36].
- VDA 5050 puts the major version in the MQTT topic path (`vda5050/v3/...`) and a `[Major].[Minor].[Patch]` version string in each message header [R02-S27].
- DroneCAN states that evolution should retain compatibility with existing devices and plans mechanisms for extending messages compatibly [R02-S37].

**Takeaways.**
- **[REC]** Adopt SemVer 2.0.0 for every versioned artifact Valtoryn defines (platform release, module manifest schema, Valtoryn-defined interfaces, module packages) and adopt the ROS rules "no breaking change inside a released line; ABI counts" for its own stable lines.
- **[REC]** Do not rely on type hashes alone for compatibility. A hash detects *any* change (including harmless ones); SemVer ranges express *intended* compatibility. Use both: ranges for planning, hashes for runtime assertion.

### 3.6 Lifecycle, hot-plug and configuration management

| Concern | Precedent | What it implies | Source |
|---|---|---|---|
| Start-up ordering | ROS 2 lifecycle: configure then activate; launch/lifecycle manager checks all components instantiate correctly before any begins behaviour | Gate activation on successful configure of every required module | [R02-S01] |
| Controlled degradation | Nav2 lifecycle manager with a "bond" so that a crashed server triggers controlled system transition down | Module liveness is part of the lifecycle contract | [R02-S13] |
| Hardware states | ros2_control: UNCONFIGURED (initialised, no communication), INACTIVE (communication up, state readable), ACTIVE (power circuits active, commands sent), FINALIZED (unrecoverable) | Mirror the same four-state model for every Valtoryn module | [R02-S08, R02-S09] |
| Recovery | Failed hardware ends in FINALIZED; reload plugin is the only way; no CM service | Recovery needs a supervisory restart at process level | [R02-S09] |
| Change of hardware set | URDF reload unsupported | Treat "robot configuration" as an input fixed at bring-up | [R02-S06] |
| Topology change in the field | EtherCAT Hot Connect Groups for modular machines/tool changers; MainDevice compares planned vs actual topology at boot | Hot connect is a fieldbus-level feature with a *planned topology* reference | [R02-S42] |
| Network joins | Cyphal plug-and-play allocation optional; node-ID otherwise assigned by integrator | Dynamic join is opt-in, with determinism trade-off | [R02-S36] |
| Config regeneration | Clearpath regenerates URDF, launch and parameters from `robot.yaml`; a config `version` exists | Treat the config as source, derived files as build artifacts | [R02-S47, R02-S48] |
| Maintenance-time reconfiguration | ROS 2 Inactive state exists so a node can be reconfigured without altering behaviour while running | Reconfiguration windows map to Inactive | [R02-S01] |

**Observation [EST].** The documented mechanisms support three distinct reconfiguration classes with sharply different risk: (a) *cold* (stop, change config, regenerate, restart), well supported everywhere; (b) *warm* (module-level lifecycle cycle of a non-safety node), supported by lifecycle but not by ros2_control for hardware set changes; (c) *hot* (module physically attached or detached while the robot runs), supported at fieldbus level (EtherCAT, Cyphal PnP) but not at the ROS control-framework level in the documentation I read.

### 3.7 Mechanical and electrical modular interface precedent

- **[FACT]** ISO 9409-1:2004 defines main dimensions, designation and marking for a circular plate as mechanical interface, intended to ensure exchangeability and orientation of hand-mounted end effectors; it does not define other requirements of the end-effector coupling device and does not correlate load-carrying ranges. It was last confirmed in 2023 [R02-S55]. Full text not inspected.
- **[FACT]** Tool-changer vendors build on that flange: Zimmer states direct mounting using a flange according to EN ISO 9409-1 and describes energy elements transmitting pneumatics, vacuum, signal, load current and communication [R02-S61]; ATI lists direct mounting to ISO 9409-1-40-4-M6 and -50-4-M6 patterns, utility pass-through, and swappable utility modules [R02-S62]. The pattern: a standard *mechanical* interface, plus vendor-specific *utility* modules for power, signals and fluids.
- **[FACT]** Raspberry Pi's HAT specification combines a mechanical specification (size, minimum 8 mm spacing), power rules (back-powering at least 1.3 A continuous required if back-powering) and an identification EEPROM, and states that only boards meeting all rules may be called HATs, while a board with only the EEPROM may claim GPIO autoconfiguration [R02-S39]. This is a worked example of *tiered conformance labels*.
- **[FACT]** Clearpath exposes mounting as catalogued, generic mount structures (brackets, risers, posts, pivots) with a parent mount and xyz/rpy offsets in the config [R02-S47]; Husarion components attach to a named parent link with xyz/rpy [R02-S49]. Mechanical modularity is encoded in the description as *frames and offsets*.
- **[FACT]** Warehouse-domain standards describe vehicles at the level of kinematics, wheel geometry, envelopes and load handling devices (VDA 5050 factsheet) rather than at a mechanical-interface level [R02-S27].
- **[UNRESOLVED]** Whether any public, vendor-neutral mechanical interface standard for AMR payload decks, battery trays or sensor mounts exists comparable to ISO 9409-1 for arm flanges. I did not find one in this search. What would resolve it: a search of ISO/TC 110 and TC 299 catalogues and of A3/VDMA/VDA publications.

### 3.8 Safety implications of modularity

What public sources establish:
- **[FACT]** ISO 3691-4:2023 specifies safety requirements and verification for driverless industrial trucks and their systems, with AMRs and AGVs named as examples; it applies across the truck's life phases for significant hazards listed in an annex; operating-zone preparation is addressed in an annex. The catalogue page says it is expected to be replaced by a draft (ISO/DIS 3691-4) within months [R02-S56]. Full text not inspected.
- **[FACT]** ISO 13849-1:2023 gives a methodology for design and integration of safety-related parts of control systems, including software, for high-demand and continuous modes; it does not specify which safety functions or performance levels apply, and does not provide measures for security, noting that security can affect safety functions [R02-S57]. Full text not inspected.
- **[FACT]** IEC 61508-1:2010 is a basic safety publication on E/E/PE safety-related systems; its catalogue lists a stability date of 2027 and a revision in preparation [R02-S58]. Full text not inspected.
- **[FACT]** ANSI/A3 R15.08 now has three parts; Part 3 (2026) is described as covering risk assessment, management of change, training and periodic inspection for IMR applications in use (secondary press source) [R02-S59].
- **[FACT]** Safety over EtherCAT uses a "black channel" where the transport is not considered safety-relevant, is standardised in IEC 61784-3 and suitable up to SIL 3, and the ETG states it permits flexible modification and expansion of the safety architecture [R02-S43]. CiA 402-4 defines safety parameters and SRDOs for drives based on a generic safety drive profile [R02-S40].
- **[FACT]** ros2_control documentation: command interfaces are currently all available in INACTIVE, and safety-critical interfaces are planned, not delivered [R02-S08]; `allow_controller_activation_with_inactive_hardware` defaults to false and the documentation recommends against enabling it for safety reasons [R02-S06].

What I infer (not established by the sources):
- **[EST]** Each of the four mechanism families (identity, manifest, plugin loading, hot-plug) can alter the *safety case*: swapping a lidar changes protective-field geometry and latency; swapping a drive changes stopping distance; swapping a controller plugin changes software on the path of a safety function. The cited standards frame safety as validated functions plus managed change, so a modular platform needs a rule for *which* configuration changes invalidate which validation evidence.
- **[EST]** The ROS control stack as documented is not a safety-rated channel. Safety functions would likely live in separate certified hardware or firmware (for example safety PLC/relay or safety-rated drive functions), with the modular software platform consuming their state. The safety architecture workstream must decide this; the dependency here is that the manifest must be able to *reference* safety-function evidence per module without pretending to provide it.
- **[EST]** Capability data used by safety-adjacent logic (max speed, stopping distance, envelope, sensor latency) should be treated as safety-relevant data with change control, versus informational data.

---

## 4. Layers of modularity

I distinguish six layers because they have different rates of change, different failure modes and different standards.

| Layer | What varies across robot configurations | Candidate mechanism (precedent) | Dynamic swap realistic? | Evidence strength |
|---|---|---|---|---|
| Software (compute) | Algorithms (planner, controller, localisation), drivers, task logic | ROS 2 composable lifecycle nodes; pluginlib plugins (Nav2, ros2_control) | Warm (lifecycle cycle) yes; process restart for plugin reload | Strong [R02-S01, R02-S02, R02-S03, R02-S13] |
| Hardware abstraction | Motor drives, encoders, IMUs, grippers, IO | ros2_control hardware components and named interfaces; URDF `<ros2_control>` tags | Not at runtime per docs (no URDF reload) | Strong for static, weak for dynamic [R02-S06, R02-S07] |
| Description / configuration | Kinematic structure, frames, sensor placement, parameters | URDF/Xacro generated from a robot config (Clearpath, Husarion) | Cold regeneration | Moderate (two vendors, no independent evaluation) [R02-S47, R02-S49] |
| Communication / electrical | Buses (CAN, EtherCAT, Ethernet, USB), power rails, connectors | Identity EEPROM (HAT), USB descriptors, Cyphal/DroneCAN, EtherCAT SII/ESI and Hot Connect | Possible at bus level; policy decision | Strong for each bus individually [R02-S36, R02-S38, R02-S42, R02-S46] |
| Mechanical | Chassis, wheel/locomotion module, payload deck, sensor mounts, tool/gripper flange | ISO 9409-1 for arm flanges and tool changers; mounts as frames in description; no vendor-neutral AMR standard found | Manual swap by trained staff | Strong for flange, [UNRESOLVED] for AMR modules [R02-S55] |
| Safety | Safety sensors, e-stop chain, safety functions, validation evidence | ISO 3691-4 / ISO 13849-1 / IEC 61508 process; safety fieldbus black channel; change management | Not appropriate to treat as plug-and-play without re-validation | Standards framing only, full text not read [R02-S56 to R02-S59] |

**[REC]** Make *layer separation* a design rule: a module's manifest declares what it provides and requires at each layer, and no layer's compatibility rule is allowed to be implicit in another (for example, "this lidar fits because the mount happens to be the right size" is a mechanical fact that must be in the mechanical declaration, not inferred from the sensor driver).

---

## 5. Design space: mechanisms, trade-offs, failure modes

### 5.1 Module identity

| Option | Description | Pros | Cons / failure modes | Evidence |
|---|---|---|---|---|
| I1. Configuration-only identity | Names and IDs live only in the robot config file (Clearpath-style serial number) | Zero hardware cost; fits cold reconfiguration | Config drifts from reality; wrong module attached with no detection | [R02-S47] |
| I2. Config identity + boot-time enumeration check | Config declares expected modules; at bring-up, drivers read vendor/product/serial (USB descriptor, CAN/EtherCAT identity, GetInfo-like) and compare | Catches wrong or missing module; maps onto EtherCAT "planned vs actual topology" idea | Needs each driver to expose identity; modules without identity need alternatives | [R02-S42, R02-S46, R02-S36] |
| I3. On-module ID memory | Small EEPROM (HAT-style atoms with UUID, product ID, version, CRC) on each Valtoryn-designed module | Works for dumb modules; per-unit serial; self-describing | Valtoryn must specify a format and tools; EEPROM contents can be wrong or stale; spec stability concern (HAT format marked preliminary and repo deprecated) | [R02-S38, R02-S39] |
| I4. Dynamic ID allocation (PnP) | Cyphal/DroneCAN-style allocation of bus IDs | Hands-free join | Spec itself warns about determinism; extra attack/failure surface | [R02-S36, R02-S37] |

**[REC]** Start with I1 + I2 (software-first, cheap), reserve I3 as the electrical-layer format for Valtoryn-designed modules once hardware exists, and avoid I4 until there is a concrete need. Separate *unit identity* (serial/UUID) from *type identity* (reverse-domain module type name and version), as HAT and Cyphal both do.

### 5.2 Capability manifest

| Option | Pros | Cons / failure modes | Evidence |
|---|---|---|---|
| M1. No manifest; capabilities implicit in URDF, ros2_control tags and parameters | No duplication; nothing new to maintain | No cross-module compatibility check; cannot answer "can this robot do task X" without reading launch code; fleet integration must be hand-written | [R02-S07] |
| M2. Hand-written YAML/JSON manifest per module and per robot | Simple; reviewable | Duplicates URDF/limits; drifts; unverified claims (CiA 402 pattern) | [R02-S40] |
| M3. Manifest generated from authoritative sources plus a small hand-authored part | Single source of truth for geometry/limits; manifest cannot contradict the description | Generator and schema to maintain; some capabilities cannot be derived | Pattern echoed by Clearpath generators [R02-S48] |
| M4. OPC UA-style information model | Standard, tooling, namespaces, type system; industrial integration | Heavy; Part 1 targets vertical integration/monitoring (read-only default), not on-robot module composition | [R02-S30, R02-S32] |
| M5. VDA 5050 factsheet as the *external* face | Directly consumable by VDA 5050 fleet controllers; mandatory topic | Describes the whole robot type series, not module-level composition; free-text and extensible enums | [R02-S27] |

**[REC]** M3 for module- and robot-level manifests, with M5 as a *projection* (a generated export of the robot manifest into a VDA 5050 factsheet, if and when the fleet workstream chooses VDA 5050). Treat M4 as an optional later export. M2 as the sole mechanism is the failure case to avoid.

### 5.3 Versioning

| Axis | Option | Notes |
|---|---|---|
| Manifest schema | SemVer in a `schema_version` field; breaking changes bump major (VDA 5050 and Cyphal both use major/minor/patch semantics) | [R02-S27, R02-S36] |
| Module version | SemVer per module package; plus optional build identity (VCS hash, image CRC) like Cyphal GetInfo | Distinguishes "same version, different build" [R02-S36] |
| Interfaces | SemVer plus pin to ROS type hash for runtime assertion; follow Cyphal rule "same name + same major = semantically compatible" for Valtoryn-defined types | [R02-S24, R02-S36] |
| Dependency ranges | Reuse REP-149 `version_gte`/`version_lt` semantics in the manifest `requires` | [R02-S18] |
| Platform | One ROS 2 LTS line at a time; Valtoryn releases pinned to it | [R02-S21] |

**Failure modes.**
- Version-number inflation without enforcement (REP-2004 Level 3 packages need not declare API) [R02-S15]. **[REC]** enforce by tests, not by policy text.
- ABI breaks: plugins built for one ROS distribution do not load safely in another [R02-S20 states ABI is public interface; inference for plugins is EST]. **[REC]** record the ROS distribution and rmw in the module manifest.
- Hash mismatch false alarms: the hashing procedure skips default values and hashes a description that includes field names and types [R02-S24], so a harmless default change does not alter the hash while a cosmetic field rename would (the rename case is inferred, [EST]). Hashes are a tripwire, not a compatibility oracle.

### 5.4 Compatibility checking

| Level | When | What is checked | Precedent |
|---|---|---|---|
| C1. Schema validation | Authoring / CI | Manifest conforms to schema; units; required fields | VDA 5050 JSON schemas published for validation [R02-S27] |
| C2. Static resolution | Config build (generation time) | All `requires` satisfied by some `provides`; version ranges; frames exist; mount points occupied once; interface names unique per REP-style namespace | package.xml ranges [R02-S18]; ros2_control joints must exist in URDF [R02-S06] |
| C3. Bring-up verification | Each start | Observed identity equals declared identity; firmware within range; interface type hashes match | EtherCAT planned vs actual topology [R02-S42]; Cyphal GetInfo [R02-S36] |
| C4. Runtime monitoring | While running | Liveness (bond), diagnostics, limit enforcement | Nav2 bond [R02-S13]; CM command-limit enforcement [R02-S06] |
| C5. Safety re-validation gate | On change of safety-relevant fields | Config hash of safety-relevant subset compared with the hash recorded in the validation record | Management-of-change framing in R15.08-3 description [R02-S59]; no software precedent found |

**[REC]** Fail closed at C3: if declared and observed disagree for a module that is on a motion or safety path, refuse to activate. Mismatch on an informational payload may degrade with a warning.

### 5.5 Plugin loading

| Option | Pros | Cons |
|---|---|---|
| P1. In-process pluginlib plugins (ros2_control, Nav2 style) | Low latency; shared costmap/TF objects (Nav2 cites the cost of duplicating costmaps) [R02-S13]; established pattern | Shared fate in one process; must match ROS distro ABI; documented `handle_exceptions` covers thrown exceptions, not memory faults (the latter is EST) [R02-S06] |
| P2. Out-of-process component nodes with lifecycle and ROS interfaces | Fault isolation; independent versioning; language freedom | Serialisation and scheduling overhead; more processes to supervise [R02-S02] |
| P3. Composable node chosen at deploy time (P1 or P2 per configuration) | Process layout is a deployment decision | Two test configurations to maintain [R02-S02] |
| P4. Custom Valtoryn plugin system | Could add manifest checks at load time | Duplicates pluginlib; no evidence of need; extra maintenance |

**[REC]** P3 using standard pluginlib and rclcpp_components; no custom plugin loader. Put the manifest check in the launch/bring-up path *before* the plugin is loaded, not inside a new loader.

### 5.6 Configuration management

- **[REC]** The robot configuration is source; URDF/xacro, launch files, controller YAML and manifest exports are generated build artifacts (Clearpath pattern [R02-S48]). Configuration includes a `version`/schema field [R02-S47].
- **[REC]** A configuration has a content hash recorded at commissioning; a second hash covers the safety-relevant subset (Section 5.4, C5).
- **[REC]** Simulation vs hardware is a swap at the hardware-abstraction layer driven by the same configuration (Husarion build-type pattern [R02-S50], ros2_control mock/simulator integrations [R02-S11, R02-S12]).

### 5.7 Failure-mode catalogue

| # | Failure mode | Layer | Likelihood/impact (EST) | Mitigation direction |
|---|---|---|---|---|
| F1 | Manifest claims capability module lacks (declared vs verified) | Manifest | High likelihood in multi-vendor setups (CiA 402 experience), variable impact | Verification step C3; "verified-by/at" metadata |
| F2 | Duplicate sources of truth (limit in URDF and manifest disagree) | Description | High if M2 chosen | Generate manifest from description (M3) |
| F3 | Catalogue bottleneck: adding a module needs generator work | Config | Medium | Escape hatch like Clearpath links/extras and Husarion `custom` type, with explicit "unvalidated" flag |
| F4 | Plugin ABI mismatch after ROS update | Software | Medium | Pin distro; manifest records distro and rmw |
| F5 | Hardware component in FINALIZED needs plugin reload, no service | HAL | Medium | Supervisor restarts the control process; test the recovery path |
| F6 | Wrong module attached after maintenance | Electrical/mech | Medium | C3 identity check; physical keying |
| F7 | Hot-plug of a module on a motion path during operation | Electrical/safety | Low frequency, high impact | Policy: forbidden for safety-relevant modules (Section 7.5, R16) |
| F8 | Config change silently invalidates safety validation | Safety | Medium | C5 gate; change records |
| F9 | Over-engineering the manifest (model-driven heavy tooling) delays first robot | Process | Medium | Phase plan (Section 7.8); no M4 initially |
| F10 | Type-evolution mismatch between old module and new platform | Interfaces | Medium | SemVer ranges plus hash check; Cyphal-style immutable released types |
| F11 | Identity spoofing or tampered module firmware | Security | Unknown | Optional signing (Cyphal GetInfo has fields); security workstream decision |

---

## 6. Evaluation of the layered approach against alternatives

**Candidate under test (C).** A layered scheme: (1) a declarative *robot configuration*; (2) *capability manifests* per module and per robot; (3) a *hardware abstraction layer* based on ros2_control and standard ROS interfaces; with generators producing description and launch artifacts.

**Alternatives.**
- **A. Per-robot forks or branches.** Each robot configuration is a copy of the platform with changes.
- **B. ROS-native only.** Xacro arguments, launch files and parameter YAML plus ros2_control; no manifest or generator.
- **D. Model-driven composition (RobMoSys-style).** Formal component and system models with toolchain generation.
- **E. Runtime self-describing modules.** Modules announce identity and capability on attach, system self-assembles (Cyphal PnP, USB-like).

| Criterion | A. Forks | B. ROS-native only | C. Layered config + manifest + HAL | D. Model-driven | E. Runtime self-describing |
|---|---|---|---|---|---|
| Avoids duplicating platform software | No: duplication is the definition | Yes | Yes | Yes | Yes |
| Evidence of working in production | Common in practice (not evidenced here) | Strong: standard ROS practice [R02-S05, R02-S13] | Moderate: two vendor frameworks [R02-S47, R02-S49] and VDA 5050 factsheet [R02-S27] | Weak/unresolved adoption [R02-S52] | Strong at fieldbus level [R02-S36, R02-S42]; no evidence at ROS control-framework level |
| Compatibility checking before runtime | No | Limited (ros2_control joint presence check, package.xml ranges [R02-S06, R02-S18]) | Yes (C1-C3) | Yes | Runtime only |
| Fleet/warehouse capability exposure | Hand-built | Hand-built | Natural (manifest export to factsheet) | Possible | Possible |
| Fit with ros2_control's static hardware set | Fine | Fine | Fine (cold regeneration) | Fine | Poor: no URDF reload [R02-S06] |
| Safety-change control | Per-fork, ad hoc | Ad hoc | Can be designed in (C5) | Possible | Hardest: runtime change of safety-relevant set |
| Up-front cost | Lowest | Low | Medium | High | High |
| Main risk | Divergence, security patches multiplied | No single place for capability and compatibility knowledge | Manifest/description drift if not generated or validated; catalogue bottleneck | Toolchain lock-in, learning curve | Determinism and safety risks; complexity |

**Honest assessment** [REC]:
1. **A is rejected** for the stated requirement; no evidence suggests it scales, and the project goal is explicit about avoiding duplication.
2. **B is the correct foundation, not a competitor.** Everything in C either builds on B's artifacts (URDF, ros2_control tags, parameters) or generates them. A first robot can be brought up with B alone.
3. **C adds value over B only where B has a documented gap:** compatibility checking across modules, capability queries for fleets, and change control. The evidence for that gap is partly indirect: the factsheet mandate in VDA 5050, the vendor config layers, and the declared-vs-real conformance experience. I found no study quantifying integration time saved by a manifest. **[UNRESOLVED]** What would resolve it: a pilot with two configurations and a measured count of manual edits per configuration change.
4. **The main way C fails is drift.** If manifests are hand-written (M2), they will contradict the URDF and ros2_control tags, and the system will have created two sources of truth. This is why Section 5.2 recommends generation (M3).
5. **D is deferred.** Its principles (separation of roles, composition with explicit properties) are useful as design vocabulary [R02-S52], but I could not establish current adoption or maintenance, and its toolchain cost is high for a project whose first deliverable is one differential-drive AMR.
6. **E is deferred and restricted.** It is valuable for electrical-layer identity (I2, I3) but not for run-time assembly of motion-path modules, given the ros2_control static hardware set [R02-S06], Cyphal's own caution [R02-S36], and the safety argument in Section 3.8.

**Recommended position:** B as foundation, C as a *thin* layer on top, E only as boot-time identity verification, D as vocabulary only.

---

## 7. Implications and recommendations for Valtoryn

All items in this section are proposals [REC]; none is implemented.

### 7.1 Architectural principles

- **R1. Layer-separated modularity.** Declare compatibility per layer (software, hardware abstraction, communication/electrical, mechanical, safety). No layer relies on implicit assumptions from another (Section 4).
- **R2. ROS-native first.** Use composable lifecycle nodes, pluginlib, ros2_control hardware components and standard REP conventions (REP-103 units, REP-105 frames). Do not build a parallel module runtime. Basis: [R02-S01, R02-S02, R02-S03, R02-S05, R02-S16, R02-S17].
- **R3. Every module has a lifecycle contract.** All Valtoryn modules (drivers, perception, planners) are managed nodes or ros2_control components with the four primary states and a liveness bond, and a documented behaviour on failure. Basis: [R02-S01, R02-S08, R02-S13].
- **R4. Separate "robot" from "platform".** The platform repository contains no robot-specific constants. Robot-specific content lives in robot configuration packages (configuration + module selections), so adding a robot type adds data and perhaps new module packages, not platform forks.

### 7.2 Robot configuration (proposal)

- **R5. One declarative robot configuration per robot variant** (Clearpath/Husarion pattern), containing: schema version; robot identity (serial, variant); list of module instances (type, version range, instance name, parent frame, pose, parameters); communication endpoints; simulation vs hardware profile; references to safety evidence. Generators produce URDF/xacro, ros2_control hardware sections, controller and Nav2 parameter files, and launch files. Basis: [R02-S47, R02-S48, R02-S49, R02-S50].
- **R6. Generated files are artifacts.** Never hand-edited; build fails if they differ from the generator output. Basis: [R02-S48] pattern; enforcement is my addition.
- **R7. Provide an explicit escape hatch** for unsupported hardware (Husarion `custom`, Clearpath links/extras analogue), marked "unvalidated" in the manifest so it is visible to compatibility and safety gates. Basis: F3.
- **R8. Locomotion and chassis are modules.** Model the drive (differential, omni, steered, legged, etc.) as a ros2_control System component plus a kinematics description in the manifest; the controller plugin and the kinematic parameters vary, the platform does not. VDA 5050's extensible kinematics enumeration is the warehouse-domain precedent [R02-S27]. This is a design direction; no kinematics other than differential drive is claimed to be implemented.

### 7.3 Capability manifest (proposal)

- **R9. Manifest content** (field names illustrative): `manifest_schema_version` (SemVer); `module_type` as a reverse-domain name (Cyphal naming convention [R02-S36]); `module_version` (SemVer) plus optional build identity; `provides[]` and `requires[]` with versions/ranges (REP-149 style [R02-S18]); ROS interfaces with type names and pinned type hashes [R02-S24]; ros2_control interface names with units (REP-103 [R02-S16]) and limits; frames following REP-105 [R02-S17]; mount declarations (parent frame, mount type, occupied mount points); hardware identity expectations (vendor, product, firmware range); ROS distribution and rmw; `verification` block (who/when/how); `safety` block referencing evidence IDs and declaring "no safety claim" explicitly when none; extensible enumerations like VDA 5050 [R02-S27].
- **R10. Generate rather than duplicate** (M3): limits and geometry are read from the description/ros2_control tags; the hand-written part is only what cannot be derived (task capabilities, payload classes, supported actions).
- **R11. External exports are projections.** If the fleet workstream adopts VDA 5050, the robot-level manifest exports to a factsheet [R02-S27]; if OPC UA is required, export to OPC 40010-1 types [R02-S33]. Do not make either the internal format.

### 7.4 Compatibility, versioning and plugin loading

- **R12. Compatibility pipeline C1 to C5** (Section 5.4) with C3 failing closed for motion-path or safety-path modules.
- **R13. SemVer everywhere**, with the ROS rule that no major bump occurs within a released Valtoryn line, and ABI counts as public interface for compiled plugins [R02-S20, R02-S26]. Valtoryn-defined interfaces follow Cyphal-style immutability once released [R02-S36].
- **R14. Target one ROS 2 LTS** and record it in manifests. From the facts in 3.5: Humble ends May 2027, Jazzy May 2029, Lyrical May 2031, Kilted (non-LTS) December 2026 [R02-S21]. Selection is an owner decision (Section 8, Q1).
- **R15. Plugin loading via standard mechanisms** only (pluginlib, rclcpp_components), with manifest checks before load (Section 5.5, P3).

### 7.5 Hot-plug and reconfiguration policy

- **R16. Tiered policy.** Tier 0: cold reconfiguration only (default for everything on a motion or safety path). Tier 1: warm module lifecycle cycling for non-safety payloads while the robot is stationary and in a maintenance state. Tier 2: true hot-plug of non-safety, non-motion payloads, only for modules whose identity can be verified at attach. Tier 3: hot-plug of anything on a safety path is prohibited unless a future safety architecture explicitly supports it. Basis: [R02-S06, R02-S09, R02-S36, R02-S42] and Section 3.8; the tier boundaries are my judgement.
- **R17. Test recovery paths** (FINALIZED hardware, plugin reload, supervisor restart) in simulation and on the first hardware, since the control framework offers no reload service [R02-S09].

### 7.6 Electrical and mechanical modularity

- **R18. Mechanical modularity progressively**: first express mounts as frames and catalogued mount types in the description (Clearpath/Husarion pattern [R02-S47, R02-S49]); for arms or grippers use ISO 9409-1 interfaces [R02-S55]; define Valtoryn's own AMR payload/sensor mount specification only when a physical design exists. [UNRESOLVED] whether a vendor-neutral AMR module standard exists (3.7).
- **R19. Electrical identity** for Valtoryn-designed modules: unique per-unit ID plus type/version, readable at boot (HAT/Cyphal pattern [R02-S38, R02-S36]), once hardware exists. Until then, rely on bus-level identity of purchased components (USB descriptors, CAN/EtherCAT identity) [R02-S46, R02-S42].
- **R20. Tiered conformance labels** for modules, as with HAT: for example "described", "identified", "verified", "safety-evidence-linked" (Raspberry Pi's HAT versus EEPROM-only distinction is the precedent [R02-S39]; the label names are mine).

### 7.7 Safety interface

- **R21. The manifest references safety evidence; it does not provide it.** Safety-relevant fields get a separate hash; change to any such field fails the C5 gate until a person records re-validation. Basis: standards framing in 3.8 [R02-S56 to R02-S59]; mechanism is mine.
- **R22. Do not treat the ROS control stack as a safety channel** until the safety architecture workstream decides otherwise; ros2_control states its safety interfaces are planned [R02-S08]. Flag the dependency.

### 7.8 Proposed phasing (software first, mechanical progressively)

| Phase | Content | Exit evidence |
|---|---|---|
| P0 | Conventions: REP-103/105, SemVer, lifecycle contract, repo layout separating platform and robot packages | Review of conventions document |
| P1 | Robot config + generator for the reference differential-drive AMR; ros2_control with mock and simulator hardware; C1-C2 checks | Same config builds sim and (later) hardware profiles; generated files reproducible |
| P2 | Manifest for modules and robot; second robot variant (different sensor set) built from config only; measure manual edits | Count of non-config edits needed for variant 2 (target zero beyond new modules) [EST target] |
| P3 | Bring-up verification C3; factsheet export prototype if the fleet workstream chooses VDA 5050 | Mismatch tests fail closed |
| P4 | Different locomotion type as module (not differential); electrical identity format; safety evidence linkage | Needs hardware and safety workstream input |

---

## 8. Open questions for the owner

1. **Q1. ROS 2 distribution.** Which LTS line does Valtoryn target (Jazzy to May 2029, Lyrical to May 2031 per the distribution table), and is Valtoryn willing to track distributions on a 12-month cadence? [R02-S21, R02-S19]
2. **Q2. Catalogue vs open modules.** Should the first release accept only a curated module catalogue (Clearpath-style) or allow third-party modules from day one (needs a published manifest schema and stability promise)?
3. **Q3. External compatibility targets.** Is VDA 5050 conformance a requirement (it determines the manifest projection and the "mobile robot" vocabulary [R02-S27]); is OPC UA or MassRobotics export wanted?
4. **Q4. Safety posture.** Is the platform expected to host safety functions, or always sit above separate certified safety hardware? This sets the limit on what "module" may mean for sensors and drives.
5. **Q5. Hot-plug appetite.** Is any runtime hot-plug a product requirement, or is cold swap (stop, reconfigure, restart) acceptable for all modules in the first product?
6. **Q6. Mechanical standardisation.** Will Valtoryn publish its own open mechanical/electrical module interface (like a payload deck standard), or consume vendor interfaces? This is a long-lived commitment.
7. **Q7. Third-party trust.** Should modules be signed/attested, and who is the authority? (Cyphal includes optional fields; no required scheme was found.) [R02-S36]
8. **Q8. Governance of schemas.** Who approves manifest schema and interface changes, and what is the deprecation window?
9. **Q9. Licence compatibility of dependencies** for module catalogue contributions (outside this workstream; flag to legal/compliance workstream).

---

## 9. Limitations of this research

- **Paywalled standards were not read.** ISO 9409-1, ISO 3691-4, ISO 13849-1, IEC 61508-1 and ANSI/A3 R15.08 claims come from public catalogue pages or a trade-press article only. Requirements in the full texts (for example how they treat software configuration change) are not established here.
- **Documentation snapshots.** ros2_control pages were read from the Rolling (development) documentation. Some pages carried banners naming Kilted as the latest release and others named Lyrical, which indicates differing cache dates (Sep 2026 and Nov 2026 titles) in what the fetch tool returned. Statements about "not supported" features (URDF reload, plugin reload service) reflect the Rolling docs at that snapshot and may differ in the Lyrical release. **[UNRESOLVED]** Re-check against the Lyrical-specific ros2_control documentation before relying on them.
- **No independent evaluation** of Clearpath or Husarion frameworks, RobMoSys adoption, or Capabilities2 was found or performed.
- **The 2023 ROSCon slides** are a snapshot; type-evolution features may have progressed by 2026.
- **No measurement.** There are no benchmarks of lifecycle, plugin-load or hot-plug latency in this document, and none are claimed. Risk likelihoods marked [EST] are judgement.
- **Not covered:** DDS/Zenoh middleware selection, security (SROS2), digital-twin formats beyond URDF/SDF, fleet orchestration, hardware compute choice, OTA update mechanics, and Asset Administration Shell / IDTA submodels (not researched).
- **Some sources are weak:** a single ROS Discourse thread (R02-S53), a single GitHub README for Capabilities2 (R02-S54), a trade-press article (R02-S59), and a 2020 newsletter (R02-S52).
- **Machine-extracted text.** Several pages were read as text extracted by tools or scripts; table layouts in PDFs (Cyphal specification) were read in raw text form, and I relied on stated rules rather than diagrams.

## 10. Unresolved questions

| ID | Question | What would resolve it |
|---|---|---|
| U1 | Current status of ROS 2 interface-evolution features (type translation, hash mismatch detection) in Lyrical | Lyrical changelog; rosidl/rcl issue trackers; REP-2011/2016 status |
| U2 | Does ros2_control (Lyrical) support hot-plug or URDF reload? | Lyrical ros2_control docs and release notes; maintainers' roadmap |
| U3 | Adoption and maintenance of RobMoSys/SmartMDSD | Repository activity; industrial case studies |
| U4 | Vendor-neutral mechanical standard for AMR modules (decks, batteries, sensor mounts) | ISO/TC 110, TC 299 catalogue review; A3/VDMA/VDA publications |
| U5 | How the safety standards treat software/configuration change for modular mobile robots | Reading licensed full texts of ISO 3691-4, ISO 13849-1, IEC 61508, ANSI/A3 R15.08 |
| U6 | Quantified benefit of manifest/config generation on integration effort | Pilot with measured manual edits per variant |
| U7 | MassRobotics standard versioning and current spec revision | Full repository (schema and PDF) review |
| U8 | Status of ISO/DIS 3691-4 revision and its effect on AMR modularity | ISO catalogue follow-up; standards-body announcements |

---

## 11. Sources

| ID | Title | Organization / author | URL | Published / revision date | Accessed | What it supports |
|---|---|---|---|---|---|---|
| R02-S01 | Managed nodes (ROS 2 design article) | Geoffrey Biggs, Tully Foote; ROS 2 design | https://design.ros2.org/articles/node_lifecycle.html | Written 2015-06; last modified 2021-02 | 2026-11-07 | Lifecycle states, transitions, reconfiguration in Inactive, black-box managed node |
| R02-S02 | Composition (ROS 2 documentation source, About-Composition) | ROS 2 documentation (Open Robotics) | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/ROS-Framework/nodes/About-Composition.rst | n/a (not stated on page) | 2026-11-07 | Components, containers, deploy-time process layout trade-off, load_node service |
| R02-S03 | Creating and using plugins (C++) tutorial, pluginlib (ROS 2 documentation source) | ROS 2 documentation (Open Robotics) | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/ROS-Framework/client-libraries/Working-with-Client-Libraries/Pluginlib.rst | n/a (not stated on page) | 2026-11-07 | pluginlib runtime loading, export macro, XML description file, ClassLoader |
| R02-S04 | Managing node lifecycles - example (ROS 2 documentation source, Managed-Nodes) | ROS 2 documentation (Open Robotics) | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/ROS-Framework/nodes/Working-with-nodes/Managed-Nodes.rst | n/a (not stated on page) | 2026-11-07 | Lifecycle nodes for hardware initialisation, rclcpp_lifecycle |
| R02-S05 | Getting Started (ros2_control, Rolling) | ros2_control maintainers | https://control.ros.org/rolling/doc/getting_started/getting_started.html | n/a (not stated on page) | 2026-11-07 | Controller Manager, Resource Manager, pluginlib-loaded hardware components and controllers |
| R02-S06 | Controller Manager (ros2_control, Rolling) | ros2_control maintainers | https://control.ros.org/rolling/doc/ros2_control/controller_manager/doc/userdoc.html | n/a (not stated on page) | 2026-11-07 | Parameters (update_rate, fallback controllers, command limits, initial hardware states), no URDF reload, spawners |
| R02-S07 | ros2_control hardware interface types (Rolling) | ros2_control maintainers | https://control.ros.org/rolling/doc/ros2_control/hardware_interface/doc/hardware_interface_types_userdoc.html | n/a (not stated on page) | 2026-11-07 | URDF `<ros2_control>` tag structure, joints/sensors/gpio, groups, data types |
| R02-S08 | Lifecycle of a Hardware Component (ros2_control, Rolling) | ros2_control maintainers | https://control.ros.org/rolling/doc/ros2_control/hardware_interface/doc/lifecycle_of_a_hardware_component.html | n/a (not stated on page) | 2026-11-07 | Hardware states, command interfaces in INACTIVE, planned safety interfaces |
| R02-S09 | Handling of Errors During read() and write() Calls (ros2_control, Rolling) | ros2_control maintainers | https://control.ros.org/rolling/doc/ros2_control/hardware_interface/doc/handling_errors_during_read_write.html | n/a (not stated on page) | 2026-11-07 | on_error behaviour, FINALIZED unrecoverable, no reload service |
| R02-S10 | Writing a Hardware Component (ros2_control, Rolling) | ros2_control maintainers | https://control.ros.org/rolling/doc/ros2_control/hardware_interface/doc/writing_new_hardware_component.html | n/a (not stated on page) | 2026-11-07 | Component methods, interface export from URDF, unlisted interfaces |
| R02-S11 | Mock Components (ros2_control, Rolling) | ros2_control maintainers | https://control.ros.org/rolling/doc/ros2_control/hardware_interface/doc/mock_components_userdoc.html | n/a (not stated on page) | 2026-11-07 | Mock hardware for hardware-free testing |
| R02-S12 | Simulator Integrations (ros2_control, Rolling) | ros2_control maintainers | https://control.ros.org/rolling/doc/simulators/simulators.html | n/a (not stated on page) | 2026-11-07 | List of simulator integrations |
| R02-S13 | Navigation Concepts (Nav2) | Nav2 maintainers | https://docs.nav2.org/rolling/getting_started/navigation_concepts/navigation_servers/ | n/a (not stated on page) | 2026-11-07 | Plugin servers, lifecycle and bond, no-fork extension, REP-105 frame requirements, costmap layers |
| R02-S14 | nav2_core controller.hpp | Nav2 maintainers (navigation2 repository) | https://raw.githubusercontent.com/ros-navigation/navigation2/main/nav2_core/include/nav2_core/controller.hpp | n/a (not stated on page) | 2026-11-07 | Controller plugin interface shape |
| R02-S15 | REP 2004: Package Quality Categories | William Woodall; ROS Enhancement Proposals | https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-2004.rst | Created 2019-12-17 | 2026-11-07 | Quality levels, version/API/ABI policy requirements |
| R02-S16 | REP 103: Standard Units of Measure and Coordinate Conventions | Tully Foote, Mike Purvis; ROS Enhancement Proposals | https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-0103.rst | Created 2010-10-07 | 2026-11-07 | SI units standard |
| R02-S17 | REP 105: Coordinate Frames for Mobile Platforms | Wim Meeussen; ROS Enhancement Proposals | https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-0105.rst | Created 2010-10-27 | 2026-11-07 | base_link, odom, map frame conventions |
| R02-S18 | REP 149: Package Manifest Format Three Specification | Dirk Thomas; ROS Enhancement Proposals | https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-0149.rst | Created 2017-10-11 | 2026-11-07 | Dependency version-range attributes |
| R02-S19 | REP 2000: ROS 2 Releases and Target Platforms | Open Robotics authors; ROS Enhancement Proposals | https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-2000.rst | Last Created entry 2023-11-10 | 2026-11-07 | 12-month cadence, LTS support policy, Kilted date (differs from S21) |
| R02-S20 | Developer Guide (ROS 2 documentation source) | ROS 2 documentation (Open Robotics) | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/The-ROS2-Project/Contributing/Developer-Guide.rst | n/a (not stated on page) | 2026-11-07 | ROS SemVer rules: no major bump in a distro, ABI is public interface |
| R02-S21 | Distributions (ROS 2 documentation source, Releases) | ROS 2 documentation (Open Robotics) | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Releases.rst | n/a (not stated on page) | 2026-11-07 | Distribution release and end-of-life dates; stability intent after release |
| R02-S22 | Lyrical Luth release notes (ROS 2 documentation source) | ROS 2 documentation (Open Robotics) | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Releases/Release-Lyrical-Luth.rst | Release May 2026 | 2026-11-07 | Lyrical is LTS, supported to May 2031; new executor, rosidl::Buffer |
| R02-S23 | Interfaces (ROS 2 documentation source, About-Interfaces) | ROS 2 documentation (Open Robotics) | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/ROS-Framework/interfaces/About-Interfaces.rst | n/a (not stated on page) | 2026-11-07 | msg/srv/action IDL description and code generation |
| R02-S24 | ROS 2 types on the wire: type descriptions and hashing in Iron and beyond (slides) | Emerson Knapp (Bonsai Robotics); ROSCon 2023 | https://roscon.ros.org/2023/talks/ROS_2_Types_On-the-wire_Type_Descriptions_and_Hashing_in_Iron_and_onwards.pdf | 2023 (ROSCon 2023) | 2026-11-07 | RIHS01 type hash, type description service, future evolved type translation |
| R02-S25 | Type Description Distribution (REP-2011 subset / REP-2016) issue #1159 | ros2/ros2 GitHub, emersonknapp et al. | https://github.com/ros2/ros2/issues/1159 | Opened 2021-07-21; closed 2023-07-28 | 2026-11-07 | History and completion of type description distribution |
| R02-S26 | Semantic Versioning 2.0.0 | Tom Preston-Werner | https://semver.org/ | n/a (not stated on page) | 2026-11-07 | MAJOR.MINOR.PATCH rules; 0.y.z initial development |
| R02-S27 | VDA 5050 Version 3.0.0 (interface for communication between mobile robots and fleet control) | VDA and VDMA | https://raw.githubusercontent.com/VDA5050/VDA5050/main/VDA5050_EN.md | Version 3.0.0 | 2026-11-07 | Factsheet structure, optional-parameter gating, versioning policy, topic version, extensible enums |
| R02-S28 | VDA5050 GitHub latest release metadata | VDA5050 GitHub project | https://api.github.com/repos/VDA5050/VDA5050/releases/latest | 2026-03-18 (release 3.0.0) | 2026-11-07 | Release date of VDA 5050 3.0.0 |
| R02-S29 | OPC 40010-1 OPC UA for Robotics Part 1: Vertical Integration (reference index) | OPC Foundation and VDMA | https://reference.opcfoundation.org/Robotics/v100/docs/ | Release 1.02, 2025-09-08 | 2026-11-07 | Specification version and publication date |
| R02-S30 | OPC 40010-1 chapter 4: General information to OPC Robotics and OPC UA | OPC Foundation and VDMA | https://reference.opcfoundation.org/Robotics/v100/docs/4 | Release 1.02, 2025-09-08 | 2026-11-07 | Scope (industrial and mobile robots, Part 1 asset management and condition monitoring), namespaces, companion specification concept |
| R02-S31 | OPC 40010-1 chapter 5: Use Cases | OPC Foundation and VDMA | https://reference.opcfoundation.org/Robotics/v100/docs/5 | Release 1.02, 2025-09-08 | 2026-11-07 | Supervision, condition monitoring, asset management, remote operation use cases |
| R02-S32 | OPC 40010-1 chapter 6: Information Model overview | OPC Foundation and VDMA | https://reference.opcfoundation.org/Robotics/v100/docs/6 | Release 1.02, 2025-09-08 | 2026-11-07 | MotionDeviceSystemType as subtype of ComponentType; read-only by default |
| R02-S33 | OPC 40010-1 chapter 7: OPC UA ObjectTypes | OPC Foundation and VDMA | https://reference.opcfoundation.org/Robotics/v100/docs/7 | Release 1.02, 2025-09-08 | 2026-11-07 | MotionDeviceSystemType, controller, axis, motor, gear, power train, safety state, task control types |
| R02-S34 | VDMA - Robotics (OPC Foundation page) | OPC Foundation / VDMA | https://opcfoundation.org/markets-collaboration/robotics/ | n/a (not stated on page) | 2026-11-07 | Joint working group scope: industrial and mobile robots, part-wise specification |
| R02-S35 | MassRobotics Autonomous Mobile Robot Interoperability Standard (README) | MassRobotics | https://raw.githubusercontent.com/MassRobotics-AMR/AMR_Interop_Standard/main/README.md | n/a (not stated on page) | 2026-11-07 | Information shared between AMRs; JSON schema and PDF |
| R02-S36 | Cyphal Specification v1.0 | OpenCyphal | https://opencyphal.org/specification | Revision 2025-05-16 | 2026-11-07 | Node-ID, plug-and-play allocation, GetInfo, DSDL data type versioning and compatibility rules, registers |
| R02-S37 | DroneCAN | DroneCAN project | https://dronecan.github.io/ | n/a (not stated on page) | 2026-11-07 | DNA node ID allocation, planned node capability message |
| R02-S38 | B+ HAT ID EEPROM Format Specification | Raspberry Pi (raspberrypi/hats) | https://raw.githubusercontent.com/raspberrypi/hats/master/eeprom-format.md | n/a (not stated on page) | 2026-11-07 | EEPROM atoms, vendor info, UUID, CRC-16; spec marked preliminary |
| R02-S39 | Add-on boards and HATs (README) | Raspberry Pi (raspberrypi/hats) | https://raw.githubusercontent.com/raspberrypi/hats/master/README.md | n/a (not stated on page) | 2026-11-07 | HAT requirements, tiered conformance, repo deprecation notice |
| R02-S40 | CiA 402: CANopen device profile for drives and motion control | CAN in Automation (CiA) | https://www.can-cia.org/can-knowledge/cia-402-series-canopen-device-profile-for-drives-and-motion-control | n/a (not stated on page) | 2026-11-07 | CiA 402 scope, parts, safety part, conformance and exchangeability caveat |
| R02-S41 | CANopen | CAN in Automation (CiA) | https://www.can-cia.org/can-knowledge/canopen | n/a (not stated on page) | 2026-11-07 | Object dictionary index ranges, device profiles and plug-and-play intent |
| R02-S42 | EtherCAT technology overview | EtherCAT Technology Group | https://www.ethercat.org/en/technology.html | n/a (not stated on page) | 2026-11-07 | SII, ESI, ENI, topology check, Hot Connect |
| R02-S43 | Safety over EtherCAT (FSoE) | EtherCAT Technology Group | https://www.ethercat.org/en/safety.html | n/a (not stated on page) | 2026-11-07 | Black channel safety, IEC 61784-3, SIL 3 |
| R02-S44 | Features and Architecture (micro-ROS) | micro-ROS project (hosted at micro.vulcanexus.org) | https://micro.vulcanexus.org/docs/overview/features/ | n/a (not stated on page) | 2026-11-07 | micro-ROS client API, agent, lifecycle on MCUs |
| R02-S45 | Defined Class Codes | USB Implementers Forum | https://www.usb.org/defined-class-codes | Last update 2023-09-22 | 2026-11-07 | USB class code triple in device and interface descriptors |
| R02-S46 | USB device descriptors | Microsoft Learn | https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/usb-device-descriptors | n/a (not stated on page) | 2026-11-07 | idVendor, idProduct, bcdDevice, immutability during connection |
| R02-S47 | Robot YAML (Clearpath ROS 2 documentation, Jazzy) | Clearpath Robotics | https://docs.clearpathrobotics.com/docs/ros/config/yaml/overview | n/a (not stated on page) | 2026-11-07 | Single robot configuration file, sections, serial number and config version |
| R02-S48 | Generators (Clearpath ROS 2 documentation, Jazzy) | Clearpath Robotics | https://docs.clearpathrobotics.com/docs/ros/config/generators/ | n/a (not stated on page) | 2026-11-07 | Generated URDF/xacro, launch, parameter and bash files from robot.yaml |
| R02-S49 | husarion_components_description (README) | Husarion | https://raw.githubusercontent.com/husarion/husarion_components_description/ros2/README.md | n/a (not stated on page) | 2026-11-07 | Component list config, parent link, pose, custom type |
| R02-S50 | husarion_ugv_ros (README) | Husarion | https://raw.githubusercontent.com/husarion/husarion_ugv_ros/ros2/README.md | n/a (not stated on page) | 2026-11-07 | Build-type switch between hardware and simulation |
| R02-S51 | husarion_ugv_description (README) | Husarion | https://raw.githubusercontent.com/husarion/husarion_ugv_ros/ros2/husarion_ugv_description/README.md | n/a (not stated on page) | 2026-11-07 | components.yaml and wheel configuration files |
| R02-S52 | RobMoSys: A Model-Driven Approach and Tools for Robotics Software Development | Eclipse Foundation newsletter | https://www.eclipse.org/community/eclipse_newsletter/2020/july/3.php | July 2020 (from URL path) | 2026-11-07 | RobMoSys principles; Eclipse SmartMDSD and Papyrus for Robotics (weak: 2020 newsletter) |
| R02-S53 | New Working Group Proposal: Hardware Interface Working Group | ROS Discourse (mrobinson and replies) | https://discourse.openrobotics.org/t/new-working-group-proposal-hardware-interface-working-group/23774 | 2022-01-11 | 2026-11-07 | Anecdotal vendor divergence in interpreting common messages (weak: forum) |
| R02-S54 | capabilities2: reimplementation of the capabilities interface for ROS 2 | CollaborativeRoboticsLab | https://github.com/CollaborativeRoboticsLab/capabilities2 | n/a (not stated on page) | 2026-11-07 | Interfaces, providers, semantic interfaces as YAML (weak: single repository) |
| R02-S55 | ISO 9409-1:2004 Manipulating industrial robots, Mechanical interfaces, Part 1: Plates | ISO | https://www.iso.org/standard/36578.html | 2004-03 (confirmed 2023-04-17 per page) | 2026-11-07 | Scope/abstract of arm flange standard (catalogue page only) |
| R02-S56 | ISO 3691-4:2023 Industrial trucks, Safety requirements and verification, Part 4: Driverless industrial trucks and their systems | ISO | https://www.iso.org/standard/83545.html | 2023-06 | 2026-11-07 | Scope/abstract; AMRs covered; draft replacement pending (catalogue page only) |
| R02-S57 | ISO 13849-1:2023 Safety of machinery, Safety-related parts of control systems, Part 1 | ISO | https://www.iso.org/standard/73481.html | 2023-04 | 2026-11-07 | Scope/abstract (catalogue page only) |
| R02-S58 | IEC 61508-1:2010 Functional safety of E/E/PE safety-related systems, Part 1 | IEC | https://webstore.iec.ch/en/publication/5515 | 2010-04-30 | 2026-11-07 | Scope/abstract, stability date 2027 (webstore page only) |
| R02-S59 | A3 announces R15.08 Part 3 safety standard for industrial mobile robot users | Robotics 24/7 (trade press) | https://www.robotics247.com/article/a3-announces-r15.08-part-3-safety-standard-for-industrial-mobile-robot-users-is-now-available | 2026-10-04 | 2026-11-07 | R15.08 three-part series; Part 3 covers management of change (secondary source) |
| R02-S60 | SDFormat Specification | SDFormat project (Open Robotics) | http://sdformat.org/spec | n/a (not stated on page) | 2026-11-07 | SDFormat spec versions 1.4 to 1.12 and element set |
| R02-S61 | Tool changer (Zimmer Group) | Zimmer Group | https://www.zimmer-group.com/en-us/products/components/robotics/tool-changer | n/a (not stated on page) | 2026-11-07 | Tool changer mounting to EN ISO 9409-1 and utility transmission |
| R02-S62 | QC-29 Tool Changer | ATI Industrial Automation (Novanta) | https://ati.novanta.com/product/qc-29/ | n/a (not stated on page) | 2026-11-07 | ISO 9409-1 mounting patterns, utility pass-through modules |
| R02-S63 | Xacro (README) | ros/xacro maintainers | https://raw.githubusercontent.com/ros/xacro/ros2/README.md | n/a (not stated on page) | 2026-11-07 | Xacro is an XML macro language |
| R02-S64 | URDF (ROS 2 documentation source, URDF-Main) | ROS 2 documentation (Open Robotics) | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Capabilities/Simulation/URDF/URDF-Main.rst | n/a (not stated on page) | 2026-11-07 | URDF definition |
| R02-S65 | Composable Models and Software for Robotics Systems (RobMoSys), project results | CORDIS, European Commission | https://cordis.europa.eu/project/id/732410/results | n/a (not stated on page) | 2026-11-07 | RobMoSys as an EU H2020 project, project ID 732410 |

### Sources that could not be inspected (not cited)

- https://www.ros.org/reps/rep-2000.html and https://www.ros.org/reps/rep-2004.html (rendered REPs): blocked by an anti-bot challenge; the same REPs were read from the source repository instead (R02-S15, R02-S19).
- https://wiki.ros.org/urdf/XML (URDF XML specification): blocked by an anti-bot challenge; only the ROS 2 documentation's URDF overview was read (R02-S64).
- https://docs.ros.org/en/rolling/Tutorials/Intermediate/Composition.html: blocked by an anti-bot challenge; composition concepts were read from the documentation source (R02-S02).
- https://blog.ansi.org/ansi/ansi-a3-r15-08-1-2020-r2026-mobile-robot-safety/ (ANSI R15.08-1 summary): request refused (HTTP 403).
- https://link.springer.com/chapter/10.1007/978-3-030-66494-7_3 (Schlegel, RobMoSys chapter): JavaScript challenge; not read.
- ISO 9409-1 amendments, ISO 10218, ISO 12100, UL 3100 and IEC 61784-3 catalogue pages: not attempted or not read.
- https://github.com/ros/pluginlib README, https://docs.nav2.org/plugins/index.html, https://dronecan.github.io/Specification/ (deep pages): returned not found.
- Safety over EtherCAT PDFs (ETG.5100 and others), MassRobotics `AMR_Interop_Standard.pdf` and JSON schema, and the REP-2011 / REP-2016 drafts: not opened.
