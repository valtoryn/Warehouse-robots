# Reference robot specification — modular differential-drive AMR

> **Status:** Proposed specification. **No hardware exists, nothing is selected finally, nothing is tested.**
> This document defines *what must be decided and how it will be sized*, using only sourced, calculated or
> explicitly estimated values. It is not a bill of materials and not a performance guarantee.
> **Method:** sizing follows the R03 §10 methodology (formulas 1–14) and the R03 §16 parameter table; component
> candidates come from the R03 §17 shortlist. Every value carries its evidence tag.
> **Audit note:** MiR250 datasheet pairings inferred from PDF extraction must be re-checked before use (A-9);
> concrete-floor `Crr` and powered-vehicle wheel derating are unresolved (A-3) and block final sizing.

## 1. Scope and status

| Item | Status |
|---|---|
| Chassis architecture | Proposed: two driven wheels + two or more casters, differential drive |
| Locomotion | Differential drive (nonholonomic, spin-in-place) |
| Final component selections | **None.** Shortlist only (R03 §17); selection requires Gates G-A/G-B/G-F |
| Performance figures | All [EST]/[CALC] until measured on hardware |
| Safety | Out of scope; see safety domain boundary (R08 §4, HARDWARE_ABSTRACTION §1) |

## 2. Chassis architecture

**Configuration [REC]:** differential drive — two powered wheels on a common axis plus passive casters for
stability. Basis: best-documented public commercial precedent (MiR250: two TPU drive wheels + casters,
250 kg payload, 2.0 m/s) [FACT R03-S58, R03-S59]; simplest kinematics; highest load per drive wheel vs mecanum
(R03 §2.2–2.3).

**Kinematics [FACT R03-S25, CALC]:**

```
v  = r·(uL + uR)/2        ω = r·(uR − uL)/(2d)
uL = (v − d·ω)/r          uR = (v + d·ω)/r
```

where `r` = wheel radius, `2d` = wheel separation. Implemented by `diff_drive_controller` (TwistStamped
`~/cmd_vel`, odometry, per-axis limits) [FACT R04-S28].

**Rejected for reference robot:** mecanum (low published load ratings vs AMR loads, inherent slip,
odometry risk — R03 §2.2–2.3); swerve (mechanical complexity, no located ROS 2 controller — R03 §2.1);
Ackermann (turning radius unsuitable for warehouse aisles — [EST]); skid-steer (floor wear, slip model
needs fitting — R03-S30); legged (out of scope — R03 §2.1).

**Future path:** the Chassis kinematics interface (HARDWARE_ABSTRACTION §3) admits omni/swerve/other
configurations as modules; VDA 5050 kinematics enum is extensible (DIFFERENTIAL, OMNIDIRECTIONAL, THREE_WHEEL,
extensible) [FACT R02-S27]. No non-differential robot is claimed.

## 3. Locomotion and drivetrain

### 3.1 Wheels and casters

- Drive wheels: polyurethane tread, ~200 mm diameter class ([FACT] MiR250 benchmark lists 200 mm drive wheel —
  A-9 caveat; [EST] for Valtoryn). PU treads: 75 or 92 Shore A; Blickle floor-pressure reference values
  3.5 / 8.0 N/mm² [FACT R03-S32]. Catalog wheel ratings assume *manual* operation — powered-vehicle derating
  is **[UNRESOLVED]** (A-3); supplier confirmation required per part.
- Casters: large enough to pass floor joints/cracks; roller/ball bearings for heavy loads [FACT R03-S34].
  Swivel resistance must be measured (odometry error source, R03-S29).
- Floor interface targets derive from site survey: friction μ, roughness, joints, slope — all
  **[UNRESOLVED]** pending measurement (R03 §16).

### 3.2 Motors, gearboxes, drives

Sizing chain per R03 §10.1 formulas 5–7:

```
T_wheel = F·r / n_driven          T_motor = T_wheel / (N·η)
ω_motor = N·v / r                 N = gear ratio
```

