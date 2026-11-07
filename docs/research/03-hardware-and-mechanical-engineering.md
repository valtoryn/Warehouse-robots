# R03 — Hardware and Mechanical Engineering

> **Status:** Research document — proposed findings, nothing here is implemented.
> **Workstream:** R03 · **Last verified:** 2026-11-07 · **Evidence legend:** see below

## Evidence legend

- **[FACT]** established by a cited source, always followed by a source ID such as [R03-S07]. For manufacturer data this means "the manufacturer states it", not "independently measured".
- **[CALC]** derived by a shown calculation from cited or labelled inputs.
- **[EST]** engineering estimate or assumption (basis stated).
- **[REC]** Valtoryn recommendation or proposal (engineering judgement, not established fact).
- **[UNRESOLVED]** could not be established; what is needed to resolve it is stated.

No Valtoryn robot hardware exists. Nothing below describes a built, tested or measured Valtoryn system. All "worked example" inputs are assumptions chosen to demonstrate a method; they are **not** a reference-robot specification.

---

## 1. Scope and method

**Scope.** Locomotion options and kinematics; wheels and casters; motors, gearboxes, drives and encoders; safety and navigation LiDAR; IMUs; depth cameras; batteries, BMS and charging; embedded compute and the real-time layer; payload mechanisms; pallet dimensions; structural/tip-over/braking calculations; a sizing method with a worked example; the list of parameters Valtoryn still has to decide; and a candidate-component shortlist. Safety-standard compliance (ISO 3691-4, ISO 13849, IEC 61496) is deliberately left to workstream R08 and only referenced here.

**Method.** I read manufacturer datasheets, official documentation pages and open-access technical documents in this session and cite only those. Several datasheets were PDFs whose tables lost their column alignment during text extraction (SICK, MiR, Faulhaber, Blickle, EVE); where I paired a value with a label by row order I say so in section 12. Where a manufacturer value could only be read from a distributor-hosted copy, the sources table says so. Values from commercial robots (MiR250) are used purely as public benchmarks of what a commercial product states; they are not Valtoryn targets.

**What "ROS 2 support evidence" means here.** A README, documentation page or package list from the vendor or an official community repository that I opened. I did not install or run any driver (no hardware, no testing).

---

## 2. Locomotion options

### 2.1 Kinematic equations (with sources)

Notation: body twist `(ω, vx, vy)` in the chassis frame, wheel radius `r`, wheel driving angular speed `u`. Equations below are restated from Lynch & Park, *Modern Robotics* (May 2017 preprint, chapter 13) [R03-S25]; symbols that the PDF text extraction dropped (Greek letters) are restated by me.

**Differential drive.** Wheels of radius `r` on a common axis, separation `2d`. [FACT] The text gives the inverse mapping `uL = (v − d·ω)/r`, `uR = (v + d·ω)/r` [R03-S25]; forward: `v = r(uL + uR)/2`, `ω = r(uR − uL)/(2d)` [CALC, algebraic inverse of the same relation]. The platform can spin in place; it needs one or more casters or sliders for support [R03-S25]. ROS 2's `diff_drive_controller` exposes `wheel_separation`, `wheel_radius` and a separation multiplier as parameters and can compute odometry from hardware feedback or from commanded velocity (open-loop) [R03-S26].

**Four-mecanum-wheel holonomic base.** [FACT] The inverse kinematics `u = H(0)·Vb` is given as eq. 13.10 for four mecanum wheels with 45° rollers; the sign pattern is: all wheels forward for +x; wheels 1,3 backward and 2,4 forward for +y; wheels 1,4 backward and 2,3 forward for CCW rotation [R03-S25]. With half-wheelbase `ℓ`, half-track `w` and `L = ℓ + w`, the forward (odometry) mapping that follows from the orthogonal columns of `H` is [CALC]:

```
vx = (r/4)(u1 + u2 + u3 + u4)
vy = (r/4)(−u1 + u2 − u3 + u4)
ωz = (r/(4L))(−u1 + u2 + u3 − u4)
```

[FACT] The source also notes that with more than three wheels, commanding wheel speeds that do not satisfy `u = H·Vb` forces wheels to skid [R03-S25]. ROS 2 has a `mecanum_drive_controller` for four mecanum wheels that takes a stamped Twist (x, y, yaw) and publishes odometry [R03-S27].

**Swerve / steerable modules.** For module `i` at position `(xi, yi)` in the chassis frame, rigid-body velocity addition gives the module's ground-velocity vector `(vx − ω·yi, vy + ω·xi)`; wheel speed is its magnitude divided by `r`, and the steering angle is its direction [CALC, from rigid-body kinematics as in the twist formalism of R03-S25]. A comparative kinematics paper covers a 4-mecanum, a 3-omniwheel and a 2-swerve platform using wheel-speed limits as the comparison basis [R03-S31] (only the abstract was readable; its equations were not inspected). I found no ROS 2 `ros2_controllers` swerve controller in the controller index/pages I opened [R03-S26, R03-S28] — **[UNRESOLVED]**: confirm by searching the `ros2_controllers` repository directly.

**Car-like (Ackermann) and tricycle.** [FACT] For a car-like robot with wheelbase `ℓ`, the steering angle `φ` relates to yaw rate `ω` and speed `v` by `φ = atan(ℓ·ω/v)` [R03-S25], i.e. `ω = (v/ℓ)·tan φ` [CALC]; the minimum turning radius follows as `ℓ / tan φmax` [CALC]. ROS 2's `steering_controllers_library` implements Bicycle, Tricycle (one steer + two drive joints) and Ackermann kinematics with front or rear steering [R03-S28].

**Skid-steer and tracked.** [FACT] Skid-steer vehicles rely on wheel/track slip, so an ideal-rolling kinematic model is inadequate; one experimental approach fits an instantaneous-centre-of-rotation (ICR) model to measured data without full dynamics [R03-S30].

**Legged.** [REC] Out of scope for warehouse floors for the reference platform: no source read in this session supports a legged configuration for pallet-scale payloads, and the only AMR documentation I read in detail (MiR250) describes a wheeled platform [R03-S58, R03-S59]. I did no further legged research.

### 2.2 Strengths, limits and odometry behaviour

| Configuration | Mobility | Warehouse-floor strengths | Limits / risks | Odometry behaviour | Evidence |
|---|---|---|---|---|---|
| Differential drive + casters | Nonholonomic; spin in place | Mechanically simple; two actuators; compact footprint; high payload per drive wheel possible | Caster scrub and swivel resistance act as "internal forces" that cause slip; cannot move sideways | Systematic errors from unequal wheel diameters and uncertain effective wheelbase dominate on smooth floors; slip from floor irregularities dominates on rough floors | [R03-S25, R03-S29] |
| 4× mecanum | Holonomic (3 DOF) | Lateral motion in tight aisles without turning | Rollers give a small contact patch and published load ratings are low (section 3.3); over-constrained at 4 wheels, so floor unevenness forces slip; roller-gap vibration is plausible but not sourced here | Slip is inherent when wheel speeds are inconsistent with `H·Vb` [R03-S25]; sideways-motion odometry is typically the least trustworthy [EST] | [R03-S25, R03-S36, R03-S37] |
| Swerve (≥2 modules) | Holonomic | Full-diameter ordinary wheels; carries load on normal PU tread | Most actuators (drive + steer per module), steering-angle calibration, mechanically complex | Steering-angle encoder error adds to wheel odometry; inconsistent module commands cause scrub [CALC from section 2.1] | [R03-S31] (abstract only) |
| Ackermann / tricycle | Nonholonomic, turn radius limited | Straightforward high-speed path tracking | Minimum turn radius; reversing and docking need larger space | Rear-axle odometry is well defined; steering-angle offset biases yaw | [R03-S25, R03-S28] |
| Skid-steer / tracked | Nonholonomic with slip | Tolerant of rough ground | Skidding wears floors and degrades dead reckoning; model needs experimental fitting | Slip makes the effective ICR differ from geometric centre | [R03-S30] |

[FACT] Borenstein and Feng classify differential-drive odometry error sources as systematic (unequal wheel diameters; mean wheel diameter differing from nominal; misalignment; uncertainty in effective wheelbase; limited encoder resolution and sampling rate) and non-systematic (uneven floors, objects on the floor, slip from slippery floors, over-acceleration, fast turning, external and internal forces such as casters, non-point wheel contact) [R03-S29]. They propose the bi-directional square-path test "UMBmark" because a uni-directional square test can hide compensating errors [R03-S29]. Systematic errors stay almost constant over time and can be calibrated; non-systematic errors depend on the floor [R03-S29]. [FACT] Modern Robotics states odometry errors accumulate from slip and integration error, so odometry is good on short time scales and should be fused with other sensing [R03-S25].

[REC] Valtoryn should treat odometry as a calibrated, covariance-tagged short-horizon input for every chassis type, with a per-chassis calibration procedure (UMBmark-style for diff-drive) in the hardware abstraction layer, and should not assume wheel odometry quality transfers between chassis types.

### 2.3 Payload implications by configuration

[CALC] Even load share across four wheels for a hypothetical 347 kg total (97 kg robot + 250 kg payload, taken from the MiR250 specification as a public benchmark [R03-S58]) is 347/4 = 86.8 kg per wheel. [FACT] Published 6-inch mecanum wheel ratings I read are 80 lb (≈36 kg) per wheel for AndyMark 6-inch [R03-S36] and 80 kg per "wheel (pair)" for Kornylak's 6-inch RW310 [R03-S37]. So [CALC] hobby/light-duty mecanum ratings are below the per-wheel load of a benchmark commercial AMR carrying its rated payload; heavy-duty mecanum parts need separate sourcing and **[UNRESOLVED]** (no heavy-duty mecanum datasheet was read). [FACT] The MiR250 specification lists TPU as drive-wheel material and separate caster wheels, and the Shelf Carrier guide refers to "the two drive wheels", i.e. a two-driven-wheel layout with casters; stated payload 250 kg at 2.0 m/s [R03-S58, R03-S59].

---

## 3. Wheels, casters and floor interaction

### 3.1 Tread materials and load rating (manufacturer data)

- [FACT] Blickle describes polyurethane treads of 75 Shore A (Besthane Soft) and 92 Shore A (Extrathane) and gives reference average floor pressures per tread material: PU 75 Shore A 3.5 N/mm², PU 92 Shore A 8.0 N/mm², standard solid rubber 3.5 N/mm², cast nylon 60 N/mm² [R03-S32]. Floor pressure is defined as radial force divided by contact area, and harder treads load the floor more [R03-S32].
- [FACT] Blickle's pallet-truck roller series HTH (92 Shore A Extrathane tread on a metal centre; series header gives dimensions 60×35 to 82×65 mm) is listed at 220–850 kg load capacity per roller; the tread is rated −20 to +70 °C with reduced load capacity above +40 °C [R03-S33].
- [FACT] Colson lists wheel types with capacity ranges in lb (e.g. "Moldon Polyurethane" 700–3500 lb, "Polyurethane HI-TECH" 100–1700 lb) and states capacities are based on ICWM "normal operating conditions" — manual operation on a relatively smooth surface such as concrete — with excessive temperature or dirt reducing ratings [R03-S34].
- [REC] Because the Colson basis is manual operation, catalogue capacities should not be used unmodified for a powered vehicle at speed; ask the wheel supplier for a powered-vehicle rating or derating factor. **[UNRESOLVED]**: the numeric derating factor; needs supplier confirmation per wheel part number.

