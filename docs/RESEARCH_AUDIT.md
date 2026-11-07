# Research audit — R01–R08

> **Status:** Audit of the eight research documents against the repository's evidence standard.
> **Date:** 2026-11-07 · **Auditor scope:** full read of R01–R08, cross-document consistency checks,
> spot verification of cited primary sources where flagged by the audit.

## Method

Each research document was read in full (R06–R08 via a delegated full read, with spot verification of reported
issues). Findings were checked for: unsupported or incorrect technical claims, internal contradictions,
duplicated or inconsistent recommendations, stale software versions, missing technical comparisons, weak source
attribution, incorrect manufacturer specifications, unjustified assumptions, and unresolved questions that block
implementation. Spot verification was performed on high-risk cited sources (SICK nanoScan3, SICK microScan3,
VDA 5050 topic list, ROS 2 distribution dates). No document required wholesale correction; the research was
already written to a high evidence standard.

Classification used below:

- **Confirmed** — claim verified against the cited source or internally consistent arithmetic.
- **Correction required** — demonstrable error; fixed in place (none required, see below).
- **Incomplete evidence** — claim rests on summarised, paywalled or single sources; must not be over-cited.
- **Conflicting evidence** — two sources disagree; unresolved.
- **Unresolved** — open question that blocks implementation decisions.
- **Recommendation** — audit-level advice for the architecture phase.

## Document-by-document findings

### R01 — Robotics ecosystem and competitive landscape

| Finding | Class | Severity | Notes |
|---|---|---|---|
| Nav2 "ultra-marathon" table internally inconsistent (implied 0.73 m/s > stated 0.45 m/s max; recoveries/mile 4.49 vs 4.3) | Confirmed (self-flagged) | Low | Doc already discloses it at §3.3 and forbids using it quantitatively. No edit needed; carry the caution into architecture docs. |
| Kilted EOL: REP-2000 says Nov 2026, Releases table says Dec 2026 | Conflicting evidence | Low | Disclosed at §2.2. Either way Kilted is EOL within weeks; immaterial to decisions. |
| Sources R01-S04, R01-S05, R01-S18 were read through a summarising fetch tool | Incomplete evidence | Medium | §9 discloses this. Facts taken only from them (Lyrical platform tiers, Kilted Zenoh Tier-1, RMF README distro list) should be re-verified before being quoted in normative documents. Carry forward as a verification task in the dependency matrix. |
| REP-2000 source file lags the Releases page (no Lyrical entry) | Confirmed | Low | Disclosed. Treat `Releases.rst` as authoritative. |
| "No open-source warehouse task/fleet stack exists" | Incomplete evidence | Low | Doc correctly labels it absence-of-evidence, not proof. Systematic GitHub survey remains unresolved (R01 §10.10). |
| VDA 5050 v3.0.0 published 2026-03-18; open library `vda5050_core` supports only v2.0.0 | Confirmed | Medium | Version lag is real and verified against repo metadata; it makes a VDA 5050 v3 gateway a build item, not a config item. |

### R02 — Modular robotics architecture

| Finding | Class | Severity | Notes |
|---|---|---|---|
| ros2_control docs were read from Rolling; "no URDF reload", "FINALIZED unrecoverable, no reload service" | Incomplete evidence | Medium | §9 flags that Lyrical docs may differ; these statements must be re-verified against the pinned distribution before the HAL spec freezes them as constraints. |
| CiA 402 conformance caveat (declared ≠ verified) | Confirmed | Medium | Central justification for the manifest "declared vs verified" split; keep it in MODULARITY_SPECIFICATION. |
| ISO 3691-4:2023 expected to be replaced by ISO/DIS 3691-4 | Incomplete evidence | Low | Paywalled; only catalogue pages read. Standards decisions deferred to R08 implementation. |
| Recommendation set R1–R22 (§7) | Recommendation | — | Coherent and consistent with R04/R06; adopted as architecture input. |

### R03 — Hardware and mechanical engineering

| Finding | Class | Severity | Notes |
|---|---|---|---|
| Several datasheet PDFs lost table alignment in extraction (SICK, MiR250, Faulhaber, Blickle, EVE, D400) | Incomplete evidence | Medium | §18 lists every pairing that was inferred by row/column order (MiR250 wheel diameters, D400 min-Z/accuracy columns, nanoScan3 per-variant columns). These values must be re-checked against the original PDFs before use in the reference-robot spec. The worked example (A1–A16) is explicitly labelled non-specification. |
| Rolling-resistance `Crr` on concrete and powered-vehicle wheel derating not established | Unresolved | High (for sizing) | Blocks final motor/battery sizing; resolves by supplier data or measurement. Recorded as a blocking item in the reference-robot spec. |
| Sizing methodology (section 10) and candidate shortlist (section 17) | Confirmed methodology | — | Arithmetic verified; all inputs labelled. The methodology is adopted verbatim as the sizing procedure for the reference robot spec. |
| Hub motors, VESC, swerve ROS controller, heavy-duty mecanum: not datasheet-verified | Unresolved | Low | Correctly deferred; supports "differential drive first" decision. |