- Motor type: brushless (AGV/AMR vendor guidance; maintenance argument) [FACT R03-S42; REC].
- Candidate motors (shortlist, no selection): maxon EC-i 52 (399 mNm cont., 11.5 A, 4360 rpm, 89 % eff.,
  823 g) [FACT R03-S38]; integrated drive Oriental BLV-R (60–400 W, 15–55 V, STO, Modbus/CANopen)
  [FACT R03-S41]; ODrive S1/Pro controllers (CAN/CAN-FD, 40–120 A class) [FACT R03-S43..S45].
- Gearbox: planetary, ratio chosen so peak motor speed at top speed stays in range (R03 §4.3 [CALC]);
  backlash/efficiency from datasheet (e.g. maxon GP 52 C: 4.3:1, 91 %, 0.6° backlash [FACT R03-S39]);
  multi-stage efficiency for ratios >1 stage **[UNRESOLVED]**.
- Drive interface: CiA 402/CANopen vs CAN-FD — decision after bench conformance test; `ros2_canopen` is
  self-declared not production-ready [FACT R03-S49]. STO/SS1/safe-speed signals consumed read-only (R08 §4).

### 3.3 Worked sizing example (template — NOT a specification)

R03 §10.2 demonstrates the method with assumed inputs (200 kg total, 1.5 m/s, 0.5 m/s², 2 % grade, r = 0.10 m,
N = 20, η = 0.85): peak tractive force 168.7 N → 8.43 Nm/wheel → 0.496 Nm motor peak; cruise 0.087 Nm;
stopping distance 1.38 m at assumed reaction+deceleration; tip-over governed by assumed CoG; battery 8S LiFePO₄
(LFP preferred over NMC for cycle life at 170 vs 242 Wh/kg cell level) [all CALC/EST; inputs R03-S38..S53].

**The real specification must re-run this with measured inputs** (R03 §16 table): target payload, mass, CoG,
footprint, speed/accel/decel limits, floor μ and Crr, slope, duty cycle, ambient range.

## 4. Sensor configuration

Reference set (proposed, subject to Gate B driver availability and R08 zone requirements):

| Function | Candidate | Basis |
|---|---|---|
| Safety scanning | 2× safety 2D LiDAR at diagonal corners for 360° (SICK nanoScan3: 3 m protective field, PL d/SIL 2/Type 3; or Hokuyo UAM-05LPA: 5 m protection) | [FACT R03-S01, R03-S02]; layout precedent MiR250 [FACT R03-S59] |
| Navigation | 2D nav LiDAR (RPLIDAR S2E class) or safety-scanner raw data if usable | [FACT R03-S04]; ROS driver evidence [R03-S05] |
| IMU | Bosch BMI088 class, rigid mount near rotation centre | [FACT R03-S10]; Allan-variance calibration required |
| Depth/obstacle | Front depth camera (RealSense D400 / Orbbec Gemini / OAK-D Pro class) for low/overhanging obstacles | [FACT R03-S13..S17]; safety scanners see only their scan plane (MiR250 note [FACT R03-S59]) |
| Optional 3D | Ouster OS1 or Livox Mid-360 class | [FACT R03-S06, R03-S08]; optional, not required |

Safety note: safety scanners' protective functions run in the safety domain; ROS drivers publish raw data
only and carry no safety function [FACT R03-S03]. Collision Monitor must not share sensors with the safety
layer (RESEARCH_AUDIT, R08).

## 5. Battery and power

- Chemistry: LiFePO₄ preferred for cycle life/duty (EVE LF105: 3.2 V, 105 Ah, 1980 g, 4000 cycles @25 °C/0.5C
  [FACT R03-S52]) vs NMC (Molicel P45B: 242 Wh/kg [FACT R03-S53]); final choice after duty-cycle measurement.
- **Gen-1 recommendation (R08 §3):** buy a certified pack/BMS (IEC 62619 lists AGVs as motive applications
  [FACT R03-S55]); do not design cell packs initially. UN 38.3 test summary required from supplier.
- Sizing: energy = P_avg·t_run/(DoD·SOH) per R03 §10.1 formula 13; worked example yielded ~2.4 kWh nominal for
  assumed 194 W average / 8 h — real values pending measurement.
- Bus voltage: 24 V vs 48 V class — **[UNRESOLVED]** (drive availability, cable current, safety
  extra-low-voltage rules; R03 §16).
