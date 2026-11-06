# R08 — Safety, Standards and Verification
> **Status:** Research document — proposed findings, nothing here is implemented.
> **Workstream:** R08 · **Last verified:** 2026-11-07 · **Evidence legend:** see below

## Read this first (mandatory framing)

1. **Passing simulation tests is not physical safety certification.** Simulation, software-in-the-loop and hardware-in-the-loop (HIL) results are engineering evidence for earlier rungs of an evidence ladder (section 5.1). None of them establishes that a physical machine is safe, and none of them is a conformity assessment under any regulation. [FACT: the EU describes CE marking as following a conformity assessment procedure prescribed by the applicable legislation, with testing of the product — R08-S32, R08-S33].
2. **Nothing in the Valtoryn project is safety-rated.** No Valtoryn software, hardware design, simulation, or document has been assessed, tested or certified against ISO 3691-4, ISO 13849-1, IEC 62061, IEC 61508, ANSI/A3 R15.08, UL 3100, or any other standard. No physical hardware exists yet. Every statement about Valtoryn below is a proposal.
3. **This is not legal advice and not a compliance determination.** Whether any product or deployment complies with any law or standard, which regulation applies, and which conformity route is required are determinations for a qualified assessor (notified body, accredited test lab, or competent safety engineer/lawyer in the relevant jurisdiction).
4. **The standards themselves were mostly not read.** Almost all standards are paywalled. This document relies on public catalogue pages (ISO, IEC, BSI), publicly visible previews, official EU texts, manufacturer manuals and secondary commentary. The table in section 1.2 states exactly what was and was not inspected for each standard.

## Evidence legend

- **[FACT]** established by a cited source, always followed by a source ID such as [R08-S01]
- **[CALC]** derived by a shown calculation from cited or labelled inputs
- **[EST]** engineering estimate or assumption (basis stated)
- **[REC]** Valtoryn recommendation or proposal (engineering judgement, not established fact)
- **[UNRESOLVED]** could not be established; what would resolve it is stated

---

## 1. Scope and method

### 1.1 Scope

Safety requirements, standards and verification practice relevant to an open-source, modular autonomous warehouse robot platform whose first reference implementation is a differential-drive AMR (autonomous mobile robot), intended eventually for physical deployment, with later chassis types and possible mobile manipulation. The question asked of this workstream: what would a credible safety and verification approach look like, what do the standards and regulations publicly say, and where should the software/safety boundary sit.

### 1.2 What was actually inspected, per standard

"Catalogue" means the publisher's public product page (scope/abstract, edition, status, price, page count). No full standard text was purchased or read unless stated.

| Standard / regulation | What I inspected | What I could NOT inspect |
|---|---|---|
| ISO 3691-4:2023 | ISO catalogue page with full scope/abstract and status [R08-S01]; iTeh public preview of the CEN-adopted text: front matter, table of contents, Annex ZA correspondence table [R08-S41]; trade summaries [R08-S37, S39, S40] | Normative clauses 4–6 and Annexes A–E (zone tables, PLr table, test procedures) |
| ISO 3691-4:2020 (withdrawn edition) | ISO catalogue page [R08-S02]; TÜV Rheinland white paper summarising it [R08-S37] | Full text |
| ISO/DIS 3691-4 (next edition) | ISO committee page, abstract identical to 2023 edition, stage 40.60 [R08-S11] | Draft text; what changes |
| ISO 13849-1:2023 / :2015 | ISO catalogue pages [R08-S03, S04]; secondary PFH table [R08-S43] | Full text, categories, MTTFd/DC tables |
| ISO 13849-2:2012 | ISO ICS listing [R08-S10]; iTeh preview excerpt of the validation clause (clause 9.1) [R08-S46] | Rest of the standard; the FDIS replacement |
| ISO 12100:2010 | ISO catalogue page [R08-S05]; ICS listing showing ISO/DIS 12100.3 [R08-S10] | Full text |
| ISO 13850:2015 | ISO catalogue page [R08-S06] | Full text |
| ISO 13855:2024 | ISO ICS listing (stage only) [R08-S10]; EU Official Journal decision listing it [R08-S31]; Leuze summary of the formula [R08-S36]. The ISO page itself was blocked to automated reads | ISO abstract page; full text; approach-speed tables |
| IEC 61496-3:2025 | IEC webstore page with full scope [R08-S17] | Full text; IEC 61496-1 |
| IEC 62061:2021 (+A1:2024, A2:2026) | IEC webstore page and BSI page, both with scope [R08-S18, S19] | Full text |
| IEC 61508-1, -3 | IEC webstore abstracts [R08-S21, S22] | Full text; SIL tables |
| IEC 60204-1 | IEC webstore page (scope, change list) [R08-S20] | Full text; stop-category definitions (taken from NIST paper instead) |
| IEC 61800-5-2 | Not inspected at all. Safe-stop function descriptions come from trade/manufacturer pages [R08-S48, S49, S50] | Standard and its abstract |
| ISO/TS 15066:2016, ISO 10218-1/-2:2025 | ISO catalogue pages incl. scope exclusions [R08-S07, S08, S09] | Full text |
| ANSI/A3 R15.08-1/-2/-3 | ANSI blog on Part 1 (R2026) [R08-S12]; press release on Part 2 [R08-S13]; trade article on Part 3 (weak) [R08-S14] | The standards; A3 store pages |
| UL 3100 | ANSI webstore scope paragraph for Ed.1-2021, marked "Historical" [R08-S15]; UL Solutions webinar page [R08-S16] | The standard; the current edition (if any) |
| IEC 62619:2022 | IEC webstore scope [R08-S25] | Full text |
| UN 38.3 | Unofficial reproduction of the 6th revised edition text [R08-S26] | Current edition (Rev. 8) |
| UL 2271 / UL 1973 | UL Solutions service page that lists them [R08-S59] | Scope text of either standard |
| IEC 61882 (HAZOP), IEC 60812 (FMEA) | IEC webstore abstracts [R08-S23, S24] | Full text |
| Regulation (EU) 2023/1230 | EUR-Lex full text as fetched [R08-S27] | The corrigendum itself (see 2.13.1 and Unresolved) |
| Machinery Directive 2006/42/EC | Only indirectly: Commission pages and implementing decisions [R08-S28, S30, S31] | The Directive text |

### 1.3 Method

Web research on 2026-11-07 using official catalogue pages, EUR-Lex, a current SICK safety-laser-scanner manual (revision dated 2026-07-23), certification-body white papers, and academic/government papers. Where two sources disagreed I recorded the disagreement instead of picking one. Worked calculations use a published manufacturer formula with every non-sourced input labelled as an assumption.

---

## 2. Findings

### 2.1 The standards landscape and edition status (verified 2026-11-07)

| Standard | Current edition per public catalogue | Status notes | Source |
|---|---|---|---|
| ISO 3691-4 (driverless industrial trucks and their systems) | Edition 2, 2023-06, 74 pages, published; the 2020 edition is withdrawn | Stage 90.92 "to be revised"; ISO/DIS 3691-4 is in the consultation stage (40.60). EN ISO 3691-4:2023 is cited in the EU Official Journal under the Machinery Directive | [FACT] [R08-S01, S02, S11, S30] |
| ISO 13849-1 (safety-related parts of control systems) | Edition 4, 2023-04, 152 pages; 2015 edition withdrawn | 2023 edition does not apply to low-demand mode; does not cover security (cyber) aspects; says mobile machinery may have specific requirements in a type-C standard. EN ISO 13849-1:2023 referenced in OJ | [FACT] [R08-S03, S04, S30] |
| ISO 13849-2 (validation) | 2012 edition, stage 90.92 | A replacement (ISO/FDIS 13849-2, "Application of principles for the design and validation", stage 50.00) is under development | [FACT] [R08-S10] |
| ISO 12100 (risk assessment and risk reduction) | 2010; reviewed and confirmed 2022 | ISO/DIS 12100.3 in development | [FACT] [R08-S05, S10] |
| ISO 13850 (emergency stop function) | 2015, reviewed and confirmed 2020; 11 pages | Under periodic review (stage 90.60) | [FACT] [R08-S06] |
| ISO 13855 (positioning of safeguards) | ISO 13855:2024 (stage 60.60); 2010 edition withdrawn | EN ISO 13855:2024 is listed by Commission Implementing Decision (EU) 2026/2015 of 4 Sept 2026 | [FACT] [R08-S10, S31] |
| IEC 61496-3 (ESPE: AOPDDR, i.e. safety laser scanners) | Edition 4.0, 2025-08-14 (supersedes 2018) | Technical revision; Type 2 detection requirements changed | [FACT] [R08-S17] |
| IEC 62061 | Edition 2.0, 2021-03-22; amendment 1 (2024); BSI shows A2:2026 published 2026-06-30 | Sector standard under IEC 61508; excludes design of complex programmable electronic subsystems | [FACT] [R08-S18, S19] |
| IEC 61508-1 / -3 | Edition 2.0, 2010 | Basic safety publication | [FACT] [R08-S21, S22] |
| IEC 60204-1 | Edition 6.1 (2016+A1:2021) | Clause 9 revised to address safe torque off, emergency stop and control-circuit protection | [FACT] [R08-S20] |
| ISO 10218-1 / -2 | 2025 editions (Part 1 Edition 3; Part 2 Edition 2), published 2025-02 | 2011 editions replaced; EN ISO 10218-1/-2:2025 listed in OJ by Decision 2026/2015 | [FACT] [R08-S08, S09, S31] |
| ISO/TS 15066 | 2016, confirmed 2022 | Marked "to be revised"; replacement ISO/AWI 15066-1 under development | [FACT] [R08-S07] |
| ANSI/A3 R15.08-1 | ANSI/A3 R15.08-1-2020 (R2026): a reaffirmation with no technical changes | Formerly ANSI/RIA R15.08-1-2020; editorial redesignation after RIA became A3 | [FACT] [R08-S12] |
| ANSI/A3 R15.08-2 | 2023 (Part 2: IMR systems and applications) | Press release dated 2023-10-09 | [FACT] [R08-S12, S13] |
| ANSI/A3 R15.08-3 | 2026 (Part 3: use of IMR applications) | Date per trade article (weak): store listing 2026-04-23, announced 2026-09-29 | [FACT, weak source] [R08-S14] |
| UL 3100 | Ed.1-2021 shown as "Historical" on ANSI webstore | Whether a later edition exists is not established | [UNRESOLVED] [R08-S15] |