### 3.2 Floor friction and rolling resistance

- [FACT] The MiR250 specification states a recommended floor-to-wheel friction coefficient of 0.60–0.80 and TPU as drive-wheel material, and limits traversable gap/step to 0–20 mm (above 20 mm at reduced speed, above 50 mm prohibited), with ±5 % incline at 0.5 m/s [R03-S58] (pairing by row order; see section 12).
- [FACT] Hamilton Caster gives rolling force `F = f × W / R` with `f` (units of length) the coefficient of rolling friction, `W` the wheel load and `R` the wheel radius; its worked example for 85A polyurethane on a steel floor uses `f = 0.047 in` [R03-S35]. [CALC] For an 8-inch wheel (R = 4 in) that is a dimensionless coefficient `f/R = 0.047/4 = 0.0118`. Hamilton also notes the coefficient varies with speed, load, and floor material and that polyurethane has a range of values [R03-S35]. No concrete-floor value was read — **[UNRESOLVED]** for concrete; a rolling-resistance test on the actual wheel and floor is needed.
- [FACT] Static friction is bounded by `fs ≤ μs·N` (OpenStax University Physics) [R03-S62]. This bounds tractive force and braking: `a_max,traction = μ·(fraction of weight on driven wheels)·g`.
- [FACT] Hamilton and Colson both distinguish a larger starting force from a lower sustained rolling force [R03-S35].

### 3.3 Casters and mecanum wheels

[FACT] Colson recommends wheels large enough to pass over floor cracks and obstructions and notes larger diameter rolls more easily; roller or ball bearings are advised for heavy loads [R03-S34]. [REC] Caster swivel resistance should be measured, because internal caster forces are a named non-systematic odometry error source [R03-S29]. Mecanum ratings are covered in section 2.3.

---

## 4. Motors, gearboxes and hub motors

### 4.1 Brushed vs brushless

[FACT] Oriental Motor's AGV/AMR white paper makes the vendor case for brushless over brushed: brushed motors are typically larger and require brush maintenance; its BLV series gives flat torque characteristic up to rated speed and a 50:1 continuous speed ratio (80–4000 rpm) [R03-S42]. [REC] For a warehouse platform targeting multi-shift operation, use brushless motors; brushed motors are only worth considering for very low-cost prototypes. The choice is not backed by lifetime data from any source I read.

### 4.2 Real datasheet examples

