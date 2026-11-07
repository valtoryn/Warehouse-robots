# Hardware interface specification — Valtoryn platform

> **Status:** Proposed specification. Nothing is implemented; no connector or protocol is selected finally.
> **Basis:** HARDWARE_ABSTRACTION.md, R02 §3 (identity/versioning), R03 §5/§11/§13, R05 §3, R08 §4.
> Rule: every interface is declared in the module manifest (provides/requires, units, limits, identity
> expectations) and verified at bring-up gate C3. Safety-related signals are read-only to ROS.

## 1. Interface classes

| Class | Bus candidates | Command direction | State direction |
|---|---|---|---|
| Actuators (wheel/steer/lift) | CANopen CiA 402; CAN/CAN-FD; EtherCAT (future) | velocity/effort/position | position, velocity, torque/current, status word, faults |
| Drive safety signals | Dedicated safety channel (not ROS) | none from ROS | STO status, SS1 status, safe-speed state — read-only |
| Sensors — safety LiDAR | Vendor safety fieldbus (e.g. SICK EFI-pro / CIP Safety; Hokuyo OSSD+Ethernet) | field configuration via engineering tool, not ROS | protective/warning field status — safety domain; raw scan optional to ROS |
| Sensors — nav | Ethernet UDP (RPLIDAR S2E), 1000BASE-T (OS1), 100BASE-TX (Mid-360), USB-C (cameras) | configuration | scan/cloud/image/IMU data |
| IMU | SPI/I²C on carrier board or USB/Ethernet on smart IMU | calibration params | accel/gyro @ documented ODR |
| Power | Pack CAN/RS-485 (BMS); charge dock handshake (CAN or vendor) | charge enable only after handshake | SoC, pack V, current, temps, faults, charge state |
| Compute interconnect | GbE (primary), USB 3.2, CAN, CSI/MIPI, PCIe | n/a | n/a |
| MCU real-time link | CAN or Ethernet (to be decided with compute, HA-5) | motor current/torque loop refs optional | encoder feedback, brake/watchdog status |
| Payload modules | Defined top-plate interface: mechanical pattern + power + CAN/Ethernet + (optional) safety I/O | module-specific commands via ros2_control System | pose/identity/load state |
| Charging dock | Contact pads + digital handshake (CAN class) | dock/undock via Nav2 docking server | charge state, alignment quality |

## 2. Standardisation rules

1. **Units:** SI per REP-103; angles rad internally. Declared per interface in manifest.
2. **Frames:** REP-105 (`base_link`, `odom`, `map`); sensor frames static in URDF relative to `base_link`.
3. **cmd_vel:** `geometry_msgs/TwistStamped` only, end to end (Nav2 ≥ Kilted, ros2_control drive controllers).
4. **Limits:** every command interface declares min/max; CM `enforce_command_limits` is the enforcement point;
   URDF 1.2 acceleration/jerk limits used where available (Lyrical).
5. **Identity:** each module exposes vendor/product/serial (or Valtoryn ID where designed) readable at
   bring-up; compared to manifest expectations (gate C3).
6. **Diagnostics:** every module publishes `diagnostic_updater` status; liveness via lifecycle bond.
7. **Safety:** protective signals never traverse ROS command topics; ROS reads state via a dedicated,
   documented channel owned by the safety-domain interface spec (HA-6, deferred to safety workstream).
8. **Determinism:** hard-RT loops (motor current, brake, watchdog) live on MCU or CM RT thread — never in
   Python or non-RT executor.

## 3. Per-class detail

### 3.1 Actuators / drives

- Interface contract (backend-agnostic): command = target velocity or effort (per manifest); feedback =
  position, velocity, torque/current estimate, status word, fault code; limits = max speed/accel/jerk,
  max current/torque, following-error window.
- Backends: CiA 402 object-dictionary profile (CiA 402-1 v5.x; IEC 61800-7 alignment [FACT R03-S48]) or
  CAN-FD vendor protocol (ODrive class). CiA 402 interchangeability is limited by optional functions
  [FACT R03-S48] — conformance must be tested per drive.
- STO/SS1: consumed as state; never commanded by ROS (R08 §4).

### 3.2 Sensors

- Safety LiDAR: protective-field configuration and safe outputs remain in the safety domain; ROS driver
  (e.g. `sick_safetyscanners2` for nanoScan3 Ethernet [FACT R03-S03]) may publish raw scans for perception —
  explicitly non-safety. Hokuyo UAM ROS 2 driver: unresolved.
- Nav sensors: standard `sensor_msgs` types (`LaserScan`, `PointCloud2`, `Image`, `Imu`, `Range`).
  Noise is injected in simulation per R05 §3.5 (SDF Gaussian baseline + measured structured degradation later).
- Cameras: depth+RGB; hardware sync where supported; IMU on camera optional.

### 3.3 Power

- Pack: certified BMS with CAN/RS-485 telemetry (SoC, cells, temps, faults) — gen-1 buys certified pack (R08 §3).
- Charge dock: mechanical + electrical contact design with inrush/arc limits; digital handshake precedes
  current enable; Nav2 `SimpleChargingDock` pattern [FACT R03-S57]. Contact ratings unresolved.
- Power budget: aux loads per R03 §10.2 A14 method (compute, scanners, cameras, MCU, drives idle).

### 3.4 Compute and MCU

- Compute module interface: defined carrier board or COM-express-style carrier with defined power, GbE,
  USB, CAN, camera CSI lanes; manifest declares module identity and power mode.
- MCU link: decision pending (HA-5); requirements: ≤1 ms cycle for motor loop option, encoder feedback,
  watchdog, brake control, safety-state read passthrough.

### 3.5 Payload modules

- Mechanical: top-plate bolt pattern + locating features; defined CoG envelope and retention method
  (strap/friction surface) per R03 §10.1 formula 11.
- Electrical: power rail(s) + CAN/Ethernet + optional safety I/O; payload identity EEPROM or bus-reported ID.
- Software: payload appears as ros2_control System component + manifest entry; payload state (present,
  mass class, geometry) published for footprint/limit switching (FR-A3).

## 4. Simulation parity contract

Each interface has a simulated counterpart implementing identical semantics:

| Real | Simulated |
|---|---|
| Drive (CiA 402/CAN-FD) | `gz_ros2_control` joint interfaces + Valtoryn motor/drive model (R05 §3.3) |
| Encoder | Joint state interfaces with noise/quantisation model |
| Safety LiDAR | GPU lidar with SDF noise model; **protective function NOT simulated** — sim models perception-only scans |
| Battery/BMS | Valtoryn power model behind HAL (Gazebo battery alone insufficient, R05 §3.7) |
| Safety state channel | Simulated safe-state injector for fault scenarios only |
| Payload | Separate rigid body per payload manifest (mass, COM, inertia) (R05 §3.4) |

## 5. Open items

| ID | Item |
|---|---|
| HI-1 | Connector/cable standard per class (M12/X-coded, EtherCAT-style, custom) — decide with mechanical design |
| HI-2 | MCU↔compute link protocol (HA-5) |
| HI-3 | Valtoryn module ID memory format (HAT-style atoms vs simpler) — when hardware exists |
| HI-4 | Charge-dock connector ratings and handshake protocol |
| HI-5 | Safety-state channel physical definition (safety workstream, HA-6) |
| HI-6 | EtherCAT evaluation for modular machines (fieldbus identity/topology precedent, R02 §3.7) — defer until mechanical modularity phase |