Observation: several edition changes happened recently (ISO 3691-4:2023, ISO 13849-1:2023, ISO 13855:2024, ISO 10218:2025, IEC 61496-3:2025). Secondary material older than about 2023 (including the TÜV paper, section 2.2) describes superseded text. [REC] Any Valtoryn safety document must carry an "edition watch" table and treat all clause numbers from secondary sources as unverified until checked against a purchased copy.

### 2.2 ISO 3691-4: what it is and what it covers

**Scope (from the ISO abstract).** [FACT] The standard specifies safety requirements and means of verification for driverless industrial trucks and their systems. The abstract names "autonomous mobile robot" as one example of a truck (trucks as defined in ISO 5053-1:2020). A driverless truck system comprises the control system (on the truck and/or separate), guidance means and power system, but requirements for power sources are not covered. It also covers trucks with automatic modes, rider capability, additional manual modes, and a maintenance mode. It excludes trucks solely guided mechanically and remote-controlled trucks. It treats the condition of the operating zone as significant and specifies preparation of zones in Annex A. Hazards are those over all life phases listed in Annex B. [R08-S01]

**Explicit exclusions in the 2023 abstract.** [FACT] Noise, vibration, ionising/non-ionising radiation, laser radiation; severe conditions (extreme climate, freezers, strong magnetic fields); nuclear; trucks intended for public zones (ISO 13482 is pointed to); public roads; explosive atmospheres; military; hygiene-specific operation; ionising radiation environments; transport of persons other than intended riders; hazardous loads (molten metal, acids, radiating materials); rider positions elevated above 1 200 mm; trailers towed behind the truck; elevated operator trucks; and trucks manufactured before publication. [R08-S01]

**Implications.**
- [FACT] Battery/power-source requirements are explicitly outside ISO 3691-4 [R08-S01], although the Machinery Regulation has battery and automatic-charging provisions (2.11, 2.13.1).
- [FACT] Laser radiation hazards are listed as not covered [R08-S01]; the SICK manual treats laser class separately [R08-S34].
- [FACT] The standard is aimed at indoor industrial trucks; it is not a public-space robot standard.

**Structure (from the publicly previewable table of contents).** [FACT] Clause 4 (safety requirements and protective measures) includes 4.2 braking system, 4.3 speed control (4.3.1 overspeed detection), 4.4 automatic battery charging, 4.5 load handling, 4.6 steering, 4.7 stability, 4.8 protective devices and complementary measures (4.8.1 emergency stop, 4.8.2 detection of persons in the path), 4.9 modes of operation (automatic, manual, maintenance), 4.11 safety-related parts of the control system, 4.12 electromagnetic immunity, 4.13 conveyors, 4.14 warning systems. Clause 5 is verification (5.2 tests for detection of persons, 5.3 stability tests, 5.4 fitness for purpose with structural and dynamic tests). Clause 6 is information for use (instruction handbook, marking, commissioning). Annex A (normative) is preparation of operating zones; Annex B (informative) list of significant hazards; Annex E (normative) is the verification table. [R08-S41]

**Content reported by secondary sources (clause-level detail NOT verified against the standard).**
- Required performance levels: a TÜV Rheinland paper on the 2020 edition reports 27 listed safety functions with minimum PLr per ISO 13849-1, including PLr d for control of the braking system and for personnel detection, and PLr b for parking-brake control [R08-S37]. Intertek (June 2026, 2023 edition) says a table in the standard lists typical safety-related functions, associated risks and minimum PLs, and that it must not substitute for an application-specific risk assessment [R08-S39]. The two sources cite different table numbers (Table 1 vs Table 3), consistent with renumbering between editions. [UNRESOLVED] the exact table, its rows, and the 2023 values; resolve by purchasing ISO 3691-4:2023.
- Zones: TÜV reports that the 2020 edition added a "confined zone" to the restricted and hazard zones of EN 1525 and ties zone classification to whether personnel detection is active [R08-S37].
- Braking: ANSI summarises that the braking system must operate on loss of power, apply automatically on loss of speed or steering control, and be able to stop the truck within the operating range of the personnel detection specified by the manufacturer (speed, friction, floor, gradient, rated load) [R08-S40].
- Overspeed: stop is initiated when speed exceeds the manufacturer's rated speed [R08-S40].
- Emergency stop: required, conforming to ISO 13850:2015 [R08-S40].
- Detection of persons: TÜV reports the wording changed from generating a signal (EN 1525) to stopping before contact with a stationary person, which makes the braking system part of the assessed safety function [R08-S37]. A vendor blog (weak) reports test pieces of a 200 mm × 600 mm vertical cylinder and a 70 mm × 400 mm horizontal cylinder, and a 0.3 m/s limit when detection is muted [R08-S42]. [UNRESOLVED] both figures; confirm in the standard (clauses 4.8.2, 5.2, Annex A).
- Limitation noted by TÜV: humans approaching the truck or stepping sideways into its path are described as outside the scope of the 2020 edition [R08-S37]. [UNRESOLVED] whether this still holds in the 2023 edition.
- Dematic (a manufacturer) says the updated standards require other measures when proximity sensors are muted to handle pallets, such as ultra-slow movement, limited mute time and layout-based controls [R08-S58] (manufacturer statement, not verified).

**Regulatory status in the EU.** [FACT] Commission Implementing Decision (EU) 2024/1329 of 13 May 2024 (published 15.5.2024) adds EN ISO 3691-4:2023 (row 189a) and lists EN ISO 13849-1:2023 among references for Directive 2006/42/EC [R08-S30]. The CEN foreword states the EN was approved 5 May 2023 and supersedes EN ISO 3691-4:2020; Annex ZA maps clauses 4–6 to Machinery Directive essential requirements, with a warning that presumption of conformity lasts only while the reference stays in the OJ list and that other Union legislation may apply [R08-S41]. Annex ZA maps, for example, the requirement 1.2.1 (safety and reliability of control systems) to clauses 4.2, 4.3, 4.5, 4.6, 4.8, 4.9, 4.11, and 3.3.3 (travelling function) to 4.2, 4.5, 4.8.1, 4.8.2, 4.9.3, 4.9.4. [R08-S41] [UNRESOLVED] Whether and when EN ISO 3691-4 will be cited under Regulation (EU) 2023/1230: a search-result snippet of a Commission page suggested a new implementing decision for the Regulation was being prepared, but that page was not opened. Resolve via the Commission's harmonised-standards page for the Machinery Regulation.

**ISO 3691-4 as a Type-C standard.** [FACT] TÜV describes it as a Type C standard for driverless industrial trucks, with the three pillars of operating environment, hazards/risk, and correct implementation of protection systems [R08-S37]. Intertek describes ISO 12100 as still required for hazards not dealt with in the standard and warns against treating ISO 3691-4 as a complete solution, listing common AGV safety-case failures: over-reliance on certified subsystems, superficial ISO 12100 use, wrong PLr allocation, missing degraded/fault-mode behaviour, and insufficient system-level validation [R08-S39].

### 2.3 Functional-safety framework: ISO 13849-1, IEC 62061, IEC 61508

**ISO 13849-1:2023.** [FACT] Specifies a methodology and requirements for design and integration of safety-related parts of control systems (SRP/CS) that perform safety functions, including software design; high-demand and continuous modes; technology-neutral; does not specify which safety functions or required performance levels apply; no specific security measures (refers to ISO/TR 22100-4 and IEC/TR 63074 for security effects on safety) [R08-S03]. The 2015 edition's catalogue entry shows its notes: examples of products that are parts of SRP/CS include relays, solenoid valves, position switches, PLCs, motor control units; compatibility with IEC 62061; and, for embedded software at PLr e, reference to IEC 61508-3 [R08-S04].

**Performance level and PFH.** [FACT, weak secondary source] One trade page gives the ISO 13849-1:2023 PFH ranges as: PL a 1e-5 to <1e-4 per hour; PL b 3e-6 to <1e-5; PL c 1e-6 to <3e-6; PL d 1e-7 to <1e-6; PL e <1e-7 [R08-S43]. A second trade page gives different, apparently inconsistent thresholds for PL b and PL c (PL b <3e-5, PL c <1e-5) [R08-S44]. **Contradiction between sources; not resolved.** [UNRESOLVED] confirm against ISO 13849-1:2023 Table 3 or IFA/SISTEMA documentation. [FACT] PFH alone does not establish a PL; architecture category, MTTFd, diagnostic coverage, common-cause failure measures and systematic-failure measures all apply [R08-S43, R08-S45]. This is visible in a real product: the SICK microScan3 Core I/O lists PFH 8e-8 per hour yet claims only PL d with Category 3 [R08-S34] (the PFH value alone would sit in the PL e band by the table above, so the architecture limit governs).

**Tooling.** [FACT] IFA (DGUV) provides SISTEMA, a free tool to model SRP/CS architectures and compute PL and PFH from category, MTTFd, DCavg and CCF; its main versions map to standard revisions (v1.x to the 2008 edition, v2.x to 2015, v3.x to 2023) [R08-S45].

**IEC 62061:2021.** [FACT] Machinery-sector standard within IEC 61508; for design, integration and validation of safety-related control systems for machines not portable by hand while working; high/continuous demand; design of complex programmable electronic subsystems is not in scope and is left to IEC 61508 or linked standards. The BSI text of scope adds that systems on chip and microcontroller boards count as complex programmable electronic subsystems. The 2021 edition added a functional safety plan, parametrization requirements, periodic testing, software use cases, independence requirements for software verification and validation, and a shift from SILCL to maximum SIL of a subsystem [R08-S18, S19]. It excludes electrical shock hazards (see IEC 60204-1) and security measures (see IEC TS 63074) [R08-S19].