**maxon EC-i 52, part 574740** (18 V variant, 180 W class, with Hall sensors) [FACT, R03-S38]: nominal voltage 18 V; no-load speed 4860 rpm; nominal speed 4360 rpm; nominal (max continuous) torque 399 mNm; nominal current 11.5 A; stall torque 4370 mNm; stall current 298 A; max efficiency 89 %; terminal resistance 0.0604 Ω; torque constant 35 mNm/A; speed constant 273 rpm/V; mechanical time constant 0.839 ms; winding thermal time constant 18 s; motor thermal time constant 1780 s; max winding temperature +155 °C; max speed 6000 rpm; 8 pole pairs; mass 823 g. [CALC] Consistency check: 1/(273 rpm/V) → 0.03498 V·s/rad, equal to the stated 35 mNm/A, as expected when back-EMF and torque constants agree in SI units (the same torque/speed-constant relation appears in Faulhaber's technical information [R03-S40]).

**maxon GP 52 C planetary gearhead, part 223081** (single stage) [FACT, R03-S39]: reduction 4.3:1; max continuous torque 4 Nm; intermittent 6 Nm; max efficiency 91 %; average backlash 0.6°; max continuous input speed 6000 rpm; max radial load 420 N at 12 mm from flange; mass 460 g. [CALC] A continuous motor torque of 0.399 Nm through this gearhead gives at most 0.399 × 4.3 × 0.91 = 1.56 Nm at the output, below the 4 Nm gearhead limit, so the motor is the limiting element in that pairing.

**Oriental Motor BLV-R series** (integrated motor + driver, DC input) [FACT, R03-S41]: output powers 60, 100, 200, 400 W; 15–55 VDC supply range (24–48 VDC lineup; the 400 W type is 48 VDC with 30–55 VDC operating range); speed range 1–4000 r/min; communication via Modbus RTU and CANopen; Safe Torque Off function; driver overvoltage alarm at 63 VDC; options include electromagnetic brake and parallel-shaft, CS-geared and hollow-shaft-flat gearheads. [FACT] The white paper states the BLV driver continues operating at reduced speed/torque when battery voltage sags, and that its RS-485 ports support a Modbus RTU network of up to 31 devices [R03-S42].

**Hub motors.** I found only vendor catalogue pages of low evidential quality: one lists servo hub motors of 4.5–12 inch size, 30–800 W rated power and 1.1–30 Nm rated torque [R03-S65] (weak source; no independent datasheet read). **[UNRESOLVED]** for hub motors: no manufacturer datasheet with torque-speed curves, load rating, bearing life or IP rating was read. [REC] Treat hub motors as a later option; integrated motor + gearbox + bearing carriers must be validated against the vertical wheel load (a function the hub bearing, not the gearhead, must carry).

### 4.3 Gear ratio and gearbox practical constraints

[CALC] Gear ratio `N` is chosen so that peak motor speed at top vehicle speed `v` stays inside the motor's speed range: `N = ω_motor / ω_wheel = ω_motor · r / v`. [FACT] Gearhead datasheets give backlash (0.6° average for the GP 52 C), efficiency (max 91 % single stage) and permissible radial/axial load [R03-S39]; with `N` > one-stage range, multi-stage efficiency is lower — **[UNRESOLVED]** the multi-stage figure, which needs the specific gearhead datasheet. [FACT] Oriental offers a hollow-shaft flat gearhead to avoid a coupling and reduce length [R03-S42].

---

## 5. Motor controllers and drives

| Product | Voltage | Current | Feedback / interfaces | Notes | Source |
|---|---|---|---|---|---|
| ODrive S1 | 12–50.5 V (typical 16–48 V) | Operating motor current 20 A free-air, 40 A with heat spreader at 25 °C, 40–80 A peak (peak derated vs. bus voltage); comparison page: 40 A nominal / 80 A peak, 2 kW continuous | Onboard encoder, quadrature, Hall, RS485, SPI encoder; USB, CAN/CAN-FD (up to 8 Mbit/s with firmware limits), UART, analog, PWM, STEP/DIR; brake-resistor support | IP20 with case; ESD ratings per IEC 61000-4-2 | [FACT: R03-S43, R03-S45] |
| ODrive Pro | 15–58 V (recommended max 58 V) | 20 A free-air, 80 A with active cooling, 100 A peak (3 s); comparison page: 70 A nominal / 120 A peak, 4 kW continuous | Adds differential SSI and BiSS-C encoders, isolated CAN; CAN-FD up to 12 Mbit/s with firmware limits | Fan output; no brake-resistor support | [FACT: R03-S44, R03-S45] |
| Roboteq SBLG2360T | up to 60 V | 2 × 16 A continuous, 2 × 30 A (30 s), 2 × 45 A peak (2 s) | USB, CAN, FOC, Hall/encoder/SSI inputs; STO | Listing states "STO PLe, Cat3, SIL3" — the safety claim was read only on the product page; full manual not read | [FACT: R03-S47] |
| Oriental BLV-R driver | 15–55 V | motor-dependent (60–400 W motors) | Modbus RTU, CANopen; Hall-based feedback; STO | Integrated motor/driver package | [FACT: R03-S41] |

- [FACT] ODrive publishes a ROS 2 package (`odrive_node`, plus a work-in-progress `odrive_ros2_control`) for CAN control of ODrive Pro/S1/Micro (not 3.x); stated system requirements Ubuntu ≥ 20.04 and ROS 2 ≥ Humble [R03-S46]. The ODrive docs state ODrive S1/Pro/Micro are supported by the next-generation firmware line; ODrive v3.6 is labelled not recommended for new designs [R03-S45].
- [FACT] CiA 402 is CAN in Automation's drive-and-motion-control CANopen profile; it standardizes functional behaviour of servo drives, frequency inverters and stepper controllers via a finite state machine and operation modes, and is partly standardized as IEC 61800-7 (CiA 402-2 corresponds to IEC 61800-7-201) [R03-S48]. CiA itself warns that the many optional functions limit interchangeability and some vendors claim conformity while implementing only a subset [R03-S48].
- [FACT] `ros2_canopen` (ros-industrial) provides a CANopen driver framework for ROS 2 including a CiA 402 driver; its README states it is "currently under development and not yet ready for production use" and lists builds for rolling, kilted, jazzy and lyrical [R03-S49].
- [REC] Make the motor-drive interface in the hardware abstraction layer a ros2_control hardware interface with two swappable backends: (a) CiA 402 over CANopen for industrial drives (Oriental BLV-R, Roboteq-class), (b) CAN/CAN-FD for ODrive-class drives. Because the CiA 402 ROS stack is self-declared not production-ready [R03-S49], budget time for a thin in-house CiA 402 layer or conformance testing per drive. I did not verify VESC: no authoritative VESC datasheet or documentation page was opened, so VESC is **[UNRESOLVED]**.
- [REC] Functional safety (STO, SS1, safe speed) is outside this document; see R08. Commercial reference: the MiR250 Shelf Carrier guide describes a safety PLC that triggers STO contactors for a category 0 stop followed by a controlled brake via SS1, a dynamic (short-circuit) brake to stop at goals and mechanical parking brakes that engage after standstill [R03-S59].

---

## 6. Encoders

- [FACT] Same Sky (formerly CUI) AMT21: 12- or 14-bit absolute position, RS-485 interface with unique node address (multiple encoders on one bus), 3.8–5.5 V supply (5 V typical), ≤16 mA, accuracy 0.2°, −40 to +105 °C; variants single-turn or multi-turn [R03-S50].
- [FACT] AS5047P (ams OSRAM, datasheet hosted by Infineon): on-axis magnetic sensor, 14-bit core resolution, SPI interface plus programmable ABI output (100–4096 steps per revolution), UVW and PWM outputs, up to 28 000 rpm, non-linearity ±0.8° optimum / ±1° with temperature, SPI propagation delay 90–110 µs [R03-S51].
- [CALC] 14-bit resolution over one revolution is 360°/16384 = 0.022° per count; at wheel radius 0.10 m, one count at the *wheel* is 0.10 × 2π/16384 = 0.038 mm of rolling distance. Gear reduction multiplies this resolution when the encoder is on the motor shaft (e.g. a 20:1 reduction yields 0.0019 mm per count) but backlash then sits outside the measurement loop; see 4.3.
- [FACT] The AMT21 accuracy of 0.2° [R03-S50] and the AS5047P's ±0.8° INL [R03-S51] are datasheet accuracies of the sensor; actual accuracy depends on magnet/mounting [R03-S51 states a magnet assumption (N35H) in its test conditions] — **[UNRESOLVED]** installed accuracy, which must be measured.
- [REC] Use absolute encoders on steering axes (swerve, tricycle) so no homing is needed after power loss; incremental/Hall is acceptable on drive wheels for odometry.
- [FACT] Two ODrive-compatible encoder interface families are documented (RS485, SPI, quadrature, Hall; Pro adds SSI/BiSS-C) [R03-S45], which matches the encoders above.

---

## 7. LiDAR (2D safety/navigation, 3D)

| Sensor | Range | FoV / resolution | Safety / protection | Interface / power | Source |
|---|---|---|---|---|---|
| SICK nanoScan3 (safety) | Protective field 3 m; warning field 10 m; distance measuring range 40 m | 275° scan angle; 0.17° angular resolution; configurable object resolution 20/30/40/50/60/70/150/200 mm | Type 3 (IEC 61496), SIL 2 (IEC 61508), Cat. 3 and PL d (EN ISO 13849); PFHd 8.0×10⁻⁸ /h; mission time 20 years; response time 70–85 ms depending on variant; 4–8 simultaneous fields, up to 128 fields on Pro | 24 V DC (16.8–30 V); 3.9 W without output load; I/O, EFI-pro or EtherNet/IP CIP Safety variants; 106.6 × 80 × 117.5 mm, 0.67 kg, IP65; document dated 2023-04-21 | [FACT: R03-S01] |
| Hokuyo UAM-05LPA-T301 (safety) | Protection range max 5 m; warning range max 30 m (non-safety); distance max 40 m | 270°; min detectable width 30 mm to 70/150 mm depending on range | Type 3 (IEC 61496-1/-3), SIL 2 (Type B, HFT=1), Cat. 3 PL d; PFHd 8.1×10⁻⁸ /h (1.6×10⁻⁷ in master/slave) | 24 V DC ±10 % (−30/+20 % on battery); 6 W no load, 50 W max with load; OSSD outputs; RS-485 config, USB 2.0, Ethernet 100BASE-TX; 80 × 80 × 95 mm, 0.8 kg, IP65; spec dated 2023-12-11 | [FACT: R03-S02] |
| Slamtec RPLIDAR S2E (navigation) | 0.05–30 m at 90 % reflectance; accuracy ±30 mm typical | 360°; 10 Hz; 32 kHz sample rate; 0.12° | None claimed (Class 1 eye-safety only) | Ethernet 10/100 (UDP); 9–28 V supply | [FACT: R03-S04] |
| Ouster OS1 (Rev8, 3D) | 90 m @10 % reflectance; 170 m @80 %; 0.0 m minimum-range capability (0.5 m default) | 44° vertical, 32/64/128 channels, up to 4096 horizontal; 5–40 Hz | None (IP68/IP69K housing) | 10–20 W (15 W nominal); 9–58 V DC; 1000BASE-T; 500 g | [FACT: R03-S06] |
| Livox Mid-360 (3D) | 40 m @10 % reflectance; 70 m @80 %; blind zone 0.1 m | 360° × (−7° to 52°); 200 000 pts/s; 10 Hz | Laser Class 1 eye-safe | 9–27 V, 6.5 W average (14 W peak in self-heating at −20 to 0 °C); 100BASE-TX; built-in ICM40609 IMU; IP67; 265 g | [FACT: R03-S08] |

- [FACT] The SICK ROS 2 driver supports microScan3, nanoScan3 and outdoorScan3 variants with Ethernet and publishes the raw scan as `laser_scan` [R03-S03]. [REC] Raw-data publication through ROS does not carry a safety function; the safety function must run through the scanner's own safe outputs/safe network and not through ROS (R08 topic). Hokuyo's UAM scanner ROS 2 driver: **[UNRESOLVED]** — I did not locate one.
- [FACT] RPLIDAR ROS 2 driver `sllidar_ros2` lists A1, A2, A3, C1, S1, S2, S3, S2E and T1 [R03-S05]. Ouster's official ROS 2 driver covers rolling/humble/jazzy/kilted/lyrical [R03-S07]; Livox ROS Driver 2 covers ROS 2 up to Jazzy on Ubuntu 24.04 per its OS list, and warns it is a debugging tool "not recommended for mass production" [R03-S09].
- [CALC] The protective-field range (3 m SICK, 5 m Hokuyo), not the 40 m measuring range, bounds the speed at which a stop can be guaranteed. The section 10 example gives a 1.38 m stopping distance for its *assumed* inputs, which is inside both fields before any field-sizing margins; those margins and the safety-distance method belong to R08.
- [FACT] The MiR250 Shelf Carrier uses two safety laser scanners with 270° fields placed diagonally on front and rear corners to give 360° coverage, plus 3D cameras and proximity sensors; localization uses motor encoders, an IMU and the safety laser scanners [R03-S59]. This is evidence for a two-scanner corner layout but is a competitor's design, not a Valtoryn requirement.
- [REC] Reference design suggestion: two safety 2D scanners at diagonal corners (360° coverage), one separate 2D navigation LiDAR only if the safety scanner cannot expose usable raw data, and 3D LiDAR optional rather than required. All numbers here need re-evaluation in R08/R04.

---

## 8. IMU

- [FACT] Bosch BMI088 (datasheet rev 1.9, January 2024): accelerometer ranges ±3/±6/±12/±24 g; zero-g offset typ ±20 mg; offset temperature drift <0.2 mg/K; ODR 12.5–1600 Hz; noise density 190 µg/√Hz (Z) and 160 µg/√Hz (X,Y) in normal mode; gyroscope ranges 125–2000 °/s; zero-rate offset ±1 °/s (25 °C, offset cancellation off); offset change over temperature ±0.015 °/s per K; g-sensitivity 0.1 °/s/g; output noise 0.1 °/s rms at 47 Hz bandwidth (stated as 0.014 °/s/√Hz); gyro current 5 mA [R03-S10]. The datasheet is designed for "harsh vibration environments" [R03-S10].
- [CALC] Cross-check: 0.014 °/s/√Hz × √47 Hz = 0.096 °/s ≈ 0.1 °/s, matching the stated rms noise.
- [UNRESOLVED] Bias *stability* (Allan variance bias instability) is not given in the BMI088 datasheet portions I read; only offset and offset-vs-temperature figures. It must be measured (Allan deviation) on the integrated board, or taken from a datasheet that publishes it.
- [CALC] Illustrative heading drift: a *constant uncorrected* 1 °/s zero-rate offset (the typ spec) integrates to 60° per minute, which is why the offset must be calibrated and the IMU is fused, not integrated alone. Temperature drift of ±0.015 °/s/K over a 20 K swing contributes up to 0.3 °/s.
- [FACT] Livox Mid-360 integrates an ICM40609 IMU [R03-S08], the MiR250 localization uses an IMU [R03-S59] and the Orbbec Gemini 335 family has a 6-DoF IMU [R03-S15]. TDK/InvenSense and Xsens/BNO085 parts were not researched (**[UNRESOLVED]**).
- [REC] Place the IMU close to the chassis rotation centre, rigidly mounted, with a calibration procedure at commissioning. In a warehouse AMR on a flat floor, the gyroscope yaw rate is the main benefit.

---

## 9. Cameras and depth

- [FACT] RealSense status: RealSense completed its spin-out from Intel on 2025-07-11 with a $50 million Series A, now an independent company that says it continues to support existing customers and the roadmap including D-series cameras [R03-S11]. The vendor's own site now lists D430, D450, D555 (PoE), D585 Pro and D405/D415 series; the D430 page lists D435 with a buy button, an ideal operating range of 0.3–3 m and specified D435 depth accuracy <2 % at 2 m [R03-S12]. The `realsense-ros` wrapper README announces a repository migration (its build-badge URL points to the `realsenseai` GitHub organization), shows ROS 2 badges for ROS 2 rolling/kilted/jazzy/iron/humble/foxy, and states the ROS 1 wrapper is no longer supported [R03-S14]. **[UNRESOLVED]**: whether D435i/D455 specifically are or will be end-of-life — no such notice found on the pages I read.
- [FACT] D400 datasheet (Revision 017, September 2023): D435 family baseline 50 mm, depth FOV 87° × 58° (HD); D455/D450 module baseline 95 mm; minimum-Z at 1280×720 about 280 mm for D435-class and 520 mm for D455-class (D415: 450 mm); Z-accuracy ≤2 % at ≤2 m (D435-class) and ≤4 m (D455-class) [R03-S13] (table cells paired by column order; see section 12).
- [FACT] Orbbec Gemini 335/336 (datasheet V1.1): active+passive stereo, 50 mm baseline (335L: 95 mm), depth 1280×800 up to 30 fps, FOV 90° × 65°, range 0.10–20 m+ with optimal 0.26–3 m, minimum depth 0.26 m at 1280×800, average power <3.0 W (peak 6.5 W), USB-C, 6-DoF IMU, ASIC-based on-camera depth processing; 335L is IP65 [R03-S15]. Orbbec's documentation set lists a ROS2 wrapper user manual [R03-S16].
- [FACT] Luxonis OAK-D Pro: 75 mm stereo baseline, mono sensors OV9282 with 80°/55° H/V FOV, IR dot projector and IR illumination, IMU, USB 2/3 connection, "ideal range" ~80 cm–12 m, MinZ ~20 cm (400P with extended disparity) to ~80 cm (800P) [R03-S17]; on-camera RVC2 processing 4 TOPS (1.4 TOPS for AI) [R03-S17]. The DepthAI ROS driver lets OAK cameras operate as ROS 2 components [R03-S18].
- [REC] Treat the depth camera as a front-facing obstacle/pallet-pocket sensor for low-height or overhanging obstacles not seen by a 2D scanner plane; the MiR250 Shelf Carrier guide states its safety scanners detect only objects intersecting a plane at 200 mm height and that its two front 3D cameras are used for navigation only, not as part of the safety system [R03-S59]. Choose camera by minimum-Z and FOV versus mounting position, not by headline range.

---

## 10. Sizing methodology and worked example

### 10.1 Formulas

Symbols: `m` total mass (kg), `g` = 9.81 m/s², `r` wheel radius (m), `N` gear ratio, `η` drivetrain efficiency (motor-to-ground), `Crr` dimensionless rolling coefficient, `θ` slope, `a` acceleration, `μ` wheel-floor friction, `n` number of driven wheels. Formulas are elementary mechanics (constant-acceleration kinematics and statics as treated in OpenStax University Physics [R03-S62, R03-S63, R03-S64]) applied to a rolling vehicle.

1. Rolling resistance force: `F_rr = Crr · m · g` (from `F = f·W/R` with `Crr = f/R` [R03-S35]).
2. Grade force: `F_g = m·g·sin θ`.
3. Inertial force: `F_a = m·a` (add rotational inertia of wheels/rotors as `J/r²` terms if significant).
4. Required tractive force: `F = F_rr + F_g + F_a`.
5. Wheel torque per driven wheel: `T_w = F·r / n`.
6. Motor torque per motor: `T_m = T_w / (N·η)` (motoring); during braking use `η` in the numerator.
7. Motor speed at top speed: `ω_m = N·v/r`.
8. Mechanical power: `P_mech = F·v`; electrical `P_el = P_mech/η` plus electronics.
9. Traction limit: `F ≤ μ·(fraction of weight on driven wheels)·m·g` [R03-S62].
10. Reaction + braking stopping distance: `d = v·t_r + v²/(2·a_b)` [constant-deceleration kinematics, R03-S64].
11. Payload slip on a top plate during braking requires `μ_payload ≥ a_b/g` (static friction bound [R03-S62]).
12. Tip-over (statics, torque balance about the support edge [R03-S63]): with centre-of-gravity height `h` and half-support-width `b` (lateral) or `ℓ` (longitudinal): tip when `a ≥ g·b/h` (lateral) or `a ≥ g·ℓ/h` (braking/accelerating); in a turn of radius `R`, `v ≤ √(g·b·R/h)`; on a slope, tip at `tan θ = ℓ/h`, slide at `tan θ = μ`.
13. Pack energy: `E_req = P_avg · t_run`; `E_nominal = E_req / (DoD · SOH)`; runtime `t = E_nominal·DoD·SOH / P_avg`; C-rate `= I/Ah_rated`.
14. Motor RMS torque over a duty cycle: `T_rms = √(Σ Tᵢ²·tᵢ / Σ tᵢ)` compared with the motor's continuous torque (e.g. 0.399 Nm for the EC-i 52 [R03-S38]); peak torque compared with the short-term operating range and thermal time constants.

### 10.2 Worked example — ASSUMED inputs, NOT a Valtoryn specification

All inputs below are [EST] assumptions chosen only to show the arithmetic.

| ID | Assumed input | Value | Basis |
|---|---|---|---|
| A1 | Total mass `m` (robot + payload) | 200 kg | Arbitrary |
| A2 | Configuration | Differential drive, 2 driven wheels, 2 casters | Arbitrary |
| A3 | Wheel radius `r` | 0.10 m | Arbitrary (same size class as the 200 mm drive wheel read in the MiR250 spec, per section 12 caveat) |
| A4 | Top speed `v` | 1.5 m/s | Arbitrary; benchmark MiR250 states 2.0 m/s [R03-S58] |
| A5 | Acceleration `a` | 0.5 m/s² | Arbitrary; benchmark MiR250 states limit 0.3 m/s² at max payload [R03-S58] |
| A6 | `Crr` | 0.015 | Hamilton gives 0.0118 for 85A PU on steel (8 in wheel) [R03-S35]; raised for concrete/castor drag; no concrete value read |
| A7 | Slope | 2 % | Arbitrary; benchmark MiR250 ±5 % at 0.5 m/s [R03-S58] |
| A8 | Efficiency `η` | 0.85 | Below the 91 % single-stage gearhead maximum [R03-S39] |
| A9 | Gear ratio `N` | 20 | Chosen so motor speed ≈ 2865 rpm |
| A10 | μ wheel-floor, weight fraction on driven wheels | 0.60, 0.60 | Low end of the 0.60–0.80 range recommended by MiR [R03-S58]; 60 % is arbitrary |
| A11 | Reaction time `t_r` | 0.170 s | 0.070 s scanner response [R03-S01] + 0.100 s assumed controller/drive latency |
| A12 | Emergency deceleration `a_b` | 1.0 m/s² | Arbitrary |
| A13 | CoG height `h`, half-track `b`, half-wheelbase `ℓ` | 0.35 m, 0.25 m, 0.30 m | Arbitrary |
| A14 | Auxiliary loads | compute 15 W, 2 safety scanners 2×3.9 W [R03-S01], 2 cameras 2×3.0 W [R03-S15], MCU/BMS/misc 5 W, drives idle 10 W | Mixed: scanner and camera values from datasheets, others [EST] |
| A15 | Average traction power, runtime | 150 W, 8 h | Arbitrary |
| A16 | Battery | 8S LiFePO₄ using EVE LF105 cells, DoD 0.8, end-of-life SOH 0.8 | Cell data [R03-S52]; DoD/SOH assumed |

**Forces and torques** [CALC]:
- `F_rr = 0.015 × 200 × 9.81 = 29.4 N`
- `F_g = 200 × 9.81 × sin(atan 0.02) = 39.2 N`
- `F_a = 200 × 0.5 = 100 N`
- Peak (accelerating on the grade): `F = 29.4 + 39.2 + 100 = 168.7 N`; wheel torque total `168.7 × 0.10 = 16.9 Nm`, i.e. 8.43 Nm per driven wheel.
- Motor torque peak per motor: `8.43 / (20 × 0.85) = 0.496 Nm`.
- Cruise on flat: `29.4 N`, motor torque `29.4×0.10/2/(20×0.85) = 0.087 Nm`.

**Speed and power** [CALC]:
- Wheel speed `1.5/0.10 = 15 rad/s = 143.2 rpm`; motor speed `15 × 20 = 300 rad/s = 2865 rpm`.
- Peak mechanical power `168.7 × 1.5 = 253 W`; electrical `253/0.85 = 298 W`.
- Cruise flat `44 W` mechanical (52 W electrical); cruise on 2 % grade `103 W` mechanical.

**Motor check against a real datasheet (illustrative only)** [CALC using R03-S38]: motor speed 2865 rpm needs a back-EMF of `2865/273 = 10.5 V`; with the 18 V EC-i 52, headroom is positive. Peak current `0.496/0.035 = 14.2 A` (+ about 1 A no-load current ≈ 15 A) exceeds the 11.5 A nominal current, but only for the 3 s acceleration, shorter than the 18 s winding thermal time constant. Duty-cycle RMS torque (flat route: 3 s accel, 20 s cruise, 3 s decel, 10 s idle) is `0.135 Nm`, well under the 0.399 Nm continuous rating. **[UNRESOLVED]**: whether short-term peaks are acceptable needs maxon's operating-range curve and a thermal model; the 18 V variant is illustrative only, since this example's bus is 25.6 V. A 20:1 ratio also exceeds the single-stage 4.3:1 gearhead read, so a suitable multi-stage gearhead datasheet is still needed.

**Traction** [CALC]: `0.60 × 0.60 × 200 × 9.81 = 706 N` available traction vs 168.7 N required, so no slip at design acceleration (max traction-limited acceleration `0.6×0.6×9.81 = 3.5 m/s²`).

**Stopping distance** [CALC]: `d = 1.5 × 0.170 + 1.5²/(2 × 1.0) = 0.255 + 1.125 = 1.38 m`. Payload slip check: `μ_payload ≥ 1.0/9.81 = 0.10`. Compare the benchmark's own note: MiR250's "minimum distance to achieve maximum speed" is 9.5 m at 2.0 m/s [R03-S58]; constant 0.3 m/s² would need `2.0²/(2×0.3) = 6.7 m` [CALC], so the published acceleration limit is a cap, not the average (average ≈ `4/19 = 0.21 m/s²` [CALC]).

**Tip-over and slope** [CALC] (A13): lateral tip at `a = 9.81×0.25/0.35 = 7.0 m/s²`; longitudinal tip at `9.81×0.30/0.35 = 8.4 m/s²`; slip occurs first at `μg = 5.9 m/s²`. Turning at `R = 1.0 m`: tip speed `√(9.81×0.25×1.0/0.35) = 2.65 m/s` vs slide `√(0.6×9.81×1.0) = 2.43 m/s`. Slope: tip at `atan(0.30/0.35) = 40.6°`, slide at `atan 0.6 = 31.0°`. If a lift raises the CoG to 0.80 m, the lateral tip threshold falls to `9.81×0.25/0.80 = 3.1 m/s²` and longitudinal to `3.7 m/s²` [CALC], i.e. below the 5.9 m/s² slip limit, so tipping rather than sliding becomes the governing mode — an important design consequence for lift-type payloads. The numbers are only as good as the assumed `h`, `b`, `ℓ`; measured CoG including payload variability is required (section 11).

**Battery** [CALC]: aux `15+7.8+6+5+10 = 43.8 W`; total average `150 + 43.8 = 193.8 W`; 8 h → `1550 Wh`; nominal energy needed `1550/(0.8×0.8) = 2423 Wh`. Using EVE LF105 cells (3.20 V nominal, 105 Ah minimum, mass 1980 ± 60 g, 4000 cycles to 80 % capacity at 25 °C and 0.5C/0.5C [R03-S52]): 8S1P = `8 × 3.2 × 105 = 2688 Wh`, cell mass `8 × 1.98 = 15.8 kg` (cell-level energy density `336/1.98 = 170 Wh/kg`), nominal pack voltage 25.6 V, full-charge voltage `8 × 3.65 = 29.2 V`. Predicted runtime `2688×0.8×0.8/193.8 = 8.9 h`. Peak electrical draw about `(298+43.8)/25.6 = 13 A` ≈ 0.13C, far below cell limits. Standard charge current is 0.5C = 52.5 A [R03-S52], i.e. `25.6 V × 52.5 A = 1.34 kW` and ≈ `0.8×105/52.5 = 1.6 h` for 20 %→100 % in constant-current terms (ignoring the CV tail) [CALC]. For comparison, Molicel INR-21700-P45B (NMC) lists 242 Wh/kg at cell level [R03-S53]; the same 2423 Wh would need about `2423/242 = 10 kg` of NMC cells vs `2423/170 = 14.3 kg` of LFP cells [CALC] — a ~4 kg cell-mass difference before packaging, cooling and BMS.

---

## 11. Batteries, BMS and charging

- **Chemistry comparison.** [FACT] EVE LF105 (LFP prismatic): 3.2 V nominal, ≥105 Ah, 1980 g, charge cut-off 3.65 V, discharge cut-off 2.5 V (2.0 V below 0 °C), 4000 cycles to 80 % at 25 °C and 2000 cycles at 45 °C (0.5C/0.5C, under a specified compression force), standard charge/discharge 0.5C = 52.5 A [R03-S52] (copy hosted by a reseller; spec dated March 2022). [FACT] Molicel INR-21700-P45B (NMC cylindrical): typical 4500 mAh / 16.2 Wh, 3.6 V nominal, 4.2 V max, 2.5 V min, 45 A max continuous discharge (80 °C cut-off), 13.5 A max charge, 242 Wh/kg, 70 g max [R03-S53]. [CALC] Cell-level energy density comparison: LFP 170 Wh/kg vs NMC 242 Wh/kg. [EST] LFP's tolerance to charge-at-rate and cycle life are the usual reasons for stationary-duty fleets; the cycle-life numbers here are manufacturer conditions at 0.5C and 25 °C, not warehouse duty cycles.
- **Commercial benchmark.** [FACT] MiR250: 47.7 V nominal (42–54 V) pack, 1.63 kWh (34.2 Ah), 14 kg, minimum 3000 full cycles to 80 %, charging up to 35 A via a dock that communicates with the robot over a CAN interface [R03-S58] (chemistry not extracted). [CALC] 47.7 V × 34.2 Ah = 1631 Wh, consistent with the stated kWh.
- **BMS.** [FACT] TI BQ76952: monitor/protector for 3- to 16-series Li-ion/Li-polymer/LiFePO₄ packs; cell-voltage accuracy <10 mV typical; coulomb counter offset <1 µV typical; protections for voltage, temperature, current and internal diagnostics; cell balancing (autonomous or host-controlled); high-side FET drivers and secondary fuse drive; I²C (400 kHz), SPI and HDQ; datasheet SLUSE13B revised November 2021; the data sheet lists "other industrial battery pack" among applications [R03-S54]. It is a monitoring/protection IC, not a certified BMS; functional safety of the BMS is out of scope here (R08). [REC] Prefer a purchased, certified BMS with a CAN/RS-485 interface or design around a monitor IC like this one with an independent hardware protection path; decision pending.
- **Standards.** [FACT] IEC 62619:2022 specifies safety requirements and tests for secondary lithium cells and batteries in industrial applications and lists "automated guided vehicle (AGV)" among motive applications (road vehicles excluded) [R03-S55]; I read only the IEC webstore description, not the standard (paid). [FACT] UN 38.3 (UN Manual of Tests and Criteria, Part III) comprises eight tests labelled T.1–T.8; Transport Canada's summary names T.1 altitude simulation, T.2 thermal, T.3 vibration, T.4 shock, T.5 external short circuit and T.7 overcharge, and says T.6 and T.8 are not required for the small rechargeable batteries it tested [R03-S56]. I could not open the UN Manual itself.
- **Charging approaches.** [FACT] Nav2's docking server (`opennav_docking`) provides a docking action server with plugin-defined docks, a `SimpleChargingDock` plugin with options such as `use_battery_status` and `use_external_detection_pose`, staging-pose parameters and condition nodes such as `IsBatteryCharging` [R03-S57]. [FACT] MiR250 docks to charging markers with stated positioning accuracies and up to 44 s docking time for the slowest marker type [R03-S58]. [REC] Contact docking: use charger-to-robot digital handshake (CAN or similar) before enabling charge current, and design contacts for the pack's 0.5C-class current (about 52 A in the worked example) with arc/inrush limits; contact-pad design data from a connector manufacturer was not read — **[UNRESOLVED]**. Wireless charging was not researched.

---

## 12. Compute and the real-time layer

- **NVIDIA Jetson Orin.** [FACT] Orin NX modules: up to 100 TOPS with power configurable 10–25 W; Orin Nano modules: up to 40 TOPS, 7–15 W; the same page's spec table lists higher AI figures (Orin NX 16GB 157 TOPS, Orin Nano 8GB 67 TOPS) and power options up to 40 W for NX, an inconsistency with the headline text that I did not resolve; interfaces include CAN (1× on NX/Nano modules, 2× on AGX), USB 3.2, 1 GbE, 4× MIPI CSI cameras (virtual channels subject to change); NX/Nano module is 69.6 × 45 mm [R03-S19]. The page also announces a "Jetson Orin Nano 2" and Jetson Thor T3000/T2000 modules, whose specifications I did not open (**[UNRESOLVED]**).
- **ROS 2 on Jetson.** [FACT] Isaac ROS 5.0.0 (2026-09-21) migrated to ROS 2 Lyrical as the supported distribution, and the Getting Started page lists Jetson Orin on JetPack 7.2 (with Ubuntu 24.04 for x86_64) as an officially tested platform with 128+ GB NVMe recommended [R03-S20, R03-S21]. [REC] Pin ROS 2 distribution, JetPack and Isaac ROS versions together; the earlier Isaac ROS lines targeted other distro/JetPack combinations [R03-S21], and a single wrong pairing is a common integration failure. Distribution policy is R-software's decision.
- **Raspberry Pi 5.** [FACT] BCM2712 quad-core Cortex-A76 at 2.4 GHz, up to 16 GB LPDDR4X, 5 V/5 A USB-C power, Gigabit Ethernet, PCIe 2.0 x1, 40-pin GPIO, operating temperature 0–70 °C, production until at least January 2036 [R03-S22]. [REC] Adequate for a non-AI gateway/diagnostic node; the 0–70 °C range and USB-C power input make it less suitable for an in-chassis main compute in a cold store without extra design work (cold storage is not a researched requirement).
- **ROS 2 platform support.** [FACT] REP 2000 defines tiered platform support, with Ubuntu on amd64 and arm64 at Tier 1 for recent distributions [R03-S23] (I read the master copy's tables; latest distro rows were not individually verified). [UNRESOLVED] No x86 industrial PC datasheet could be read (the Neousys page blocked automated reads), so no x86 board is in the shortlist; the need is a fanless, wide-voltage-input (9–36 V or similar) unit.
- **Microcontroller layer.** [FACT] micro-ROS targets mid-range 32-bit MCUs needing tens of kB of RAM, with FreeRTOS, Zephyr and NuttX support; its hardware page lists officially supported boards (e.g. Renesas EK-RA6M5, ESP32, Arduino Portenta H7) and community boards including STM32-based Olimex STM32-E407 and an STM32L4 Discovery kit, with STM32CubeMX integration [R03-S24]. [REC] Use a hard real-time MCU (e.g. STM32 class) for wheel/steer motor loops, brake and watchdog handling, connected to the compute module via CAN or Ethernet; micro-ROS is a convenience bridge, not a safety layer. No STM32 datasheet was read (**[UNRESOLVED]**).

---

## 13. Payload mechanisms and mechanical interfaces

- **What public documentation exists.** [FACT] The MiR250 specification documents a top plate of 5 mm anodized aluminium, mounting dimensions "equal to robot footprint", maximum payload 250 kg and payload placement via centre-of-mass directions in the user guide [R03-S58]. The MiR250 Shelf Carrier guide covers a shelf-carrier top module with payload up to 300 kg that requires a traction kit and forbids operation on slopes [R03-S59]; the MiR250 spec lists a Hook (cart towing) variant [R03-S58]. These are commercial user guides, not engineering design data; no public CAD-level or load-path design data for conveyor tops, lifts, tuggers or forks was found — **[UNRESOLVED]**.
- **Pallet dimensions.** [FACT] EPAL Euro pallet: 1200 mm × 800 mm × 144 mm, about 25 kg, safe working load 1500 kg, stack limit 5500 kg on the bottom pallet [R03-S60]. [FACT] ISO 6780:2003 (preview only; full text not inspected) lists rectangular plan sizes 1200×800, 1200×1000 and 1219×1016 mm, and square sizes 1067×1067, 1100×1100 and 1140×1140 mm [R03-S61]. [CALC] A 1.2×0.8 m footprint is 0.96 m². A fully loaded pallet (1500 kg safe working load + about 25 kg pallet = 1525 kg) is about 5–6 times the 250–300 kg payload figures of the MiR250 [R03-S58, R03-S59] (1525/300 = 5.1; 1525/250 = 6.1), so a pallet-handling robot is a different mass class from the 200 kg example.
- **Structural and CoG practice.** [REC] Specify CoG-height limit and payload-containment as inputs to the tip-over formulas in section 10.1; require payload strapping or friction-pad surface when `μ_payload < a_b/g`. For raised or lift payloads, tip-over likely governs (section 10.2). [FACT] The Shelf Carrier guide says the integrator must determine payload limit, weight distribution and safe fastening, and make brake tests with a full payload [R03-S59].
- ISO 3691-4 and related stability/braking requirements: see R08 (no standard text was read here).

---

## 14. Comparison and trade-off summary

| Decision | Option A | Option B | Key trade-off | Basis |
|---|---|---|---|---|
| Reference chassis | Differential drive | Mecanum | Simplicity, load per wheel and PU tread vs lateral motion and slip/odometry penalties | Sections 2.2, 2.3 |
| Drive electronics | CiA 402 industrial drives (Oriental BLV-R) | ODrive-class CAN FD drives | Industrial interface and STO listing vs open docs and ROS 2 package; ROS CiA 402 stack self-declared not production-ready | Section 5 |
| Cell chemistry | LFP (EVE LF105) | NMC (Molicel P45B) | 170 vs 242 Wh/kg cell level; cycle-life figures stated at 0.5C/25 °C | Section 11 |
| Safety scanner | SICK nanoScan3 | Hokuyo UAM-05LPA | 3 m vs 5 m protective range; both Type 3, SIL 2, PL d; SICK has a documented ROS 2 driver, Hokuyo's was not located | Section 7 |
| Compute | Jetson Orin | Pi 5 / x86 IPC | AI throughput and Isaac ROS vs temperature range, simplicity | Section 12 |

---

## 15. Implications and recommendations for Valtoryn (all [REC])

1. **Make the hardware abstraction explicit about chassis kinematics.** Define a `Chassis` interface exposing: chassis type, wheel geometry, kinematic forward/inverse functions (formulas in 2.1), per-chassis odometry covariance, calibration routine and limits (wheel speed, acceleration, steering limits). Differential drive is the first implementation; mecanum/swerve/Ackermann should be addable without changing planner interfaces. Rationale: the equations differ only in the `H` matrix/steering mapping [R03-S25].
2. **Choose differential drive for the first reference chassis, with PU-tread drive wheels and low-friction casters**, because it has the best-documented public commercial precedent (MiR250: two TPU drive wheels plus casters, 250 kg) [R03-S58, R03-S59]. This is a judgement, not a validated finding.
3. **Define the sizing spreadsheet from section 10 as a repository artifact**, with every input labelled assumed/measured/datasheet and with source IDs, so the first hardware build is sized from decisions, not from this example.
4. **Plan for measured, not assumed, rolling resistance and friction**, because no concrete-floor `Crr` or powered-vehicle derating factor was found.
5. **Isolate safety from ROS.** Treat safety scanners, STO, brakes and the BMS protection path as hardware/safety-controller functions; ROS only reads diagnostics (the SICK ROS driver publishes raw data [R03-S03]). Details in R08.
6. **Treat CiA 402 as a first-class but unproven interface**, schedule bench conformance tests per drive, and do not take `ros2_canopen` maturity for granted [R03-S49].
7. **Pick a certified pack/BMS path early** (IEC 62619 lists AGVs as motive applications [R03-S55]) and require the supplier's UN 38.3 test summary.
8. **Document the ROS 2 distribution/JetPack/Isaac ROS pin** in the BOM.
9. **Mechanical modularity:** define a top-plate interface (bolt pattern, CoG limits, electrical/CAN connector) before designing any lift or conveyor module.

---

## 16. Parameters Valtoryn still needs to decide or measure

| Parameter | Decide / measure | Why it matters | Where used |
|---|---|---|---|
| Target payload (kg) and payload classes | Decide | Sets wheel, motor and pack size; tip-over | 10.1 |
| Robot mass, CoG height and range with payload | Measure (CAD then weighbridge/tilt test) | Tip-over, axle load split | 10.1 item 12 |
| Footprint and wheel track / wheelbase | Decide | Aisle width, stability, odometry resolution | 2, 10 |
| Max speed, max acceleration, emergency deceleration | Decide with R08 | Stopping distance, field size, motor sizing | 10 |
| Floor type, friction `μ`, roughness, floor flatness, joints | Measure on target floor | Traction, wheel tread, caster size | 3 |
| Rolling-resistance `Crr` for chosen wheel+floor | Measure | Motor sizing, runtime | 10 |
| Slope/ramp and dock-threshold requirements | Decide | Traction, motor peak | 10 |
| Drive wheel diameter, tread, durometer, load rating | Decide with supplier (powered rating) | Rating basis is manual operation in catalogues | 3.1 |
| Gear ratio, gearhead type, backlash tolerance | Decide | Torque, speed, efficiency | 4.3 |
| Bus voltage (24 V vs 48 V class) | Decide | Drive availability, cable current, safety extra-low-voltage rules (R08) | 5, 11 |
| Motor type, continuous/peak torque, thermal duty cycle | Measure duty cycle then choose | RMS torque vs rating | 10.2 |
| Drive interface (CiA 402 vs CAN FD) | Decide after bench test | Integration risk | 5 |
| Encoder type, resolution, mounting accuracy | Decide / measure | Odometry | 6 |
| Calibration procedure and target odometry accuracy | Decide / measure | Localization budget | 2.2 |
| Sensor set, mounting heights, blind zones | Decide with R04/R08 | Coverage | 7, 9 |
| IMU bias stability and calibration | Measure (Allan variance) | Heading drift | 8 |
| Compute platform, power mode, cooling, ambient range | Decide, benchmark | Perception load, thermal | 12 |
| Average and peak power, runtime and charge/dock cycle | Measure | Pack size, charger | 10.2, 11 |
| Cell chemistry, pack configuration, BMS, charger, dock contacts | Decide | Safety, life | 11 |
| Operating temperature range (e.g. cold store) | Decide | Battery, lubricants, electronics | 11, 12 |
| Ingress protection class and washdown | Decide | Connectors, sensors | 7 |
| Payload module interface (mechanical + electrical) | Decide | Modularity | 13 |
| Brake design (dynamic brake, parking brake) | Decide with R08 | Safe stop, holding on slope | 5, R03-S59 |

---

## 17. Candidate-component shortlist

Candidates for comparison and methodology only. **No selection is made.** "ROS 2 evidence" = documentation/README opened in this session; nothing was installed or tested.

| Category | Manufacturer / part | Key datasheet values (source) | Interface | ROS 2 support evidence |
|---|---|---|---|---|
| Safety LiDAR | SICK nanoScan3 | 3 m protective, 275°, 0.17°, PL d / SIL 2 / Type 3, 24 V, 3.9 W, IP65, 0.67 kg [R03-S01] | I/O, EFI-pro, EtherNet/IP CIP Safety | `sick_safetyscanners2` supports nanoScan3 Ethernet variants (raw scans only) [R03-S03] |
| Safety LiDAR | Hokuyo UAM-05LPA-T301 | 5 m protection, 270°, PL d / SIL 2, 24 V, 6 W typical, 0.8 kg, IP65 [R03-S02] | OSSD, RS-485, USB, 100BASE-TX | [UNRESOLVED] none located |
| Nav LiDAR | Slamtec RPLIDAR S2E | 30 m (90 % refl.), 32 kHz, 0.12°, ±30 mm, 9–28 V [R03-S04] | Ethernet UDP | `sllidar_ros2` lists S2E [R03-S05] |
| 3D LiDAR | Ouster OS1 Rev8 | 90 m @10 %, 44° V, 10–20 W, 9–58 V, 500 g [R03-S06] | 1000BASE-T | Official `ouster-ros` driver [R03-S07] |
| 3D LiDAR | Livox Mid-360 | 40 m @10 %, 360°×59°, 200 kpts/s, 6.5 W, 9–27 V, 265 g [R03-S08] | 100BASE-TX | `livox_ros_driver2` [R03-S09] |
| IMU | Bosch BMI088 | ±24 g, 160–190 µg/√Hz; ±2000 °/s, 0.014 °/s/√Hz, offset ±1 °/s [R03-S10] | SPI/I²C (chip) | Via board/driver; not researched |
| Depth camera | RealSense D435 / D455 (D400 family) | 87°×58°, Min-Z 280 / 520 mm, <2 % Z-accuracy at stated range [R03-S13] | USB | `realsense-ros` [R03-S14] |
| Depth camera | Orbbec Gemini 335 / 335L | 90°×65°, 50 / 95 mm baseline, 0.26–3 m optimal, <3 W [R03-S15] | USB-C | ROS 2 wrapper docs listed [R03-S16] |
| Depth camera | Luxonis OAK-D Pro | 75 mm baseline, ~0.8–12 m ideal, 4 TOPS on-board [R03-S17] | USB | DepthAI ROS driver [R03-S18] |
| Motor | maxon EC-i 52 (574740, 18 V) | 399 mNm cont., 11.5 A, 4360 rpm, 89 % max efficiency, 823 g [R03-S38] | Hall; needs drive | Via drive |
| Gearhead | maxon GP 52 C (223081) | 4.3:1, 4 Nm cont., 91 %, backlash 0.6° [R03-S39] | Mechanical | n/a |
| Integrated drive | Oriental Motor BLV-R | 60–400 W, 15–55 V, 1–4000 r/min, STO [R03-S41] | Modbus RTU, CANopen | CiA 402 route via `ros2_canopen` [R03-S49] (not verified for this drive) |
| Motor controller | ODrive S1 / Pro | 12–50.5 V / 15–58 V; 40/80 A and 70/120 A (nominal/peak) [R03-S43, R03-S44, R03-S45] | CAN/CAN-FD, USB, UART, many encoders | `odrive_node` ROS 2 package [R03-S46] |
| Motor controller | Roboteq SBLG2360T | 60 V, 2×16 A continuous, STO listed [R03-S47] | USB, CAN | [UNRESOLVED] |
| Encoder | Same Sky AMT21 | 12/14-bit absolute, 0.2°, RS-485 [R03-S50] | RS-485 | Via drive/MCU |
| Encoder | AS5047P | 14-bit, ±0.8° INL optimum, 28 000 rpm [R03-S51] | SPI, ABI | Via drive/MCU |
| Cell | EVE LF105 (LFP) | 3.2 V, 105 Ah, 1980 g, 4000 cycles @25 °C [R03-S52] | n/a | n/a |
| Cell | Molicel INR-21700-P45B (NMC) | 4.5 Ah, 45 A cont., 242 Wh/kg [R03-S53] | n/a | n/a |
| BMS IC | TI BQ76952 | 3–16S, <10 mV accuracy, I²C/SPI [R03-S54] | I²C, SPI, HDQ | n/a |
| Compute | NVIDIA Jetson Orin NX / Nano | 100 / 40 TOPS, 10–25 W / 7–15 W [R03-S19] | CAN, USB 3.2, GbE, CSI | Isaac ROS 5.0 targets Orin on JetPack 7.2 + ROS 2 Lyrical [R03-S20, R03-S21] |
| Compute | Raspberry Pi 5 | 4×A76, 5 V/5 A, 0–70 °C [R03-S22] | GbE, USB 3, PCIe x1, GPIO | ROS 2 arm64 Tier-1 platform class [R03-S23] |
| MCU | STM32 family (micro-ROS-listed boards) | Not datasheet-verified | CAN, UART, Ethernet | micro-ROS hardware page [R03-S24] |
| Wheel | Blickle Extrathane PU series | 92 Shore A, floor pressure 8.0 N/mm² ref. [R03-S32, R03-S33] | Mechanical | n/a |
| Wheel | Colson polyurethane | Capacity basis: manual use [R03-S34] | Mechanical | n/a |

---

## 18. Limitations of this research

- No hardware was built, bought or tested. Every number is a manufacturer claim or a calculation.
- Several PDF datasheets (SICK, MiR, Faulhaber, Blickle, EVE, D400) lost table alignment in text extraction. Pairings of labels and values for MiR250 (drive-wheel diameter 200 mm and caster 125 mm, TPU, friction 0.60–0.80, step tolerance, battery and charging rows), D400 minimum-Z/accuracy columns, and the nanoScan3 per-variant columns were inferred from row/column order and should be re-checked against the original PDFs before use.
- Some datasheets were read from distributor-hosted copies (EVE LF105 via a battery reseller; RPLIDAR S2E via Seeed; Hokuyo spec via the Hokuyo USA download link; MiR documents via third-party hosts). Revisions may differ from the vendor's current release.
- Standards (IEC 62619, ISO 6780, UN 38.3, ISO 3691-4) were not read in full; only catalogue pages, previews, or regulator summaries.
- Hub motors, VESC, TDK/InvenSense and Xsens IMUs, x86 industrial PCs, STM32 datasheets, heavy-duty mecanum wheels, swerve modules and wireless charging were not researched to datasheet level.
- Rolling resistance on concrete, caster swivel resistance and powered-vehicle wheel derating factors are not established.
- ROS 2 distribution naming (Lyrical, Kilted, Jazzy, Humble) was read from vendor pages; the authoritative distribution timeline belongs to the software workstream.

## 19. Unresolved questions

1. Concrete-floor rolling coefficient and powered-vehicle derating for PU wheels (needs supplier test data or a measurement).
2. Heavy-duty mecanum or omni wheel datasheets with load rating and roller material.
3. Swerve module availability and a ROS 2 swerve controller (none located in pages read).
4. Hub motor manufacturer datasheets with torque-speed curves and bearing loads.
5. Multi-stage planetary gearhead efficiency and backlash for the 20:1 example ratio.
6. Hokuyo UAM-05LPA ROS 2 integration; any x86 industrial PC suitable for a mobile platform (wide DC input, temperature).
7. BMI088 bias instability (Allan variance), and alternative IMU datasheets.
8. D435i/D455 end-of-life status (RealSense spin-out confirmed; no EOL notice found on pages read).
9. Specifications of Jetson Orin Nano 2 and Jetson Thor T2000/T3000, announced on the NVIDIA page and not opened.
10. UN 38.3 full text and IEC 62619 requirements (paywalled or not retrievable).
11. VESC controller datasheets from a primary source.
12. Public engineering documentation for conveyor-top, lift, tugger and pallet-fork modules beyond MiR user guides.
13. Contact-dock connector current ratings and arc/inrush design data.
14. CiA 402 conformance of specific drives and the production-readiness timeline of `ros2_canopen`.

---

## 20. Sources

| ID | Title | Organization / author | URL | Published / revision date | Accessed | What it supports |
|---|---|---|---|---|---|---|
| R03-S01 | nanoScan3 product information (8024822) | SICK AG | https://www.sick.com/media/docs/5/75/075/product_information_nanoscan3_en_im0087075.pdf | 2023-04-21 (document footer) | 2026-11-07 | nanoScan3 range, FoV, resolution, safety levels, power, size |
| R03-S02 | Safety Laser Scanner UAM-05LPA-T301 Specification (C-62-00050) | Hokuyo Automatic Co., Ltd. (via Hokuyo USA) | https://www.hokuyo-usa.com/download_file/view/cec0fa09-ad7d-4d2d-9fa8-c9b580a6f596/236 | 2023-12-11 | 2026-11-07 | Hokuyo UAM-05LPA ranges, safety levels, power, interfaces |
| R03-S03 | sick_safetyscanners2 README | SICK AG (GitHub) | https://raw.githubusercontent.com/SICKAG/sick_safetyscanners2/master/README.md | n/a (not stated on page) | 2026-11-07 | ROS 2 driver support for microScan3/nanoScan3/outdoorScan3 |
| R03-S04 | RPLIDAR S2E datasheet v1.3 | Slamtec (hosted by Seeed Studio) | https://files.seeedstudio.com/wiki/SLAMRadar/SLAMTEC_rplidar_datasheet_S2E_v1.3_en.pdf | v1.3 (date n/a) | 2026-11-07 | S2E range, sample rate, resolution, interface, supply |
| R03-S05 | SLAMTEC LIDAR ROS2 Package README | Slamtec (GitHub) | https://raw.githubusercontent.com/Slamtec/sllidar_ros2/main/README.md | n/a (not stated on page) | 2026-11-07 | ROS 2 driver coverage of RPLIDAR models |
| R03-S06 | OS1 Mid-Range High-Resolution Imaging Lidar datasheet (Rev8 v4p0) | Ouster | https://data.ouster.io/downloads/datasheets/datasheet-rev8-v4p0-os1.pdf | Rev 8 / v4.0 (date n/a) | 2026-11-07 | OS1 range, FoV, power, interface, mass |
| R03-S07 | Official ROS driver for Ouster sensors | Ouster (GitHub) | https://raw.githubusercontent.com/ouster-lidar/ouster-ros/ros2/README.md | n/a (not stated on page) | 2026-11-07 | ROS 2 distribution coverage |
| R03-S08 | Specs - Mid-360 LiDAR Sensor | Livox | https://www.livoxtech.com/mid-360/specs | n/a (not stated on page) | 2026-11-07 | Mid-360 range, FoV, power, interface, IMU |
| R03-S09 | Livox ROS Driver 2 README | Livox-SDK (GitHub) | https://raw.githubusercontent.com/Livox-SDK/livox_ros_driver2/master/README.md | n/a (not stated on page) | 2026-11-07 | ROS 2 OS/distro support; production-use caveat |
| R03-S10 | BMI088 Data Sheet (BST-BMI088-DS000-19) | Bosch Sensortec | https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmi088-ds001.pdf | Rev 1.9, January 2024 | 2026-11-07 | Accelerometer and gyroscope noise, offsets, drifts |
| R03-S11 | RealSense Completes Spin Out from Intel, Raises $50 Million | Intel Capital / RealSense | https://www.intelcapital.com/realsense-completes-spin-out-from-intel-raises-50-million-to-accelerate-ai-powered-vision-for-robotics-and-biometrics/ | 2025-07-11 | 2026-11-07 | RealSense independent company status |
| R03-S12 | D430 Series (D435) product page | RealSense | https://www.realsenseai.com/products/depth-camera-d435i/ | n/a (not stated on page) | 2026-11-07 | Current RealSense product line, D435 listing, operating range note |
| R03-S13 | Intel RealSense Product Family D400 Series Datasheet (337029-017) | Intel Corporation (hosted by RealSense) | https://www.realsenseai.com/wp-content/uploads/2023/10/Intel-RealSense-D400-Series-Datasheet-September-2023.pdf | Revision 017, September 2023 | 2026-11-07 | D400 baseline, FOV, min-Z, accuracy |
| R03-S14 | ROS Wrapper for RealSense Cameras README | RealSense (GitHub) | https://raw.githubusercontent.com/IntelRealSense/realsense-ros/ros2-master/README.md | n/a (not stated on page) | 2026-11-07 | ROS 2 wrapper, repo migration, ROS 1 unsupported |
| R03-S15 | Orbbec Gemini 330 Series Datasheet V1.1 | Orbbec | https://d1cd332k3pgc17.cloudfront.net/wp-content/uploads/2024/06/Orbbec-Gemini-330-Series-Datasheet-v1.1-2.pdf | V1.1 (upload path 2024-06) | 2026-11-07 | Gemini 335/335L specs |
| R03-S16 | Gemini 330 Series Datasheet (Overall) — documentation index | Orbbec | https://www.orbbec.com/docs/g330-orbbec-gemini-330-series-datasheet/ | n/a (not stated on page) | 2026-11-07 | Existence of ROS2 wrapper documentation |
| R03-S17 | OAK-D Pro | Luxonis | https://docs.luxonis.com/hardware/products/OAK-D%20Pro | n/a (not stated on page) | 2026-11-07 | OAK-D Pro depth, baseline, processing |
| R03-S18 | DepthAI ROS Driver | Luxonis | https://docs.luxonis.com/software-v3/depthai/ros/driver | n/a (not stated on page) | 2026-11-07 | ROS 2 driver for OAK cameras |
| R03-S19 | NVIDIA Jetson Orin | NVIDIA | https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/ | n/a (not stated on page) | 2026-11-07 | Orin module TOPS, power, interfaces, size |
| R03-S20 | Getting Started — Isaac ROS | NVIDIA | https://nvidia-isaac-ros.github.io/getting_started/index.html | n/a (not stated on page) | 2026-11-07 | Supported Jetson/JetPack/ROS 2 distro |
| R03-S21 | Release Notes — Isaac ROS | NVIDIA | https://nvidia-isaac-ros.github.io/releases/index.html | Isaac ROS 5.0.0 dated 2026-09-21 | 2026-11-07 | Release history and distro migration |
| R03-S22 | Raspberry Pi 5 Product Brief (RP-008348-DS) | Raspberry Pi Ltd | https://pip.raspberrypi.com/documents/RP-008348-DS-raspberry-pi-5-product-brief.pdf | n/a (not stated on page) | 2026-11-07 | Pi 5 specs, power, temperature, lifetime |
| R03-S23 | REP 2000 — ROS 2 Releases and Target Platforms | Open Robotics / ROS community (ros-infrastructure/rep) | https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-2000.rst | n/a (master branch) | 2026-11-07 | ROS 2 platform tiers, Ubuntu amd64/arm64 |
| R03-S24 | Supported Hardware — micro-ROS | micro-ROS project | https://micro.vulcanexus.org/docs/overview/hardware/ | n/a (not stated on page) | 2026-11-07 | micro-ROS MCU/board support, RTOSes |
| R03-S25 | Modern Robotics: Mechanics, Planning, and Control (preprint, ch. 13) | Kevin M. Lynch, Frank C. Park | https://hades.mech.northwestern.edu/images/7/7f/MR.pdf | May 3, 2017 (preprint) | 2026-11-07 | Differential, mecanum, car-like kinematics; odometry |
| R03-S26 | diff_drive_controller (ros2_controllers, Jazzy) | ros2_control project | https://control.ros.org/jazzy/doc/ros2_controllers/diff_drive_controller/doc/userdoc.html | n/a (not stated on page) | 2026-11-07 | ROS 2 differential drive controller parameters/odometry |
| R03-S27 | mecanum_drive_controller (ros2_controllers, Jazzy) | ros2_control project | https://control.ros.org/jazzy/doc/ros2_controllers/mecanum_drive_controller/doc/userdoc.html | n/a (not stated on page) | 2026-11-07 | ROS 2 mecanum controller |
| R03-S28 | steering_controllers_library (ros2_controllers, Jazzy) | ros2_control project | https://control.ros.org/jazzy/doc/ros2_controllers/steering_controllers_library/doc/userdoc.html | n/a (not stated on page) | 2026-11-07 | Bicycle/tricycle/Ackermann kinematics support |
| R03-S29 | UMBmark: A Benchmark Test for Measuring Odometry Errors in Mobile Robots | J. Borenstein, L. Feng (Univ. of Michigan) | https://johnloomis.org/ece445/topics/odometry/borenstein/paper60.pdf | SPIE Conference on Mobile Robots, Oct 1995 | 2026-11-07 | Systematic/non-systematic odometry error sources |
| R03-S30 | Experimental kinematics for wheeled skid-steer mobile robots | A. Mandow et al. (Univ. of Málaga) | http://babel.isa.uma.es/_utils/downloads/logdownloads.php?u=jafma&t=pdf&f=downloads%2Fjafma%2Fpapers%2Fmandow2007ekw.pdf | IROS 2007 | 2026-11-07 | Skid-steer slip and ICR-based model |
| R03-S31 | Wheeled Mobile Robots: State of the Art Overview and Kinematic Comparison Among Three Omnidirectional Locomotion Strategies (abstract only read) | L. Tagliavini et al., J. Intell. Robot. Syst. 106, 57 | https://link.springer.com/article/10.1007/s10846-022-01745-7 | 2022 | 2026-11-07 | 4-mecanum / 3-omni / 2-swerve comparison scope |
| R03-S32 | Infobox Blickle wheel series | Blickle | https://www.blickle.us/en-us/guide/info-box-wheel-series | n/a (not stated on page) | 2026-11-07 | Tread hardness, floor pressure values |
| R03-S33 | Wheels and castors for pallet trucks (catalogue chapter 16) | Blickle | https://www.blickle.us/en-us/-/media/project/blickle/global-web/services/mediathek/katalogkapitel/pdf-dokumente/en/g16-chapter-16.pdf?fh=f92c7cddc922fe68c7ce4c467f5f4090 | n/a (not stated on page) | 2026-11-07 | HTH series tread, load range, temperature |
| R03-S34 | How to Select the Proper Caster & Wheel (Colson Catalog 2020) | Colson Group | https://resources.colsongroup.com/colson/pdfs/sections/ColsonCatalog2020_R3_How_To_Select.pdf | 2020 catalogue | 2026-11-07 | Capacity-rating basis, wheel selection |
| R03-S35 | Rolling Resistance and Industrial Wheels (White Paper No. 11) | Hamilton Caster | https://www.hamiltoncaster.com/Portals/0/blog/White%20Paper%20Rolling%20Resistance.pdf | n/a (not stated on page) | 2026-11-07 | Rolling force formula, PU coefficient example |
| R03-S36 | Mecanum Wheel Specs | AndyMark | http://files.andymark.com/MecanumWheelSpecSheet.pdf | n/a (not stated on page) | 2026-11-07 | 6/8/10 in mecanum load ratings |
| R03-S37 | 6 Inch Mecanum Wheels | Kornylak Corporation | https://www.kornylak.com/wheels/mecanumwheel_6inch.html | n/a (not stated on page) | 2026-11-07 | 6 in mecanum load capacity and materials |
| R03-S38 | EC-i 52 Ø52 mm, brushless, 180 W, with Hall sensors (574740) | maxon group | https://www.maxongroup.us/maxon/view/product/motor/ecmotor/EC-i/574740 | catalog page version 2025 | 2026-11-07 | EC-i 52 electrical, thermal, mechanical data |
| R03-S39 | Planetary Gearhead GP 52 C Ø52 mm, 4–30 Nm (223081) | maxon group | https://www.maxongroup.us/maxon/view/product/gear/planetary/GP52/223081 | catalog page version 2025 | 2026-11-07 | Gearhead ratio, torque, efficiency, backlash |
| R03-S40 | Technical Information (17th edition) | Dr. Fritz Faulhaber GmbH & Co. KG | https://www.faulhaber.com/fileadmin/Import/Media/EN_TECHNICAL_INFORMATION.pdf | 17th edition, 2022 | 2026-11-07 | DC motor relations (torque/speed constants, power) |
| R03-S41 | BLV Series R Type Brushless DC Motor & Driver Packages | Oriental Motor USA | https://www.orientalmotor.com/brushless-dc-motors-gear-motors/brushless-dc-motors-gear-motors-blv-r-type.html | n/a (not stated on page) | 2026-11-07 | BLV-R powers, voltage, interfaces, STO |
| R03-S42 | 10 Standard Features for AGV / AMR Powertrain Applications | Oriental Motor USA | https://www.orientalmotor.com/brushless-dc-motors-gear-motors/technology/brushless-dc-motors-features-for-agv-drivetrain.html | n/a (not stated on page) | 2026-11-07 | BLV features, supply range, gearhead options |
| R03-S43 | ODrive S1 Datasheet | ODrive Robotics | https://docs.odriverobotics.com/v/latest/hardware/s1-datasheet.html | docs v0.6.12 (2026) | 2026-11-07 | S1 voltage, current, CAN, environment |
| R03-S44 | ODrive Pro Datasheet | ODrive Robotics | https://docs.odriverobotics.com/v/latest/hardware/pro-datasheet.html | docs v0.6.12 (2026) | 2026-11-07 | Pro voltage, current, CAN |
| R03-S45 | ODrive Comparison Table | ODrive Robotics | https://docs.odriverobotics.com/v/latest/hardware/odrive-comparison.html | docs v0.6.12 (2026) | 2026-11-07 | Feedback/control interfaces, power ratings |
| R03-S46 | ROS2 Package for ODrive | ODrive Robotics (GitHub) | https://raw.githubusercontent.com/odriverobotics/ros_odrive/main/README.md | n/a (not stated on page) | 2026-11-07 | ROS 2 packages and requirements |
| R03-S47 | SBLG2360T Brushless DC Motor Controller | Roboteq | https://www.roboteq.com/products/products-brushless-dc-motor-controllers/sblg2360t-393-detail | n/a (not stated on page) | 2026-11-07 | Roboteq ratings and interfaces |
| R03-S48 | CiA 402: CANopen device profile for drives and motion control | CAN in Automation (CiA) | https://www.can-cia.org/can-knowledge/cia-402-series-canopen-device-profile-for-drives-and-motion-control | n/a (not stated on page) | 2026-11-07 | CiA 402 scope, IEC 61800-7 relation, interoperability caveat |
| R03-S49 | ROS2 CANopen README | ROS-Industrial (GitHub) | https://raw.githubusercontent.com/ros-industrial/ros2_canopen/master/README.md | n/a (not stated on page) | 2026-11-07 | ros2_canopen maturity statement, distros |
| R03-S50 | AMT21 Series Datasheet | Same Sky (CUI Devices) | https://www.sameskydevices.com/product/resource/amt21.pdf | n/a (not stated on page) | 2026-11-07 | Absolute encoder resolution, accuracy, interface |
| R03-S51 | AS5047P 14-Bit On-Axis Magnetic Rotary Position Sensor datasheet | ams OSRAM (hosted by Infineon) | https://www.infineon.com/assets/row/public/documents/30/49/infineon-as5047p-datasheet-en.pdf | n/a (not stated on page) | 2026-11-07 | Magnetic encoder resolution, INL, interfaces |
| R03-S52 | LF105 Product Specification (RD-LF105-S01-LF) | EVE Power Co., Ltd. (copy hosted by batteryfinds.com) | https://batteryfinds.com/wp-content/uploads/2023/09/EVE-LF105-105Ah-3.2V-LiFePO4-Prismatic-Battery-Cell-SpecificationDatasheet.pdf | Mar 2022 (document cover) | 2026-11-07 | LFP cell capacity, voltage, mass, cycle life, charge rate |
| R03-S53 | Product Data Sheet INR-21700-P45B (v1.2) | Molicel (E-One Moli Energy) | https://www.molicel.com/wp-content/uploads/INR21700P45B_1.2_Product-Data-Sheet-of-INR-21700-P45B-80109.pdf | Version 1.2 | 2026-11-07 | NMC cell capacity, current, energy density |
| R03-S54 | BQ76952 3-Series to 16-Series High Accuracy Battery Monitor and Protector (SLUSE13B) | Texas Instruments | https://www.ti.com/lit/ds/symlink/bq76952.pdf | January 2020, revised November 2021 | 2026-11-07 | BMS monitor/protector features |
| R03-S55 | IEC 62619:2022 (catalogue page) | International Electrotechnical Commission | https://webstore.iec.ch/en/publication/64073 | 2022-05-24 | 2026-11-07 | Standard scope incl. AGV (full text not read) |
| R03-S56 | Research summary – Evaluation and analysis of substandard lithium-ion batteries by UN 38.3 testing | Transport Canada | https://tc.canada.ca/en/dangerous-goods/publications/lithium-battery-transport-research/research-summary-evaluation-analysis-substandard-lithium-ion-batteries-383-testing | n/a (not stated on page) | 2026-11-07 | UN 38.3 test list (T.1–T.8) |
| R03-S57 | Docking Server — Nav2 documentation | Nav2 project | https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/core_servers/configuring_docking_server/ | n/a (not stated on page) | 2026-11-07 | ROS 2 docking server and charging dock plugin |
| R03-S58 | MiR250 specifications (v2.81) | Mobile Industrial Robots A/S (hosted by Shelley) | https://shelley.com/wp-content/uploads/2024/07/MiR250-Specifications-2.81.pdf | 2024-06-28 | 2026-11-07 | Public commercial AMR benchmark data |
| R03-S59 | MiR250 Shelf Carrier User Guide v1.1 (SW 2.9.0) | Mobile Industrial Robots A/S (hosted by Astor) | https://download.astor.com.pl/dokumentacja/Mobile%20Industrial%20Robots/Opcje/MiR%20Shelf/Podr%C4%99czniki/mir250-shelf-carrier-user-guide-11-en.pdf | 07/2020 | 2026-11-07 | Safety scanner layout, brakes, STO, payload warnings |
| R03-S60 | EPAL Euro Pallet | EPAL (European Pallet Association) | https://www.epal-pallets.org/eu-en/load-carriers/epal-euro-pallet | n/a (not stated on page) | 2026-11-07 | EUR/EPAL pallet dimensions and load |
| R03-S61 | ISO 6780:2003 (preview) | ISO (preview hosted by iTeh Standards) | https://cdn.standards.iteh.ai/samples/30524/ec0a6ce1ee454b98b00c8551c8ecb7df/ISO-6780-2003.pdf | 2003-12-01 (corrected 2004-04-15) | 2026-11-07 | Standard pallet plan dimensions (preview only) |
| R03-S62 | University Physics Volume 1, 6.2 Friction | OpenStax | https://openstax.org/books/university-physics-volume-1/pages/6-2-friction | n/a (not stated on page) | 2026-11-07 | Static friction bound μs·N |
| R03-S63 | University Physics Volume 1, 12.1 Conditions for Static Equilibrium | OpenStax | https://openstax.org/books/university-physics-volume-1/pages/12-1-conditions-for-static-equilibrium | n/a (not stated on page) | 2026-11-07 | Torque equilibrium for tip-over |
| R03-S64 | University Physics Volume 1, 3.4 Motion with Constant Acceleration | OpenStax | https://openstax.org/books/university-physics-volume-1/pages/3-4-motion-with-constant-acceleration | n/a (not stated on page) | 2026-11-07 | Constant-acceleration kinematics (braking distance) |
| R03-S65 | Precision Servo Hub Motor for Mobile Robot (vendor catalogue, weak source) | DMK Motor | https://www.dmkmotor.com/servo-hub-motor/ | n/a (not stated on page) | 2026-11-07 | Hub motor size/power/torque ranges (vendor claim only) |

**Sources that could not be inspected** (not cited for any claim):
- UN Manual of Tests and Criteria, Section 38.3 (unece.org) and PHMSA lithium battery test summary pages — access blocked (HTTP 403 / unreachable).
- maxon catalogue PDF (maxongroup.com) — HTTP 403 (product pages on maxongroup.us were read instead).
- Oriental Motor EU BLV-R PDF (orientalmotor.eu) — HTTP 403.
- Neousys Nuvo-9000 product page — blocked for automated reads.
- intelrealsense.com D435 page — connection failed.
- Slamtec RPLIDAR S2 key-parameters page — renders by script; no values extracted (S2E datasheet used instead).
- Jetson Orin Nano datasheet (openzeka-hosted PDF) — text not extractable.
- Orbbec ROS 2 wrapper README — repository path returned 404.
- ISO 3691-4, ISO 13849, IEC 61496 — paywalled; deferred to R08.
- Tagliavini et al. full text — abstract only.