- Charging: contact dock with digital handshake before current enable; Nav2 `opennav_docking` +
  `SimpleChargingDock` exist [FACT R03-S57, R04-S43]; contact rating **[UNRESOLVED]**.

## 6. Compute

- Primary candidate: NVIDIA Jetson Orin NX/Nano class (100/40 TOPS, 10–25 W/7–15 W, CAN, GbE, CSI)
  [FACT R03-S19]; gated on Ubuntu 26.04 BSP (Gate A) and Isaac ROS 5.0 Lyrical/JetPack 7.2 pairing
  [FACT R03-S20, R03-S21].
- Auxiliary: Raspberry Pi 5 class for gateway/diagnostics [FACT R03-S22]; MCU (STM32 class) for hard-RT
  motor/brake/watchdog loops [FACT R03-S24, REC].
- Power/thermal: wide-input industrial compute preferred over Pi 5 for in-chassis main compute (0–70 °C limit)
  [FACT R03-S22; REC]. x86 industrial PC datasheet not yet read — [UNRESOLVED].

## 7. Payload interfaces

- Top plate: defined bolt pattern, CoG limits, electrical/CAN connector — to be specified before any lift/
  conveyor module (R03 §15.9 [REC]). Public engineering data for conveyor/lift/tugger/fork tops beyond MiR
  user guides was not found — [UNRESOLVED].
- Payload containment: strapping/friction surfaces when μ_payload < a_b/g (R03 §10.1 formula 11);
  tip-over likely governs for raised/lift payloads (R03 §10.2).
- Payload state is a first-class software input switching footprint, costmap filters, speed limits (FR-A3).

## 8. Mechanical constraints

| Parameter | Value | Status |
|---|---|---|
| Footprint | To be set from aisle survey | [UNRESOLVED] |
| Wheel track / wheelbase | To be set (stability + odometry) | [UNRESOLVED] |
| CoG height limit | To be set; drives tip-over formulas | [UNRESOLVED] |
| Max speed / accel / decel | To be set with R08 stopping-distance requirements | [UNRESOLVED] |
| Payload mass classes | To be set (benchmark: MiR250 250 kg; shelf carrier 300 kg w/ traction kit) | [FACT R03-S58, R03-S59] |
| Ingress protection | To be set per environment | [UNRESOLVED] |
| Operating temperature | To be set (cold-store possibility affects battery/lubricants) | [UNRESOLVED] |

## 9. Performance requirements (targets to be validated, not claims)

All values below are **[EST] placeholders pending the measurement campaign** — they define what must be
measured, not what is promised:

| Metric | Target form | Method |
|---|---|---|
| Payload capacity | ≥ two defined classes | Weigh/tilt test |
| Speed/accel/decel | Per R08 stopping-distance budget | Controlled stops, encoders + ground truth |
| Stopping distance | Within validated envelope per payload/floor | R05 F6 procedure |
| Odometry drift | Per-metre/per-radian budget after UMBmark calibration | R03 §2.2, R05 F4 |
| Runtime | Per duty cycle at defined payload | Logged discharge (R05 F15) |
| Docking accuracy | Per dock type (MiR250: ≤44 s worst marker, positioning accuracies published) | R07 §2.4, R06 docking params |

## 10. Open items blocking specification freeze

| ID | Item | Source |
|---|---|---|
| RS-1 | Target payload classes and mass budget | Owner decision |
| RS-2 | Floor survey data (μ, Crr, roughness, joints, slopes) | Site measurement |
| RS-3 | `Crr` and powered-vehicle wheel derating | Supplier data / measurement (A-3) |
| RS-4 | Bus voltage decision | Drive availability + safety rules |
| RS-5 | Drive backend (CiA 402 vs CAN-FD) | Bench conformance test |
| RS-6 | Compute platform final selection | Gates A–B |
| RS-7 | Pack/BMS/charger selection | Certified supplier shortlist |
| RS-8 | Mechanical module interface definition | Before any payload module |
| RS-9 | Re-verify MiR250 PDF-extracted pairings | Original PDFs (A-9) |
| RS-10 | ISO 3691-4 stopping/performance requirements | Licensed standard (A-5) |