**IEC 61508.** [FACT] IEC 61508-1 is a basic safety publication on E/E/PE systems carrying out safety functions, intended to enable sector standards [R08-S21]. IEC 61508-3:2010 covers software forming part of a safety-related system or used to develop one: software safety functions and systematic capability must be specified; lifecycle phases and activities apply; measures and techniques are graded against required systematic capability; support tools (design, translators, testing, configuration management) are included; modification requirements apply [R08-S22]. [REC] Conceptually: software safety is a process-and-evidence discipline (requirements, design, verification independence, configuration control, tool qualification), not a property that emerges from code quality or test coverage alone.

**SIL/PL correspondence.** [FACT, weak] A trade page notes PL d and SIL 2 share the same PFH interval but says a design cannot simply be relabelled between standards [R08-S43].

**Implication for a custom safety controller.** [FACT] A safety function that needs a bespoke microcontroller board is, per IEC 62061's scope note, a complex programmable electronic subsystem handled under IEC 61508-style development [R08-S19]. [REC] Valtoryn should not develop its own safety MCU firmware as part of the platform; it should specify and integrate pre-certified safety components (section 4).

### 2.4 Risk assessment and hazard analysis methods

**ISO 12100:2010.** [FACT] Basic terminology, principles and methodology for safety in machine design: principles of risk assessment and risk reduction, procedures for identifying hazards and estimating/evaluating risks across life-cycle phases, hazard elimination or sufficient risk reduction, and guidance on documentation and verification. Intended also as a basis for type-B and type-C standards. Does not deal with risk to domestic animals, property or environment. [R08-S05] ISO/TR 14121-2 (practical guidance on risk assessment methods) and ISO/TR 22100-5 (implications of AI/machine learning) exist per the ISO ICS listing (titles only; not read) [R08-S10].

**Methods (credible descriptions found).**

| Method | What the sources say | Fit for Valtoryn |
|---|---|---|
| HAZOP (IEC 61882:2016) | Guide for HAZOP studies of systems using guide words; covers study definition, preparation, examination sessions, documentation and follow-up; includes a procedural HAZOP case study [R08-S23] | [REC] Good for operating procedures and interfaces: docking, pallet hand-off, charging, door/lift interaction, fleet traffic messages |
| FMEA/FMECA (IEC 60812:2018) | Establishes how items or processes might fail and the local/global effects; applicable to hardware, software, processes including human action; generic, gives no specific safety guidance; alternative RPN calculations and criticality-matrix method [R08-S24] | [REC] Use on the safety layer hardware to feed MTTFd/DC inputs and on mechanical brake/drive-train |
| STPA (Leveson & Thomas) | Top-down control-structure method: define accidents and hazards, model control structure, identify unsafe control actions, identify causal scenarios; framed as a control problem rather than component reliability like FMEA [R08-S51]. An MIT Lincoln Laboratory review for the FAA found its key value is the structured framework for unsafe control actions and scenarios, but also that it does not give a structured way to derive requirements from scenarios and that it should supplement, not replace, an existing safety management system [R08-S51]. A Sandia presentation describes it as evaluating interfaces between components, software controllers and people [R08-S52] | [REC] Best fit for the autonomy/safety-layer/human-supervisor control structure, including software and fleet behaviour where failure is a flawed command, not a broken part |

[REC] Method stack: ISO 12100 as the umbrella process; use ISO 3691-4 Annex B (informative list of significant hazards, per TÜV and the preview TOC [R08-S37, S41]) as a completeness checklist, not as the analysis; STPA for the system control structure; HAZOP for procedures and message/interface deviations; FMEA for hardware of the safety layer. All results live in a versioned hazard log in the repository, with each hazard linked to a safety requirement and to the evidence-ladder level at which that requirement has been verified.

### 2.5 Emergency stop, stop categories and safe stopping

**ISO 13850:2015.** [FACT] Functional requirements and design principles for the emergency stop function independent of energy type; does not itself deal with reversal, limitation of motion, braking or disconnecting that can be part of the function; applies to all machines except where an emergency stop would not reduce risk and hand-held/hand-operated machines; electrical/electronic realisation is described in IEC 60204-1 [R08-S06]. IEC 60204-1:2016+A1:2021 has a revised Clause 9 covering safe torque off, emergency stop and control-circuit protection [R08-S20]. ISO 3691-4 requires an emergency stop function conforming to ISO 13850:2015 [R08-S40]; its clause 4.8.1 is the emergency stop [R08-S41].

**Stop categories (IEC 60204-1, as tabulated in a NIST paper).** [FACT] Stop 0: uncontrolled, power removed, brakes applied. Stop 1: controlled stop, power removed, brakes applied. Stop 2: controlled stop, power not removed, no brakes. [R08-S47] SEW-Eurodrive states STO (safe torque off per IEC 61800-5-2) corresponds to non-controlled stop category 0 and that the STO input must be switched off by an external safety controller or relay [R08-S49].

**Safe stop functions (secondary/trade sources; IEC 61800-5-2 itself not read).**
- STO: removes torque-producing power from the motor while the drive stays connected to supply; used for emergency stop and to prevent unexpected start [R08-S48].
- SS1: controlled ramp-down, then STO [R08-S48, S50]. SS2: controlled ramp-down, then safe operating stop (SOS) with the motor energised and zero speed monitored [R08-S48, S50].
- Rexel states SS2 is not acceptable for emergency stopping because the motor remains energised, while SS1 can be used [R08-S50] (trade claim).
- Related drive functions listed: SBC (safe brake control), SLS (safely limited speed), SSM, SDI, SLP [R08-S48].

**Wheeled-robot implication.** [EST] On a small differential-drive AMR, STO alone leaves the wheels free; the stopping distance then depends on friction and drive-train losses, or on a mechanical brake. [FACT] ISO 3691-4 (as summarised) requires brakes that apply on power loss and at loss of speed or steering control [R08-S40], and the MR requires that failure of the steering system on autonomous mobile machinery not affect safety [R08-S27, Annex III 3.3.5]. [REC] Treat the brake (spring-applied, power-off-engaged, with brake monitoring) and drive-integrated SS1/SLS/STO as first-class safety components, selected for stated stopping performance on the worst-case floor and load.

### 2.6 Protective sensing: safety laser scanners versus navigation lidar

**IEC 61496-3:2025 scope.** [FACT] Additional requirements for non-contact ESPE designed specifically to detect persons or parts of persons as part of a safety-related system, using active opto-electronic protective devices responsive to diffuse reflection (AOPDDR; 2D or 3D). It covers near-infrared devices (820 nm to 1 100 nm), relevant for minimum detectable object sizes from 30 mm to 200 mm; it does not specify detection-zone dimensions for a particular application; it does not address complex classification of detected objects; it does not cover outdoor application [R08-S17]. [REC] The "no classification" scope point matters: a perception stack that tries to distinguish a person from a box is not the protective function; the certified scanner detects any object of the specified size.

**SICK microScan3 Core I/O (manual revision 2026-07-23), what a certified scanner states.** All [FACT] [R08-S34]:
- Type 3 (IEC 61496), SIL 2 (IEC 61508 and 62061), Category 3, PL d (ISO 13849), PFH 8e-8 per hour, mission time 20 years; safe state on error is at least one OSSD in the OFF state.
- Intended use includes mobile hazardous-area protection (protection from automated guided vehicles). Improper use includes use as a physical guard, access control, detection of transparent items, outdoor use, underwater and explosive atmospheres.
- Field types: protective field, reference contour field, contour detection field (all safe switch-off, PL d) and warning field (not a safe switch-off). Protective ranges 4.0, 5.5 or 9.0 m by variant; warning field up to 40 or 64 m.
- Field sets are selected by monitoring cases driven by hardwired inputs, software bits or encoder speed; this particular device allows at most 2 monitoring cases, 8 field sets, 8 fields, 4 simultaneously monitored fields; scanning angle 275 degrees. The manual states the parts of the control that switch the active protective field need the same safety level as the safety function itself, often PL d or SIL 2.
- Antivalent (complementary) dual-channel inputs: an invalid combination switches all safety outputs OFF. A short- or cross-circuit on input cables can select the wrong monitoring case, so protected cable routing, a 0 s switch-on delay with sequence monitoring, and regular checks are recommended.
- Scan plane height must not exceed 200 mm for detection of lying persons; 150 mm is suggested in many cases.
- Response time tR = (tS + tI) × n + tO with tS 30/40/50 ms, tI 0 to 3 ms, n = multiple sampling (default 2, range 2 to 16), tO = 10 ms for OSSD pair 1; at least 70 ms for the 4.0 m and 5.5 m variants. A higher multiple sampling raises response time and the protective field must be re-sized.
- Tolerance zone TZ = 65 mm (4.0 and 5.5 m variants) or 100 mm (9.0 m variant); additional supplement ZR = 350 mm if a retroreflector lies within 6 m of the protective field.
- Restart interlock and external device monitoring (EDM) are provided; automated restart after 2 to 60 s is configurable.
- The manual requires a commissioning/regular-test checklist covering, among others, whether the protective device meets the required PL/SIL and PFH.

**Navigation lidar versus safety scanner.** [FACT, from the above] The safety scanner's value is a certified, fail-safe output with bounded response time and tolerance, not range or resolution of information. [EST] A typical navigation lidar has no OSSD outputs, no tested safe state, no certified response time and no tamper/contour monitoring. Treating it as the protective device would make the whole safety case depend on a non-safety component and on ROS 2. [REC] Two sensing roles, separately procured and wired: (a) safety scanners wired to the safety layer; (b) navigation sensors feeding ROS 2. Navigation sensing may reduce nuisance trips (availability) but must never be what stops the vehicle for personnel protection.

**Warning fields and speed adaptation.** [FACT] SICK describes using warning fields so vehicles slow before the protective field is entered, with encoder-based speed information used to switch fields so the protective field is rarely violated; extra scans (multiple sampling) lengthen response time which matters for AGV applications [R08-S35]. Dematic describes the same pattern (warning field reduces speed, protective field stops) [R08-S58, manufacturer claim].