### R04 — Robotics software stack evaluation

| Finding | Class | Severity | Notes |
|---|---|---|---|
| Recommended baseline: ROS 2 Lyrical + Gazebo Jetty + ros2_control 6.x + Nav2 1.5.x + Fast DDS default, Zenoh spike | Recommendation | — | Internally consistent; dependency table verified against `ros/rosdistro` files. Gates A (Ubuntu 26.04 on compute BSP), B (driver availability on Lyrical), C (one-week spike) are prerequisites, not yet passed. |
| `fuse` released in rosdistro but README silent on ROS 2 support | Incomplete evidence | Low | Flagged; not adopted in baseline. |
| REP-2005 snapshot predates `ros_gz`; ros2_control not listed | Incomplete evidence | Low | REP-2005 is stale; not relied on for package decisions. |
| Windows 11 host guidance (WSL2/dev container, usbipd-win limits) | Confirmed | Low | Consistent with R05 §3.11 Windows limitation. |
| "~5.5 months since release" for Lyrical and third-party driver lag risk | Unresolved | Medium | The central adoption risk; recorded as ADR risk. |

### R05 — Simulation, digital twins and the reality gap

| Finding | Class | Severity | Notes |
|---|---|---|---|
| Gazebo non-determinism report (gz-sim issue #3349, run-to-run metre-scale divergence) | Confirmed (as a report) | Medium | Open, single reporter; correctly treated as "do not assume bitwise determinism" → statistical regression gates. Adopted in SIMULATION_REQUIREMENTS. |
| Gazebo battery model does not couple consumption to torque | Confirmed | Medium | Drives the recommendation for a Valtoryn-supplied power model. |
| Evidence levels E0–E4 and fidelity dimensions F1–F20 | Recommendation | — | Well-formed; adopted into VALIDATION_STRATEGY with the same "no hardware data yet" status. |
| Reality-gap literature is manipulator/legged-dominated, not warehouse AMR | Incomplete evidence | Medium | Correctly disclosed; means F-dimension thresholds must come from Valtoryn's own hardware campaign. |

### R06 — Autonomous robotics

| Finding | Class | Severity | Notes |
|---|---|---|---|
| Route Server "0.0031 ms (100 nodes) to 44 ms (1,000,000 nodes)" | Incomplete evidence | Low | Sourced to README with unstated hardware; 44 ms over 1 M nodes is implausibly fast. Treat as order-of-magnitude only; verify with prototype (already an unresolved question). |
| AMCL "500 to 2000 particles" phrasing loose (default is a range, not fixed) | Confirmed (minor) | Low | Immaterial; Nav2 docs govern. |
| TEB listed in plugin catalogue but omitted from the §3.6 controller comparison table | Correction required (minor) | Low | Coverage gap, not an error; noted so readers do not infer TEB was excluded deliberately. No edit made to preserve research as-is; architecture docs will use the catalogue table in R01 §3.2 which does include TEB. |
| "Kinematically feasible paths" scoped to planners could be misread as covering controllers | Confirmed (minor) | Low | Clarity note only. |
| Distro codename "Luth" vs "Lynx" inconsistency | Conflicting evidence | Low | Self-flagged [UNRESOLVED]; resolve when pinning the distribution (R04 names it "Lyrical Luth"). |
| Nav2 adopted behind an abstraction; payload-aware footprint/limits as first-class input | Recommendation | — | Consistent with R02 manifest and R07 capability model; adopted. |

### R07 — Warehouse automation and fleet intelligence

| Finding | Class | Severity | Notes |
|---|---|---|---|
| Delegation of "tugger/cart safety" to R08 is only half-met: R08 confirms ISO 3691-4 excludes towed trailers but has no dedicated trailer/towing hazard analysis | Incomplete evidence | Medium | **Action for architecture phase:** the safety/validation docs must carry an explicit open item for trailer/towing hazards rather than assuming R08 covered it. |
| Facility-asset model split between R06 (versioned SLAM map, filter masks, route graph, dock DB) and R07 (one internal facility model with exporters to LIF/RMF/GeoJSON) | Conflicting evidence (unreconciled) | Medium | **Resolved at architecture level:** the facility model is defined once in SYSTEM_ARCHITECTURE §facility model and includes R06's costmap-filter/zone semantics as an export target; R06's per-asset versioning applies within it. |
| VDA 5050 v3.0.0 has no conformance/certification scheme; four incompatible graph models exist (VDA 5050, LIF, RMF, Nav2 GeoJSON) | Confirmed | Medium | Confirms R01's "adopt spec externally, never internally" recommendation; internal facility model is a build item. |
| "about 24 cycles per hour" fleet-cycle estimate | Confirmed (arithmetic) | Low | Explicitly [EST] with stated assumption. |
| Task allocation must handle interrelated sub-tasks outside Gerkey's model | Confirmed | Low | Drives the two-stage capability-matching dispatch design in SYSTEM_ARCHITECTURE. |

### R08 — Safety, standards and verification

| Finding | Class | Severity | Notes |
|---|---|---|---|
| Safety domain must never depend on ROS 2; autonomy may request but never command safety states; certified safety controller (Option B) recommended; no first-party safety certification target | Confirmed | High | This is the binding safety boundary for all architecture docs. |
| ISO 13849-1:2023 PFH-band conflict between two trade sources | Conflicting evidence | Medium | Correctly left [UNRESOLVED]; does not affect architecture (PLr decisions belong to the safety case, not the software architecture). |
| Machinery Regulation application date 14 vs 20 Jan 2027 | Conflicting evidence | Low | Best-supported date recorded; irrelevant until deployment jurisdiction is known. |
| Collision Monitor must not share sensors with the safety layer | Confirmed | Medium | Interface constraint to encode in HARDWARE_INTERFACE_SPECIFICATION. |
| Evidence ladder L0–L4 consistent with R05 E0–E4 and R07 validation table | Confirmed | — | Three documents agree in spirit; VALIDATION_STRATEGY adopts one ladder referencing all three. |
| ISO 3691-4:2023 normative content (PLr table, muting limits, zone tables) not read (paywalled) | Incomplete evidence | High (for safety case) | Blocks any claim about required performance levels; safety case is out of this milestone's scope but must be listed as blocking physical deployment. |
| Worked stopping-distance example arithmetic | Confirmed | — | Verified correct. |

## Cross-document synthesis

**Consistent across all eight documents (confirmed, adopt as architecture foundation):**

1. ROS 2 is the mandatory middleware; reuse `ros2_control`, Nav2, BehaviorTree.CPP, SLAM Toolbox/AMCL, Gazebo+`ros_gz`, and the VDA 5050 *specification* — never rebuild these (R01 §8, R02 R2, R04 §4.1, R06 §8).
2. Software modularity first: declarative robot configuration + generated URDF/launch/parameters; capability manifest generated not hand-written; SemVer everywhere; ROS-native plugin mechanisms only (R02 §7).
3. VDA 5050 is an external fleet edge protocol only; internal architecture uses ROS 2 actions/state + a Valtoryn facility model with exporters (R01 §5.3, R07 §4.3).
4. Open-RMF is an optional integration target, never a core dependency; a minimal reservation-based baseline coordinator is a build item (R01 §5.1, R07 §4.3).
5. Simulation is a validation environment, not the product; evidence levels E0–E4 / L0–L4 / validation table are consistent (R05 §7, R08 §5).
6. Safety domain never depends on ROS 2; safety functions are separate certified hardware; ROS consumes safety state only (R08 §4, R03 §15.5, R06 §3.10).
7. Reference robot: differential drive first; mecanum/omni/swerve remain addable through the same kinematics abstraction (R03 §15.1–15.2, R04 controllers table, VDA 5050 extensible kinematics).

**Corrections made to research documents:** none required. No demonstrable factual errors were found that justified editing the research; all discrepancies were already self-disclosed. Minor coverage gaps (TEB omission in R06 §3.6 table) are noted here rather than editing the research, per the instruction to preserve research and traceability.

**Remaining uncertainties that block or condition implementation:**

| ID | Uncertainty | Blocks | Resolves by |
|---|---|---|---|
| A-1 | ROS 2 distribution pin (Lyrical recommended, Gates A–C unpassed) | All code work | R04 §4.3 gates |
| A-2 | Third-party driver availability on Lyrical for chosen LiDAR/IMU/motor drives | Reference robot spec freeze | Driver survey per shortlisted part |
| A-3 | Concrete-floor `Crr`, powered-vehicle wheel derating, caster swivel resistance | Motor/battery sizing | Supplier data or measurement |
| A-4 | ros2_control Rolling-doc claims (no URDF reload, FINALIZED unrecoverable) on Lyrical | HAL spec freeze | Re-read Lyrical ros2_control docs |
| A-5 | ISO 3691-4:2023 normative content | Safety case (not software architecture) | Licensed standard |
| A-6 | Trailer/towing hazard analysis gap (R07→R08 delegation) | Safety case for tugger variants | Dedicated analysis in validation programme |
| A-7 | VDA 5050 v3 open implementation status | Fleet gateway estimate | Track `vda5050_core`; prototype |
| A-8 | Gazebo Jetty ↔ Open-RMF/`gz_ros2_control` compatibility | Simulation stack pin | Compatibility check + demo run |
| A-9 | MiR250 datasheet pairings inferred from PDF extraction | Benchmark comparisons only | Re-check original PDFs |
| A-10 | Summarised-source facts (R01-S04/S05/S18) | Dependency matrix entries | Re-fetch originals |

## Recommendation

Proceed to architecture synthesis using the "confirmed" decisions above. Where a research document's claim is
labelled Incomplete evidence or Conflicting evidence, the architecture documents must either (a) carry the
uncertainty explicitly, or (b) list it as a decision gate — never silently upgrade it to fact.