### 2.7 Stopping-distance and protective-field sizing, with worked example

**Formula (SICK microScan3 manual, project planning).** [FACT] [R08-S34]
- Protective field length: SL = SA + TZ + ZR + ZF + ZB
- Stopping distance: SA = SBr + SAnF + SAnS
- SAnS = tR × Vmax (distance travelled during scanner response time)
- SBr braking distance and SAnF distance during vehicle-control response (incl. signal propagation) come from the vehicle documentation; ZB is a supplement for decreasing braking force from vehicle documentation.
- ZF: ground-clearance supplement; the manual gives a lump supplement of 150 mm for ground clearance under 120 mm and a graph for reductions.
- Protective field width: SB = FB + 2 × (TZ + ZR + ZF), FB being vehicle width; the effect of turning must be considered separately.
- Braking distance rises with the square of speed, not linearly.

[FACT] A SICK blog states that the vehicle must always stop fast enough that a person is not injured, and that of all parameters in the chain the stopping distance SA is usually the largest and most variable [R08-S35].

**Relationship to ISO 13855.** [FACT] The general minimum-distance formula in the 2010 edition is S = K × T + C; in the 2024 edition (per Leuze) S = K × T + DDS + Z, with K = 2 000 mm/s for walking (S > 500 mm) and 1 600 mm/s for hand/arm approach (S ≤ 500 mm) [R08-S36]. The NIST paper describes ISO/TS 15066 SSM's minimum protective distance as derived from the ISO 13855 form, adding terms for robot reaction distance, robot braking distance, intrusion distance and position uncertainties [R08-S47]. The SICK mobile-vehicle formula does not include a pedestrian approach-speed term. [UNRESOLVED] how ISO 3691-4:2023 treats pedestrian approach speed; TÜV lists approaching persons as a limitation of the 2020 edition [R08-S37].

**Worked example — all inputs labelled; this is an illustration, not a design value.**

| Input | Value | Provenance |
|---|---|---|
| Vmax | 1.5 m/s (also computed at 0.5, 1.0, 2.0) | [EST] typical warehouse AMR speed range; Valtoryn has no vehicle |
| Scanner config | scan time 30 ms, interference mode 1 (tI = 0), n = 2, OSSD output (tO = 10 ms) | [FACT] formula and ranges from [R08-S34]; settings chosen by me |
| Scanner response tR | (30 + 0) × 2 + 10 = 70 ms | [CALC] |
| Vehicle control + brake actuation latency (SAnF time) | 60 ms | [EST] assumed total for safety controller, output switching and brake engagement; must be measured |
| Braking deceleration | 1.5 m/s², loaded, worst-case floor | [EST] must be measured on the vehicle |
| TZ | 65 mm | [FACT] [R08-S34] (4.0/5.5 m variant) |
| ZR | 0 mm | [EST] assumes no retroreflector within 6 m |
| ZF | 150 mm | [FACT] [R08-S34] lump value for ground clearance under 120 mm; applied as a conservative choice |
| ZB | 10 % of SBr | [EST] allowance for brake fade; must come from vehicle data |

| Vmax (m/s) | SAnS = 0.070 × v (mm) | SAnF = 0.060 × v (mm) | SBr = v²/(2a) (mm) | SA (mm) | ZB (mm) | SL (mm) |
|---|---|---|---|---|---|---|
| 0.5 | 35.0 | 30.0 | 83.3 | 148.3 | 8.3 | 371.7 |
| 1.0 | 70.0 | 60.0 | 333.3 | 463.3 | 33.3 | 711.7 |
| 1.5 | 105.0 | 90.0 | 750.0 | 945.0 | 75.0 | 1 235.0 |
| 2.0 | 140.0 | 120.0 | 1 333.3 | 1 593.3 | 133.3 | 1 941.7 |

[CALC] at 1.5 m/s: SL = 945 + 65 + 0 + 150 + 75 = 1 235 mm. Raising multiple sampling from n = 2 to n = 3 gives tR = 100 ms and adds 45 mm at 1.5 m/s [CALC]. Assuming a 600 mm wide vehicle (FB, [EST]), field width SB = 600 + 2 × (65 + 0 + 150) = 1 030 mm [CALC].

Reading the table: the squared braking term dominates above about 1 m/s, so field length (and with it the footprint the vehicle needs, nuisance stops, and clearance) grows faster than speed [CALC]. Fixed supplements (TZ + ZF = 215 mm) dominate below about 0.5 m/s. Field-set switching by safely measured speed is therefore not an optimisation but the way to keep field length workable.

**Illustrative only (not a standard method).** [CALC] If a risk assessment concluded that a pedestrian walking toward the vehicle must be covered, an ISO 13855-style K × T term would add 1 600 mm/s × (0.070 + 0.060 + 1.0 s braking time) ≈ 1.8 m at 1.5 m/s (braking time 1.5/1.5 = 1.0 s). This shows the order of magnitude of the issue, not a requirement. [UNRESOLVED] what ISO 3691-4 requires here.

**Differential-drive notes.** [EST] In-place rotation sweeps the chassis corners through space not covered by a forward protective field; rotation-speed limits or rotational field sets are needed, and the manual says turning must be assessed separately [R08-S34]. A single 275 degree scanner at one corner cannot cover 360 degrees; multiple scanners or a different mounting is needed (rear and side coverage) [R08-S34 for 275 degrees].

### 2.8 Speed and separation monitoring, ISO/TS 15066, ISO 10218, and mobile manipulation

- [FACT] ISO/TS 15066:2016 specifies safety requirements for collaborative industrial robot systems, supplements ISO 10218-1/-2, applies to industrial robot systems as defined there, does not apply to non-industrial robots, and is marked "to be revised" with ISO/AWI 15066-1 in development [R08-S07].
- [FACT] NIST's analysis of the SSM method: the protective distance at time t0 sums the operator's travel during the robot's reaction and stopping time, the robot's travel before braking and while braking, plus intrusion distance C and position-uncertainty terms ZR (robot) and ZS (sensor); a safety-rated controlled stop is initiated when separation falls below S. NIST notes simple SSM may improve safety but not in all circumstances and stresses validating algorithms, models and sensor systems before relying on them [R08-S47].
- **Key exclusion for Valtoryn's long-term plans.** [FACT] The 2025 editions of ISO 10218-1 and -2 state they do not cover hazards related to mobility when robots or manipulators are fixed to or part of driverless industrial trucks or mobile platforms [R08-S08, S09]. ISO 10218-2 also excludes multi-purpose lifting devices such as forklift trucks [R08-S09]. Therefore, [FACT] neither ISO 10218 nor ISO/TS 15066 (which builds on it) covers a mobile manipulator as such.
- [UNRESOLVED] Which standard covers a mobile manipulator: whether ANSI/A3 R15.08-2 addresses manipulators on IMRs was not established from public sources; ISO 3691-4 abstract mentions load handling and conveyors but not manipulators. Resolve by reading R15.08-2 scope and a notified-body opinion.
- [REC] Treat mobile manipulation as a separate, later hazard study; do not reuse base-vehicle safety claims for a vehicle with an arm. Until a standards route is confirmed, use SSM-style logic only as an additional layer behind a proper safety function.

### 2.9 Fault handling, safe state and safety-rated hardware

- [FACT] Machinery Regulation Annex III 1.2.1 requires: a fault in hardware or logic of the control system must not lead to hazardous situations; errors in control logic must not; limits of the safety functions are established by the manufacturer's risk assessment and settings must not be modifiable by the machine or operators (including during a learning phase) where that could lead to hazard; reasonably foreseeable human errors must not lead to hazard; the machine must not start unexpectedly; it must not be prevented from stopping [R08-S27].
- [FACT] For control systems of machinery with self-evolving behaviour: no actions beyond defined task and movement space; recording of safety-related decision data retained one year; ability at all times to correct the machine to maintain inherent safety [R08-S27].
- [FACT] For autonomous mobile machinery, the control system must perform the safety functions by itself, even when actions are ordered through a remote supervisory function [R08-S27, Annex III 3.3].
- [FACT] SICK scanner safe state: OSSD(s) OFF; OSSDs tested at regular intervals; restart interlock and EDM [R08-S34].
- [FACT] Machinery "safety component" examples in Annex II include protective devices designed to detect the presence of persons and logic units to ensure safety functions [R08-S27].
- **Architecture options for the safety layer** (trade-off table in section 3).
- [REC] Define a single "safe state" per mode: stationary, brakes applied, drive torque removed (STO), load secured; define degraded modes (reduced speed with reduced fields) explicitly, because Intertek identifies missing degraded/fault-mode behaviour as a common AGV safety-case gap [R08-S39].
- [REC] Heartbeat/watchdog: the safety layer treats loss of the autonomy stack's heartbeat as a stop trigger. The ROS 2 Safety-Critical Working Group maintains software watchdog libraries based on DDS QoS and lifecycle nodes [R08-S53]; these are availability/diagnostic tools for the non-safety side, not a replacement for a safety-rated monitor.

### 2.10 Software, ROS 2 and AI/ML

- [FACT] The ROS 2 Safety-Critical Working Group's stated mission is to support creating safe robots using ROS; it produces tools, libraries (software watchdogs, C++ contracts), a safety patterns catalogue and a safety-critical ROS cookbook [R08-S53]. The repository describes no certification of ROS 2 against any functional-safety standard.
- [FACT, community statement] In an Open Robotics Discourse thread (2022-10), a community member states vanilla ROS 2 is not safety-certified and will most likely not be without significant work, that it can be used in systems requiring safety certification only if kept out of safety-critical paths with other systems responsible for safety, and that Apex.OS is a fork presented as certified (ISO 26262 SEooC up to ASIL D per the vendor's own post in the same thread) [R08-S54]. [UNRESOLVED] I found no official Open Robotics/OSRF statement; the evidence is the working-group scope plus this community statement. Resolve by asking the ROS TSC or the safety WG directly.
- [FACT] Research precedent: Safe-ROS (University of Manchester, 2025) separates an intelligent control system from an independent Safety System of Safety Instrumented Functions, demonstrated on a small robot with a Gazebo simulation and lab test [R08-S55]. That paper is an academic demonstration, not a certification.
- [FACT] Machinery Regulation Annex I Part A lists, as categories requiring third-party-type conformity procedures, "safety components with fully or partially self-evolving behaviour using machine learning approaches ensuring safety functions" and machinery embedding such systems (items 5 and 6); recital text says third-party assessment applies to ML-based safety functions and not to software incapable of learning or evolving [R08-S27]. ISO/TR 22100-5 addresses implications of AI/ML [R08-S10, title only].
- [FACT] Annex III 1.2.1(f): logs of interventions and versions of safety software uploaded after placing on the market must be enabled for five years [R08-S27].
- [REC] Rule: no learned model (perception, prediction, planner) may be the sole or primary means of executing a safety function. Learned components stay on the non-safety side of the boundary.

### 2.11 Lithium batteries

- [FACT] ISO 3691-4 does not cover power sources [R08-S01]. The Machinery Regulation requires that the battery can be disconnected with an easily accessible device and that automatic-charging batteries on autonomous mobile machinery prevent contact/collision hazards while moving to the charging station (Annex III 3.5.1) [R08-S27].
- [FACT] IEC 62619:2022 specifies safety requirements and tests for secondary lithium cells and batteries for industrial applications, including motive applications named as forklift, golf cart, automated guided vehicle, railway and marine (not road vehicles) [R08-S25].
- [FACT] UN 38.3 (transport): per the unofficial 6th-edition text, cells undergo tests T1–T6 and T8 and rechargeable batteries T1–T5 and T7; T1 altitude, T2 thermal, T3 vibration, T4 shock, T5 external short circuit, T6 impact/crush, T7 overcharge, T8 forced discharge; type changes such as altered protective devices (hardware and software) or a >20 % change in nominal energy create a new type requiring retesting [R08-S26]. [UNRESOLVED] differences in the current revision (the UNECE Rev. 8 files appeared in search results but were not opened).
- [FACT] UL Solutions' battery services page names UL 1973 as the standard for batteries in stationary and motive auxiliary power applications and UL 2271 for light electric vehicles, and mentions functional safety for battery management systems [R08-S59]. [UNRESOLVED] whether either is appropriate for an AMR traction battery; resolve with the battery vendor and a test lab.
- [FACT] UL 3100's listed evaluation areas include fire, shock, energy hazards, batteries and BMS, object detection and avoidance, risk assessment, functional safety, robotic payloads and product integration [R08-S16]; its scope text covers battery-operated mobile platforms with lead-acid or lithium batteries, indoors or outdoors in commercial/industrial environments [R08-S15].
- [REC] Buy a battery pack from a vendor with IEC 62619 and UN 38.3 reports and a BMS with documented safety functions; do not design cell-level packs in the first hardware generation.

### 2.12 Verification: physical test categories and HIL

**What ISO 3691-4 verification covers (publicly documented structure).** [FACT] Clause 5: tests for detection of persons (5.2), stability tests (5.3), fitness-for-purpose structural tests (5.4.2) and dynamic tests (5.4.3); clause 4.7.2 refers to a tilting platform stability test; Annex E is a normative verification table; clause 6.4 covers putting into service (commissioning) [R08-S41]. TÜV's summary of the assessment flow lists risk assessment per ISO 12100, SRP/CS assessment, type testing ("Test A & B"), stability, structural and functional verification, commissioning, warning system, instruction handbook and marking [R08-S37]. Applus+ lists EMC testing, electrical safety, risk assessment and control-software assessment for AGVs, and states it is not specifically accredited to the 2023 edition but can provide compliance via equivalent previous standards [R08-S38]; this illustrates that lab scope and accreditation must be checked. [UNRESOLVED] The detail of "Test A and B", the person-detection test procedure, and acceptance criteria require the standard.

**ISO 13849-2 validation methods.** [FACT] The 2012 text (iTeh preview) requires validation to demonstrate that required PLs and categories are met, principally by failure analysis on circuit diagrams, and where analysis is inconclusive by fault-injection tests on the actual circuit and components and/or simulation of control behaviour under faults by hardware and/or software models. Test options listed: fault injection into a production sample, into a hardware model, software simulation of faults, and subsystem failures such as power supplies; the instant of fault injection can be critical and worst case must be established [R08-S46]. [REC] This supports a HIL-with-fault-injection rung that prepares and de-risks the later physical fault tests, but the text positions simulation as complementary, not as a replacement for tests on the actual circuit.

**HIL for mobile robots (research precedent).** [FACT] The CAT Vehicle testbed (University of Arizona, 2018) is a ROS-based simulator with physics-based vehicle models and simulated sensors/actuators with a straightforward transition to hardware-in-the-loop testing [R08-S56]. Safe-ROS verified a safety function in simulation and lab testing [R08-S55]. Neither is a safety certification route.

**HIL scope proposal.** [REC] HIL rig contents: real safety controller and real drive/brake electronics with simulated wheel/encoder/scanner-output inputs; fault-injection capability (stuck OSSD, antivalent input mismatch, encoder loss, comms loss, power dips); timestamped measurement of reaction time from injected stimulus to STO/brake command. What HIL cannot show: real braking distance on real floors and loads, scanner detection behaviour on real objects/surfaces, EMC, thermal behaviour, mechanical strength, stability on slopes.

**Physical measurement requirements implied by the SICK/ISO method.** [FACT] The Leuze page states the total stopping time can only be determined accurately by measurement with stopping-time measuring devices, and that a safety inspection including stopping-time measurement may legally be done only by competent persons (as stated for their jurisdiction) [R08-S36]. [REC] Stopping distance is a measured property of each vehicle configuration (speed, load, floor, brake wear), recorded in the verification dossier; simulation-based braking models are only for planning.

### 2.13 Conformity routes and regulatory timelines

#### 2.13.1 EU Machinery Regulation (EU) 2023/1230

- [FACT] Adopted 14 June 2023, published OJ L 165, 29.6.2023; repeals Directive 2006/42/EC [R08-S27].
- [FACT] **Application date discrepancy.** The EUR-Lex text I fetched shows Article 54 saying the Regulation applies from 14 January 2027 [R08-S27]. The Commission's machinery page says the Regulation was adopted 14 June 2023, that a corrigendum fixed a clerical error in the application dates, and that it applies on a mandatory basis from 20 January 2027; machinery placed on the market before that date must comply with Directive 2006/42/EC [R08-S28]. DGUV says only the Directive applies until 19.1.2027 and only the Regulation from 20.1.2027 with no transitional phase [R08-S29]. [UNRESOLVED] I did not open the corrigendum. The best-supported date is **20 January 2027**; confirm against the corrigendum and the current consolidated version (EUR-Lex shows a consolidated version dated 27/07/2026 exists) before relying on a specific day.
- [FACT] The Regulation includes provisions for AI-powered safety functions and cyber-safety for compliance-relevant software data and safety control systems [R08-S28]. Annex III 1.1.9 requires protection against corruption (connected devices must not lead to hazard; hardware that carries safety-critical software data must be protected against accidental or intentional corruption) [R08-S27].
- [FACT] Annex III, section 3, for autonomous mobile machinery: definitions of autonomous mobile machinery (an autonomous mode in which all essential safety functions are ensured without permanent operator interaction), supervisor and supervisory function. The supervisory function may only allow remote stop, start, or move-to-safe-position; only when the supervisor can see the machine's movement and working area (directly or indirectly) and protective devices are operational; the machine may not operate if the supervisory function is inactive [R08-S27, 3.2.4]. Travelling function: autonomous mobile machinery must meet one or both, per risk assessment, of (i) operating in an enclosed zone with perimeter protection, (ii) being equipped with devices to detect humans, domestic animals or other obstacles that could create risk [R08-S27, 3.3.3]. Steering failure must not affect safety [3.3.5]. Instructions must specify intended travel, working areas and danger zones [3.6.3.3]. Movement must take account of risks of the area it moves in [3.3.2].
- [FACT] Conformity assessment (Article 25): machinery in Annex I Part A (includes ML safety components/embedded ML safety systems) uses EU type-examination plus conformity to type (modules B+C), full quality assurance (H), or unit verification (G), each involving a notified body; Part B (includes protective devices designed to detect the presence of persons, and logic units to ensure safety functions) may use internal production control (module A) only if designed per harmonised standards covering all relevant requirements, otherwise B+C, H or G; machinery not listed in Annex I uses module A [R08-S27]. Articles 26–42 on notified bodies apply earlier per Article 54 (14 January 2024 as printed) [R08-S27].
- [FACT] Technical documentation and the declaration of conformity must be kept for at least 10 years after placing on the market [R08-S27].
- [FACT] The Commission warns that voluntary certificates are not a recognised means of proving compliance and have no value for market-surveillance checks; only notified bodies issue certificates of compliance for harmonised products, within their notified area; NANDO lists bodies notified under both the Directive and the Regulation [R08-S28, S33].
- [FACT] Your Europe: the manufacturer is whoever makes a product or has it made and sells it under their own name; they are responsible for the compliance of the entire product including components supplied by others; CE marking requires identifying requirements, deciding whether a notified body is needed, assembling technical documentation, and a signed EU declaration of conformity; there is no central EU body granting CE permission; if a notified body is involved its 4-digit number appears next to the CE mark [R08-S32].
- [REC] Because the Annex I lists as published put "protective devices designed to detect the presence of persons" and "logic units to ensure safety functions" in Part B, and ML-based safety functions in Part A, Valtoryn's design choice to use pre-certified third-party scanners and safety controllers and to keep ML out of safety functions also keeps its own conformity burden lower. This reading of Annex I is mine; whether it applies to any actual product requires a qualified assessor.

#### 2.13.2 United States and others

- [FACT] ANSI/A3 R15.08-1 (R2026) addresses manufacturers: safety requirements so industrial mobile robots operate with acceptable risk in a manufacturer-documented specified operating environment; risk assessment as an iterative process; information for use for integrators/end users; primarily for structured and semi-structured industrial environments where people interacting are trained; "industrial" includes warehousing, distribution and logistics [R08-S12]. Part 2 (2023) covers integrating, configuring and customising an IMR or fleet into a site, including interaction with workstations and charging stations [R08-S13]. Part 3 (2026) covers user responsibilities including risk assessment, management of change, training, periodic inspection (weak source) [R08-S14].
- [FACT] UL 3100 covers battery-operated mobile platforms for lifting, carrying, picking and towing in commercial/industrial indoor use; excludes industrial robots (UL 1740/CSA Z434), floor-cleaning AGVs, Type E/EE/ES/EX industrial trucks, forklifts and personnel carriers; Ed.1-2021 shown as historical [R08-S15]. UL Solutions describes UL 3100 evaluation as third-party [R08-S16]. [UNRESOLVED] OSHA recognition claims seen in a search snippet were not verified; OSHA/HSE guidance on AGVs was not found in an inspectable form.
- [FACT] A Swiss accident-insurer (Suva) summary hosted on the "Safe machines at work" site lists AGV hazards (collision, crushing, falling loads, floor conditions, maintenance) and recommends segregation into a secured zone where possible plus traffic rules, active/passive safety systems, stop and manual control and maintenance [R08-S57].
- UK (HSE/UKCA), Canada (CSA Z434 mentioned in UL 3100 scope), Japan, China: not investigated. [UNRESOLVED].

---

## 3. Trade-off analysis: safety-layer architecture options

| Option | Description | Strengths | Weaknesses / risks | Evidence base |
|---|---|---|---|---|
| A. Scanner OSSD directly to drive STO/brake via safety relay | Certified scanner with static fields; relay/contactor or drive STO | Simplest; fewest safety components; scanner PL d / Cat 3 (as for microScan3) | Single field set only; no speed-adaptive fields; long fixed fields force low speeds; limited diagnostics | [R08-S34] |
| B. Certified safety controller (safety PLC/module) | Scanner(s), E-stop, mode switch, encoders, drive STO/SS1/SLS, brake all wired to a certified controller that does field-set switching, speed monitoring, muting, restart | Standard industrial pattern; configuration (not firmware) work; supports safe speed monitoring and field switching; same-PL requirement for switching logic is met by certified controller | Cost; configuration/validation effort; vendor lock-in; configuration still needs verification (cross-circuit risk, per SICK note) | [R08-S34, S39] |
| C. Drive-integrated safety (SLS, SS1, STO, SBC) plus scanner field switching | Safety functions inside the servo/drive | Short reaction chains; certified drives | Hardware selection constrained to drives with these functions; per-drive configuration | [R08-S48] (trade source) |
| D. Custom safety MCU/firmware by Valtoryn | In-house safety microcontroller | Open, low cost per unit | IEC 62061 scope puts such boards under IEC 61508-style development (complex programmable subsystem); heavy process, assessor effort; not suitable for an open-source community project | [R08-S19, S22] |
| E. ROS 2 node as the protective function | Navigation lidar + costmap stop | Easiest | Not certifiable as such; ROS 2 not safety-certified (community statement); fails every item in 2.6 | [R08-S54] |

[REC] Option B (or B+C) for hardware reference designs; Option A only for early bench rigs; D and E rejected for any claim of personnel protection.

---

## 4. Safety architecture boundary — proposal

All items in this section are [REC].

### 4.1 Boundary definition

```
+--------------------------------------------------------------+
|  NON-SAFETY DOMAIN (ROS 2): untrusted by the safety layer     |
|  perception, localisation, mapping, Nav2/planners, fleet,     |
|  task execution, digital twin, nav lidar, cameras, learned    |
|  models. Output: velocity / mode REQUESTS only.               |
+-------------------------+------------------------------------+
                          | requests (non-safety, validated, limited)
                          v  <---- status/diagnostics (read-only)
+--------------------------------------------------------------+
|  SAFETY DOMAIN (separate, certified components)               |
|  safety scanners (OSSD/safe network) + safety controller      |
|  safe speed monitoring (encoders) -> field-set selection      |
|  E-stop chain, mode selector, muting, restart interlock       |
|  drive STO/SS1/SLS, spring-applied brake + monitoring         |
|  battery protection / BMS safety functions                    |
|  watchdog on the autonomy heartbeat                           |
+--------------------------------------------------------------+
```

Rules:
1. **The safety domain never depends on ROS 2 for any safety function.** It must be able to stop the vehicle with the autonomy stack absent, crashed or malicious.
2. **The autonomy stack can only request, never command, safety-relevant states.** The safety domain enforces speed limits and field sets from its own safely measured inputs (consistent with SICK's requirement that the logic selecting protective fields has the same safety level as the function [R08-S34]). It can reduce permitted speed; it never raises it beyond the safety layer's own limit.
3. **One-way trust:** the safety domain publishes status (fault, mode, active field set, stop reason) to ROS 2 for logging and operator UI. These are not safety signals.
4. **Safety configuration is controlled data:** field geometry, speed limits, timing assumptions and firmware/configuration hashes are versioned, reviewed by a different person, and logged on every change. This aligns with the Machinery Regulation's requirement to log safety software versions for five years and to prevent unintended modification of safety settings [R08-S27].
5. **No ML in the safety domain** (see 2.10).
6. **Nav lidar and safety scanners are different sensors in different domains.** Sharing one physical scanner between domains is not permitted in reference designs.
7. **Simulation is a design tool across the boundary:** it can check field geometry using the formula in 2.7 and exercise autonomy behaviour at the boundary, but it does not stand in for the safety domain's verification.

### 4.2 Repository and process controls

- A top-level `SAFETY-STATUS` statement: "not safety-rated; simulation and research use; no warranty of safe operation; integrators are responsible for conformity".
- Documentation vocabulary rules: never write "safe", "certified" or "PL d" about Valtoryn artefacts without citing an assessor's report; use "simulated-verified", "HIL-verified", "bench-measured" according to the ladder.
- Code-ownership rules for safety-adjacent interfaces (the request/status messages), with mandatory review by a safety lead.
- Hazard log, safety requirements and traceability maintained in-repo (the ROS 2 Safety WG maintains Doorstop extensions for requirements traceability [R08-S53]).
- Release notes must state which evidence-ladder level each safety requirement has reached.

---

## 5. Implications for the Valtoryn roadmap

1. [REC] Treat safety as an architecture constraint from day one: the software stack should be designed so a certified safety layer can be inserted below it, including hardware abstraction interfaces for safe-speed status, stop-reason and mode.
2. [REC] Do not target a first-party safety certification of the platform. Target "safety-ready": documented interfaces, reference integrations with certified components, a hazard analysis and a test plan that an integrator and assessor can reuse.
3. [REC] The modular-chassis vision implies the safety case is per chassis and per payload; reusable pieces are the method, templates, formulas and test harnesses, not the safety claim. Mobile manipulation needs its own standards path (2.8).
4. [REC] Multi-robot fleet logic is outside the vehicle's safety functions; any fleet-level "safe" claim (for example traffic rules at intersections) needs its own hazard analysis (STPA suits this) and must degrade to vehicle-level safety, consistent with R15.08-2's system/fleet focus [R08-S12, S13].
5. [REC] Early budget items: a safety-rated scanner pair and safety controller for the reference AMR, a spring-applied brake, a brake/stopping-distance measurement setup, and an assessor consultation before design freeze.

### 5.1 Evidence ladder

| Level | Name | What it is | Claims permitted | Claims NOT permitted |
|---|---|---|---|---|
| L0 | Simulated | Software-in-the-loop, digital twin, scenario tests, formula-based field sizing | "Behaviour X was observed in simulation under model M"; design-space exploration; test-case generation | Any statement about physical safety, response times, stopping distance, detection performance |
| L1 | HIL | Real safety controller/drive electronics with simulated plant, fault injection, timestamped reaction-time measurement | "Controller configuration C reacts to injected fault F within T on the rig" | Brake performance, sensor detection on real objects, EMC, thermal |
| L2 | Bench-tested hardware | Components and subsystems tested physically: brake torque, stopping on a test track at single conditions, scanner field verification with test pieces, fault injection on actual circuits, battery pack documents | Component-level performance within tested conditions | System-level compliance; any PL claim beyond component data sheets |
| L3 | System tested | Integrated vehicle in a representative site: full verification (person-detection tests, stopping at all speeds/loads/floors, stability, modes, E-stop, commissioning checklist) by the manufacturer/integrator | "Verified by manufacturer against requirements R1..Rn" for that configuration | Conformity or certification |
| L4 | Third-party assessed | Independent assessment by a notified body or accredited test lab, where a regulation or customer requires it | Wording as stated in the assessor's report, scope-limited | Anything outside the report scope or after a change |

Gating rules [REC]: no field deployment with people nearby before L3 at minimum, and L4 where the regulation or the site requires; every change to a safety-relevant element (field geometry, speeds, brake, software/config of the safety domain) drops the affected requirement to the lowest level at which it can be re-verified; L0 and L1 evidence is never presented as L3/L4.

---

## 6. Limitations of this research

- The core standards (ISO 3691-4, ISO 13849-1/-2, IEC 62061, IEC 61508, IEC 61496, ISO 13850, ISO 13855, IEC 60204-1, IEC 61800-5-2, ANSI/A3 R15.08, UL 3100) were not read in full. Clause-level statements come from catalogue abstracts, the iTeh preview TOC and secondary sources and are flagged.
- Several sources are manufacturers, trade blogs or certification-body marketing (Fabrico, Dematic, CTB, industrialsafetysensor, Rexel, Applus+, Intertek, MarketScale); I labelled them weak or manufacturer claims where used.
- The EU Machinery Regulation application date shows a discrepancy between the fetched text (14 January 2027, original print) and the Commission/DGUV statements (20 January 2027, after a corrigendum I did not open).
- The worked example uses assumed inputs and a single manufacturer's formula; it is not a validated design.
- No US federal (OSHA) or UK (HSE) AGV guidance was obtained in inspectable form; those jurisdictions are not covered.
- No safety statement here has been reviewed by a functional-safety professional.
- The scanner datasheet values are for one product (microScan3 Core I/O) at one manual revision; other products and variants differ.

## 7. Unresolved questions

1. ISO 3691-4:2023 normative content: exact PLr table, person-detection test pieces and acceptance criteria, muting speed limits, zone tables, stability and dynamic test procedures. Resolve by purchasing the standard (CHF 204 at the ISO catalogue price on 2026-11-07 [R08-S01]).
2. What the next edition (ISO/DIS 3691-4) changes and when it publishes.
3. ISO 13849-1:2023 PFH band values: two trade sources conflict. Resolve with the standard or IFA SISTEMA v3 documentation.
4. Exact Machinery Regulation application date: confirm via the corrigendum and consolidated text (20 January 2027 is best supported).
5. When EN ISO 3691-4 and other standards will be cited under Regulation 2023/1230; whether Directive-based presumption carries over.
6. Which standard covers mobile manipulators (R15.08-2 scope? ISO 3691-4 + ISO 10218 combination? notified-body opinion?).
7. UL 3100 current edition and OSHA recognition claims.
8. Whether any official Open Robotics statement on ROS 2 safety certification exists.
9. UK, Canadian, Japanese and Chinese regimes.
10. IEC 61800-5-2 actual text for STO/SS1/SS2 definitions; our descriptions come from vendor pages.
11. UL 1973 / UL 2271 applicability to AMR traction batteries.
12. How pedestrian approach speed is treated in ISO 3691-4:2023 protective-field sizing.

---

## 8. Sources

| ID | Title | Organization / author | URL | Published / revision date | Accessed | What it supports |
|---|---|---|---|---|---|---|
| R08-S01 | ISO 3691-4:2023 Industrial trucks — Safety requirements and verification — Part 4: Driverless industrial trucks and their systems (catalogue page) | ISO | https://www.iso.org/standard/83545.html | Edition 2, 2023-06 | 2026-11-07 | Scope, exclusions, status 90.92, price, DIS pointer |
| R08-S02 | ISO 3691-4:2020 (catalogue page) | ISO | https://www.iso.org/standard/70660.html | Edition 1, 2020-02 (withdrawn) | 2026-11-07 | 2020 edition withdrawn, replaced by 2023 |
| R08-S03 | ISO 13849-1:2023 (catalogue page) | ISO | https://www.iso.org/standard/73481.html | Edition 4, 2023-04 | 2026-11-07 | Scope of 13849-1:2023 |
| R08-S04 | ISO 13849-1:2015 (catalogue page) | ISO | https://www.iso.org/standard/69883.html | Edition 3, 2015-12 (withdrawn) | 2026-11-07 | 2015 edition scope/notes, withdrawn |
| R08-S05 | ISO 12100:2010 (catalogue page) | ISO | https://www.iso.org/standard/51528.html | 2010-11; reviewed 2022 | 2026-11-07 | Risk assessment methodology scope; DIS 12100.3 |
| R08-S06 | ISO 13850:2015 (catalogue page) | ISO | https://www.iso.org/standard/59970.html | Edition 3, 2015-11 | 2026-11-07 | E-stop scope, link to IEC 60204-1 |
| R08-S07 | ISO/TS 15066:2016 (catalogue page) | ISO | https://www.iso.org/standard/62996.html | Edition 1, 2016-02 | 2026-11-07 | Cobot TS scope, status, AWI replacement |
| R08-S08 | ISO 10218-1:2025 (catalogue page) | ISO | https://www.iso.org/standard/73933.html | Edition 3, 2025-02 | 2026-11-07 | Industrial robot scope; mobile-platform exclusion |
| R08-S09 | ISO 10218-2:2025 (catalogue page) | ISO | https://www.iso.org/standard/73934.html | Edition 2, 2025-02 | 2026-11-07 | Robot application scope; mobile-platform exclusion |
| R08-S10 | ISO ICS 13.110 Safety of machinery (standards list) | ISO | https://www.iso.org/ics/13.110.html | n/a (not stated on page) | 2026-11-07 | Stages of ISO 13849-2, FDIS 13849-2, ISO 13855:2024, TR 22100-5, DIS 12100.3 |
| R08-S11 | ISO/DIS 3691-4 (committee catalogue page) | ISO | https://committee.iso.org/es/sites/isoorg/contents/data/standard/08/86/88615.html?browse=tc | n/a (not stated on page) | 2026-11-07 | Draft stage 40.60 |
| R08-S12 | ANSI/A3 R15.08-1-2020 (R2026): Industrial Mobile Robots Safety | ANSI Blog (A. Schirn) | https://blog.ansi.org/ansi/ansi-a3-r15-08-1-2020-r2026-mobile-robot-safety/ | 2026-09-10 | 2026-11-07 | R15.08 series structure and Part 1 scope |
| R08-S13 | ANSI/A3 R15.08-2 Safety Standard for Industrial Mobile Robot Systems and Applications Now Available | A3 via Business Wire | https://www.businesswire.com/news/home/20231009986731/en/ANSIA3-R15.08-2-Safety-Standard-for-Industrial-Mobile-Robot-Systems-and-Applications-Now-Available | 2023-10-09 | 2026-11-07 | R15.08-2 scope |
| R08-S14 | A3's final mobile robot safety standard is written for the sites running the robots (weak) | MarketScale | https://www.marketscale.com/industries/industrial-iot/a3s-final-mobile-robot-safety-standard-is-written-for-the-sites-running-the-robots | 2026-10-11 | 2026-11-07 | R15.08-3 scope and date (weak source) |
| R08-S15 | UL 3100 Ed.1-2021 Automated Mobile Platforms (AMPs) (scope excerpt) | ANSI Webstore / UL | https://webstore.ansi.org/standards/ul/ul3100ed2021 | Shown as "Historical" | 2026-11-07 | UL 3100 scope and exclusions |
| R08-S16 | Are your Industrial Automated Mobile Robots or Platforms Safe? | UL Solutions | https://www.ul.com/resources/are-your-industrial-automated-mobile-robots-or-platforms-safe | n/a (not stated on page) | 2026-11-07 | UL 3100 evaluation areas |
| R08-S17 | IEC 61496-3:2025 (webstore page) | IEC | https://webstore.iec.ch/en/publication/84133 | 2025-08-14 | 2026-11-07 | AOPDDR scope and edition |
| R08-S18 | IEC 62061:2021 (webstore page) | IEC | https://webstore.iec.ch/en/publication/59927 | 2021-03-22 | 2026-11-07 | Scope, changes |
| R08-S19 | BS EN IEC 62061:2021+A2:2026 | BSI Knowledge | https://knowledge.bsigroup.com/products/safety-of-machinery-functional-safety-of-safety-related-control-systems-2 | 2026-06-30 | 2026-11-07 | A2:2026; complex programmable subsystem note |
| R08-S20 | IEC 60204-1:2016+AMD1:2021 (webstore page) | IEC | https://webstore.iec.ch/en/publication/71256 | 2021-09-15 | 2026-11-07 | Scope; Clause 9 STO/E-stop |
| R08-S21 | IEC 61508-1:2010 (webstore page) | IEC | https://webstore.iec.ch/en/publication/5515 | 2010-04-30 | 2026-11-07 | IEC 61508 basic safety publication |
| R08-S22 | IEC 61508-3:2010 (webstore page) | IEC | https://webstore.iec.ch/en/publication/5517 | 2010 | 2026-11-07 | Software requirements scope |
| R08-S23 | IEC 61882:2016 HAZOP application guide (webstore page) | IEC | https://webstore.iec.ch/en/publication/24321 | 2016-03-10 | 2026-11-07 | HAZOP method description |
| R08-S24 | IEC 60812:2018 FMEA and FMECA (webstore page) | IEC | https://webstore.iec.ch/en/publication/26359 | 2018 | 2026-11-07 | FMEA method description |
| R08-S25 | IEC 62619:2022 (webstore page) | IEC | https://webstore.iec.ch/en/publication/64073 | 2022-05-24 | 2026-11-07 | Industrial lithium battery safety scope incl. AGV |
| R08-S26 | UN Manual of Tests and Criteria, 6th rev., sub-section 38.3 (unofficial version) | PRBA (reproducing UN text) | https://www.prba.org/wp-content/uploads/Sub-section-38.3-UN-Manual-6th-Revised-Edition-with-corrections.pdf | n/a (not stated on page) | 2026-11-07 | UN 38.3 tests T1–T8 |
| R08-S27 | Regulation (EU) 2023/1230 on machinery (EUR-Lex text) | European Parliament and Council | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023R1230 | 2023-06-14; OJ L 165, 29.6.2023 | 2026-11-07 | Articles 25, 54; Annexes I–III; autonomous machinery provisions |
| R08-S28 | Machinery (EU machinery legislation overview) | European Commission, DG GROW | https://single-market-economy.ec.europa.eu/sectors/mechanical-engineering/machinery_en | n/a (not stated on page) | 2026-11-07 | 20 Jan 2027 date, corrigendum note, notified bodies, voluntary-certificate warning |
| R08-S29 | Regulation (EU) 2023/1230 | DGUV Test | https://www.dguv.de/dguv-test/prod-testing-certi/conform-prod/machinery/eu-maschinenverordnung/index.jsp | 2026-04-28 | 2026-11-07 | No transition; 19/20 Jan 2027 cut-over |
| R08-S30 | Commission Implementing Decision (EU) 2024/1329 | European Commission (EUR-Lex) | https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202401329 | 2024-05-13 (OJ 15.5.2024) | 2026-11-07 | EN ISO 3691-4:2023, EN ISO 13849-1:2023 in OJ list |
| R08-S31 | Commission Implementing Decision (EU) 2026/2015 | European Commission (EUR-Lex) | https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202602015 | 2026-09-04 (OJ 7.9.2026) | 2026-11-07 | EN ISO 13855:2024, EN ISO 10218-1/-2:2025 listed |
| R08-S32 | CE marking — Your Europe | European Commission | https://europa.eu/youreurope/business/product-rules-compliance/general-product-compliance/ce-marking/index_en.htm | n/a (not stated on page) | 2026-11-07 | Manufacturer responsibility, CE steps, notified body ID |
| R08-S33 | Conformity assessment | European Commission, DG GROW | https://single-market-economy.ec.europa.eu/single-market/goods/building-blocks/conformity-assessment_en | n/a (not stated on page) | 2026-11-07 | Conformity assessment definition; voluntary certificates |
| R08-S34 | microScan3 Core I/O operating instructions (8016346/1WGY/2026-07-23) | SICK AG | https://www.sick.com/media/docs/7/57/757/operating_instructions_microscan3_core_i_o_en_im0063757.pdf | Document dated 2026-07-23 | 2026-11-07 | Safety parameters, field sizing formulas, response time, TZ/ZR/ZF, monitoring cases |
| R08-S35 | The perfect size of the protective field on an industrial autonomous vehicle | SICK | https://www.sick.com/ch/en/the-perfect-size-of-the-protective-field-on-an-industrial-autonomous-vehicle/w/blog-size-protective-field-industrial-autonomous-vehicle | 2021-02-09 | 2026-11-07 | Scanner type, warning fields, multiple sampling, SA dominance |
| R08-S36 | Calculation wizards — Safety at work | Leuze | https://www.leuze.com/en-uk/contact-and-support/specialist-knowledge/safety-at-work/calculation-wizards | n/a (not stated on page) | 2026-11-07 | ISO 13855:2010 and :2024 formulas; stop-time measurement |
| R08-S37 | ISO 3691-4:2020 A Standard for Automated Guided Vehicles (white paper) | TÜV Rheinland | https://www.tuv.com/content-media-files/master-content/services/industrial-services/pdf/tuv-rheinland-automatic-guided-vehicles-whitepaper-en_neu.pdf | n/a (not stated on page); refers to 2020 edition | 2026-11-07 | PLr table summary, zones, safety functions, limitations (2020 edition) |
| R08-S38 | ISO 3691-4:2023: Compliance testing for AGVs | Applus+ Laboratories | https://www.appluslaboratories.com/global/en/what-we-do/service-sheet/iso-3691-4-2023-compliance-testing-for-automated-guided-vehicles-agvs | n/a (not stated on page) | 2026-11-07 | Test services, accreditation statement (manufacturer/lab marketing) |
| R08-S39 | Demonstrating Functional Safety Integrity in AGV Applications | Intertek (J. Lynskey) | https://www.intertek.com/blog/2026/06-17-functional-safety-integrity-in-agv-applications/ | 2026-06-17 | 2026-11-07 | How 3691-4, 12100, 13849-1 fit; common safety-case gaps |
| R08-S40 | ISO 3691-4:2023 — Driverless Industrial Trucks | ANSI Blog | https://blog.ansi.org/ansi/iso-3691-4-2023-driverless-industrial-trucks/ | 2023-07-10 | 2026-11-07 | Braking, speed control, E-stop requirements summary |
| R08-S41 | SIST EN ISO 3691-4:2023 (public preview PDF) | iTeh Standards / SIST / CEN | https://cdn.standards.iteh.ai/samples/74578/7409905cc77749cd822732c7c2350902/SIST-EN-ISO-3691-4-2023.pdf | CEN approval 2023-05-05; ISO 2023-06 | 2026-11-07 | Table of contents, Annex ZA mapping, supersession |
| R08-S42 | ISO 3691-4 Explained (weak, vendor blog) | Fabrico | https://www.fabrico.io/blog/iso-3691-4-driverless-industrial-trucks/ | 2026-07-09 (updated 2026-11-02) | 2026-11-07 | Unverified claims on test pieces and 0.3 m/s |
| R08-S43 | ISO 13849 Performance Level (PL a–e) Explained (weak) | industrialsafetysensor.com | https://industrialsafetysensor.com/blog/iso-13849-performance-level/ | n/a (not stated on page) | 2026-11-07 | PFH bands (secondary); PL vs SIL caveats |
| R08-S44 | EN ISO 13849-1 and EN 62061 — PL and SIL explained (weak) | CTB | https://www.ctb.co.at/en/knowledge/safety-performance-level-sil-iec-13849-62061/ | n/a (not stated on page) | 2026-11-07 | Conflicting PFH thresholds (flagged) |
| R08-S45 | SISTEMA software assistant | IFA / DGUV | https://www.dguv.de/ifa/praxishilfen/practical-solutions-machine-safety/software-sistema/index.jsp | 2026-10-26 | 2026-11-07 | PL/PFH tool; version mapping to 13849-1 editions |
| R08-S46 | SIST EN ISO 13849-2:2013 (public preview) | iTeh Standards / SIST | https://standards.iteh.ai/catalog/standards/sist/31f719dd-05d7-47e4-a892-de94c4c001cb/sist-en-iso-13849-2-2013 | 2013-03-13 | 2026-11-07 | Validation by analysis and fault-injection testing |
| R08-S47 | Implementing speed and separation monitoring in collaborative robot workcells | J.A. Marvel, R. Norcross (NIST), Robotics and Computer-Integrated Manufacturing 44 | https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=914783 | 2017 (online 2016) | 2026-11-07 | SSM protective-distance formula; IEC 60204-1 stop categories |
| R08-S48 | What are typical drive-based safety functions? | Motion Control Tips | https://www.motioncontroltips.com/faq-what-are-typical-drive-based-safety-functions/ | 2017-01-24 | 2026-11-07 | STO, SS1, SS2, SOS, SBC, SLS descriptions (trade) |
| R08-S49 | STO – Safe Torque Off according to IEC 61800-5-2 | SEW-Eurodrive | https://download.sew-eurodrive.com/download/html/31960413/en-EN/28733575051.html | n/a (not stated on page) | 2026-11-07 | STO equals stop category 0 |
| R08-S50 | Safe Stopping Options Explained | Rexel USA (C. Williams) | https://pages.rexelusa.com/blog/automation/safe-stopping-options | 2019-02-19 | 2026-11-07 | SS1 vs SS2 behaviour; SS2 not for e-stop (trade claim) |
| R08-S51 | Review of STPA Method and Results to Support NextGen Concept Assessment and Validation (ATC-427) | MIT Lincoln Laboratory (Harkleroad, Vela, Kuchar) | https://www.ll.mit.edu/sites/default/files/publication/doc/2018-12/Harkleroad_2013_ATC-427.pdf | 2013-10-25 | 2026-11-07 | STPA description, findings and limits |
| R08-S52 | System Theoretic Process Analysis (slides) | Sandia National Laboratories (T. Stirrup), EFCOG | https://www.osti.gov/servlets/purl/1375580 | 2016-08 | 2026-11-07 | STPA interfaces/controllers framing |
| R08-S53 | ROS 2 Safety-Critical Working Group | ros-safety (GitHub) | https://github.com/ros-safety/safety_working_group | n/a (not stated on page) | 2026-11-07 | WG mission, subprojects (watchdogs, contracts, Doorstop) |
| R08-S54 | How to enable ROS to pass the safety certification of the automotive industry? | Open Robotics Discourse (community thread) | https://discourse.openrobotics.org/t/how-to-enable-ros-to-pass-the-safety-certification-of-the-automotive-industry/27819 | 2022-10-17 | 2026-11-07 | Community statement that ROS 2 is not safety-certified; Apex.OS claim (community, not official) |
| R08-S55 | Safe-ROS: An Architecture for Autonomous Robots in Safety-Critical Domains | Benjumea, Farrell, Dennis (Univ. of Manchester), EPTCS 436 | https://arxiv.org/abs/2511.14433 | 2025-11-18 | 2026-11-07 | Separate safety system architecture precedent |
| R08-S56 | The CAT Vehicle Testbed: A Simulator with Hardware in the Loop for Autonomous Vehicle Applications | Bhadani, Sprinkle, Bunting | https://arxiv.org/abs/1804.04347 | 2018-04-12 | 2026-11-07 | ROS-based simulator-to-HIL precedent |
| R08-S57 | Automated Guided Vehicles (AGVs) — English summary | Suva, hosted on safe-machines-at-work.org | https://www.safe-machines-at-work.org/fileadmin/user_upload/content/digital_manufacturing/digital_connectivity/Automated_guided_vehicles.pdf | n/a (not stated on page) | 2026-11-07 | AGV hazard overview and mitigation list |
| R08-S58 | AGV & AMR Safety Standards Have Recently Evolved (manufacturer claim) | Dematic | https://www.dematic.com/en-us/insights/articles/agv-and-amr-safety-standards/ | n/a (not stated on page) | 2026-11-07 | Warning/protective field pattern; muting measures (manufacturer statement) |
| R08-S59 | Battery Module and Pack Testing for Manufacturers | UL Solutions | https://www.ul.com/services/battery-module-and-pack-testing-manufacturers | n/a (not stated on page) | 2026-11-07 | UL 1973 / UL 2271 named uses; BMS functional safety service |


### Sources that could not be inspected (not cited)

- ISO 13855:2024 catalogue page (https://www.iso.org/standard/80590.html) — blocked to automated reads.
- ISO/TC 199 committee catalogue (https://www.iso.org/committee/54604.html) — blocked.
- IEC functional-safety FAQ (https://iec.ch/functional-safety/faq) and IEC blog on IEC 62061 — blocked.
- Pilz pages on EN 61800-5-2 and ISO 3691-4 updates — blocked.
- ANSI webstore page for UL 1973 and SCC page for UL 2271 — blocked.
- UNECE UN Manual Rev. 8 section 38.3 PDF — unreachable on retry.
- TÜV SÜD presentation on IEC 61800-5-2 — unreachable.
- ros2.org safety working group site — unreachable.
- Commission harmonised-standards page for the Machinery Regulation (statement about a forthcoming implementing decision seen only in a search snippet) — not opened.
- The corrigendum to Regulation (EU) 2023/1230 — not located as a separate document.
- OSHA 29 CFR 1910.178 and HSE HSG136 — appeared in search results; not opened, so not cited.
