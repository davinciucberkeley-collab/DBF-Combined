# T-083 (D-227, AM-018): X2216 integration, landing re-run, CAD, BOM, gates. 2026-11-21. Not VERIFIED COMPLETE. Nothing committed.

No edit to docs/, CHANGE-LOG, task ledger, TEST-PLAN-O4B, MASS-GATE or BOM-A.csv (proposed text in s10). Labels: V = vendor page or drawing read today (URL, 2026-11-21); D = read off the SunnySky drawing; EST = estimate; "—" = unknown.
Categories: illustrative (prop_a.py EST thrust model: s2), rigid-body dynamics (landing_a.simulate, s5), hand calculation (strength rows s5, mount rows s4), interference (collide, linkage poses, assembly: s8), geometry arithmetic (mass, CG, box, wire lengths: s6, s9). No FEA, CFD or SITL was run.
Data, scripts, outputs: `T083_data/` (index in s11). The 87 MB demand array is `T083_data/fea/demand_t083.npz`, git-ignored (`.gitignore` line added).

## Acceptance test (restated from the brief)
1. Propulsion: X2216 880KV data in `prop_a.py` and `params-A.json` (pack 2.8 Ah); Lua spin cap and current limits (ESC, H743-Wing, pack C, connector); window, T/W fresh / sag, cruise, A-P6 at the new mass; TP-1 / TP-2 re-spec (text only).
2. Landing: demand re-run at the new mass with the plateau rescaled (no bottoming, end tilt <= 3.0 deg); D-226 rows and the motor cups re-judged; rib both ways (25x23 drawn, 14x12 if the coupon passes).
3. CAD: real-shape X2216 from the vendor drawing (unknowns marked), cups / mounts resized, cage forward for CG / SM (A-P4), 0.50 m box kept; printed_mass.json, build steps, drawings.
4. BOM copy with the motor swap and the crash reserve by its definition; total incl. reserve <= $2,000.
5. Gates once at the end into `T083_data/gates/`.
6. This report. Never relaxed: KF 1.725, KP 2.156, RF >= 1.0 at max(DAF, 1.5) with the D-223 DAF (2.23 on these rows), A-P3 window >= +5 %. No ballast.

## 0. Outcome
| # | Item | Result | Verdict |
|---|---|---|---|
| 1 | Motor | **SunnySky X2216 V3 880KV SHORT shaft (RMRC 84776), not the long-shaft RMRC 85810 the study named.** SunnySky's drawing shows the long-shaft version's shaft leaving the BASE 16 mm with a Phi 9 x 5 collar (50 - 34 mm); behind the cup plate sits the 12 mm arm tube 7.9 mm away, so it cannot be fitted (s3.1). The short-shaft V3 has a 2.5 mm stub, Rm 89 mohm, 450 W, 67.5 g and a maker thrust table. | needs Dillon (money: +$4 per motor, BACKORDER, s7) |
| 2 | Propulsion (tallied 1.913 kg, Q_M_BAT_CURR_MAX 72 A) | window **+11.02 %**, T/W fresh 2.586 / sag 2.074 (3 % download), cruise 223 s, one motor 20.1 A vs 24.9 A EST line, 11,358 rpm vs APC 11,667, pack 73.3 A peak -> XT90 | PASS (model EST) |
| 2a | A-P6 at the predicted mass | 1.3 Vs **17.71 m/s > 17.0** (CLmax 0.75 EST; ceiling 1.762 kg; CLmax needed 0.81) | **FAIL, limit gap** (s2.3) |
| 2b | Bench lines | derate >= **0.889 for the 204.6 s cruise** (binds first), 0.824 for A-P3, at 1.913 kg. SunnySky's own 14.8 V table (prop "APC9045", variant not stated) is 0.80-0.88 of the APC MR rows at equal rpm | PASS on paper at 0.93; **bench risk** |
| 3 | Landing demand | Fp 30 -> **36 N** (24 mm): stroke 20.87 mm, end tilt **2.90 deg**, n 8.7 / 10.3 / 12.7 g at zeta 0.02 / 0.05 / 0.10 | PASS (tilt, stroke); n 12.7 g > 12 at zeta 0.10 |
| 3a | D-226 rows + strut / R4 clamp, 25x23 rib | **all pass at pad zeta <= 0.05 (min 1.11, fin node N4a at 0.05)**; at zeta 0.10, 9 row groups fail, min **0.66** (centre flange bond C3) | **gap at zeta 0.10**: TP-3 decides (s5) |
| 3b | Rib 14x12 (coupon case) | rib R1 0.33 at zeta 0.02 on tau 30 MPa: coupon line rises **79 -> about 92 MPa** (zeta 0.02; 99 MPa all zeta, EST); its root-block bond D14 x 31 is 0.67 (needs about 47 mm, EST) | not available on this demand without a root-block change |
| 3c | Drawn root block FIN-003 | P6 0.25-0.44, P8 0.31-0.60 (undrawn enlargement, as p8) | FAIL, carried (SL-3) |
| 3d | Motor mount and cup rows (new) | min MS +0.46 (plate strip at the nut); all PASS | PASS |
| 4 | Mass / CG | drawn 1,650.6 g, CG 21.34 mm; **tallied 1,669.8 g, 1.913 kg, CG 24.41 mm, SM 6.65 %**, trim ends 23.44 / 26.03 | PASS A-P4 (was 30.17 / 4.30 %) |
| 5 | Box (props on) | x 496.9 mm (was 491.4) of 500; cage + pack 3 mm forward | PASS (x); z 465 mm vs 0.39 m proxy is the old P1 finding |
| 6 | BOM | **$2,006.66, margin -$6.66** (reserve $346.94 by definition); $1,871.21 with the 14x12 rib; $1,981.31 without the spare motor | **FAIL by $6.66** (s7) |
| 7 | Exposed wire | 0.609 strand-m (was 0.502): +0.107 = 12 X2216 phase strands x about 8.4-8.9 mm between the can and the cup lead hole, + 3 mm on each pack lead | listed (s9) |
| 8 | Gates | collide pose 21 PASS, 18 linkage poses PASS, assembly PASS (66 steps, 129 / 129), wire inventory, cad_mass, mission gate, prop sched, drawings 49 / 49, build guide OK; build_a fails only on the 1,500 g mass gate; proofs 8 failing claims (15 at p8) | PASS except the mass gate (not relaxed) |

**Blocker (one line):** two gaps need Dillon: (a) money: the motor SKU (84776 short shaft, $22.99, backorder) and $6.66 over budget with the 25x23 rib; (b) A-P6 (1.3 Vs 17.71 > 17.0) cannot pass at 1.91 kg without a measured CLmax >= 0.81 or a re-derived cruise speed. The zeta-0.10 landing rows are a TP-3 test gap, not a design change made here.

## 1. Sources read today (2026-11-21)
- SunnySky X2216 V3 page (Shopify JSON of https://sunnyskyusa.com/products/sunnysky-x2216): KV880: stator 22 x 16, rotor Phi 27.7, body length 34, 12N14P, 3-4S, ESC 50 A, I0 0.5 A / 10 V, **Rm 89 mohm, 32 A / 30 s, 450 W max continuous, 67.5 g**; thrust table KV880 + "APC9045" at 14.8 V: 100 % = 16.3 A, 1,180 gf, 241.24 W, 10,972 rpm. Text: "880KV ... are short shaft version"; "Both of them come with the same prop adapter and motor mount."
- SunnySky drawing X2216 (https://cdn.shopify.com/s/files/1/2024/0305/files/X2216.jpg, linked from that page): see s3.1.
- RMRC 85810 X2216 long shaft 880KV: $18.99 In Stock, 72 g, Rm 117 mohm, 320 W, shaft 3.175, no drawing (https://www.readymaderc.com/products/details/85810-sunnysky-x2216-brushless-motors-long-shaft-version-880kv).
- RMRC 84776 X2216 V3 short shaft 880KV: **$22.99, Backorder (availability date November 2026)**, 67.5 g, Rm 89 mohm, 450 W, 32 A / 30 s; includes "X Mount Bracket with screws" and a prop adapter (https://www.readymaderc.com/products/details/sunny-sky-x2216-brushless-motor-short-shaft-880kv).
- APC RPM limits: Multi-Rotor (MR) props "Maximum RPM=105,000/prop diameter (inches)" -> 11,667 rpm for 9 in (https://www.apcprop.com/technical-information/rpm-limits/). The 2026-11-21 study had this as "—".
- RMRC 86593 XT90 pigtail set, 3 male + 3 female, 12 AWG 10 cm, $12.99 In Stock (https://www.readymaderc.com/products/details/86593-xt90-male-female-adapters-with-12awg-10cm-leads).
- XT60 / XT90 current ratings: secondary sources only (web search, AMASS data sheet not read): XT60 30 A continuous / 60 A momentary, XT90 40-90 A. Used as: XT90 90 A for A-P16 (EST, "—" until the AMASS sheet is read).
- Not found: X-mount material, lead gauge, bullet-nut size, Phi 9 recess depth, adapter counterbore depth (all "—", modelled EST and marked in the CAD names).

## 2. Propulsion (illustrative: prop_a.py EST model)
`prop_a.py` constants: Kv 880, Rm 0.089, I0 0.5 (maker), `I_MOTOR_MAX` 24.94 A = min(450 W / 16.8 V, 32 A) x 12.1/13 (EST: the A-P16 margin carried; the maker gives power, not a continuous current). Backup `T083_data/prop_a_p8_backup.py`. `gen_params_a.py` -> `params-A.json`: kv 880, rm 0.089, i0 0.5, **pack_ah 2.8** (was 2.3, CS-5), motor_rating_a 26.8 A EST, spin_cap 0.993 (the fresh duty at the 72 A pack limit). `mission_gate_a.py`: motor line 4 x (67.5 + 9.2) g, adapter + nut line 20.0 g.

### 2.1 Numbers (`t083_metrics.py`, `t083_packcap.py`, `t083_prop.py`, `gates/gate_prop_sched.txt`)
| State | basic g | pred kg | CG mm | SM % | trim ends mm | window % (dl) | T/W fresh dl | T/W sag dl | cruise s | 1.3 Vs |
|---|---|---|---|---|---|---|---|---|---|---|
| T-083 as drawn | 1,650.6 | 1.8915 | 21.34 | 7.90 | 20.36 / 22.97 | +11.57 | 2.616 | 2.098 | 230 | 17.61 |
| **T-083 tallied** (+12.2 g root blocks at 283.1, +7.0 g shoe cups at 298.1, EST, as p8) | **1,669.8** | **1.9129** | **24.41** | **6.65** | 23.44 / 26.03 | **+11.02** | **2.586** | **2.074** | **223** | **17.71** |
| tallied, rib 14x12 (if the coupon and root block allow, s5.3) | 1,646.0 | 1.8863 | 22.08 | 7.60 | 21.10 / 23.72 | +11.71 | 2.623 | 2.105 | 232 | 17.59 |

Limits: A-P3 >= +5 %, A-P2 2.0 / 1.6, A-P4 19.3..26.0 (28.5 trim end), SM >= 5 %, cruise >= 204.6 s, A-P6 <= 17.0. Predicted = basic x 1.1174 + 0.032 x 1.47 (CALC-A-MASS-PRED).

| Current / rpm check (1.913 kg) | Value | Limit | Verdict |
|---|---|---|---|
| One motor saturated + three hovering, fresh, duty 1.0 | 20.08 A | 24.94 A EST line; motor 32 A / 30 s (V) | PASS |
| All four, fresh, at the 72 A pack limit (duty 0.993) | 11,358 rpm, 18.1 A per motor, 1,434 gf table | APC 11,667 rpm (V); ESC 35 A per channel (BOM P04) | PASS (rpm margin 2.6 %) |
| All four, sag 14.92 V, duty 1.0 | 10,343 rpm, 15.15 A, 1,185 gf table, bus 13.10 V | same | PASS |
| Pack peak (uncapped / at Q_M_BAT_CURR_MAX 72) | 73.3 / 72.0 A | RDQ 2800 100C = 280 A (BOM W01) | PASS |
| Connector A-P16 (>= 1.25 x peak) | 90.0 A at the 72 A limit | XT60 60 A momentary (secondary) **fails**; XT90 90 A (secondary): PASS at the limit | XT90 (BOM W10) |
| Pack cap sweep (window with download) | 41 A -1.4 %; 48 A +3.6 %; 55 A +7.9 %; 72 A +10.8 % (1.92 kg) | >= +5 % | needs >= about 52 A, so XT60 cannot stay |
| H743-Wing current sensor at 72 A | "—" (range not read) | | open: read before Order 1 |
| Hover, derate 0.93 | 516 gf, 7,106 rpm (1P 118 Hz), 7.51 A per motor, pack 19.9 A | A-P2 hover throttle <= 0.625: about 0.58 at sag | PASS; 1P now at the top of the A-P10 hover band (100-119 Hz) |
| A-P10(b) forced-response sweep range | full-duty rpm 11,358 | sweep is 6,000-10,500 rpm | **open: extend the sweep to 11,400 rpm** |

Sensitivity at 1.913 kg (`prop_t083.md`): derate 0.88 / 0.85 / 0.80 -> window +8.3 / +6.6 / **+3.5 %**, cruise **200** / 185 / 157 s; one-motor line 17.7 / 15.0 / 12.1 A -> window +11.0 / +4.9 / -5.4 % (the X2216 must not be held below about 15 A).
Bench lines at 1.913 kg (thrust real / APC at equal rpm that just meets): A-P3 window 0.824, A-P2 fresh 0.712, A-P2 sag 0.717, and **cruise 204.6 s at 0.889** (bisection, `cruise_derate_line.txt`): the cruise-time line binds first, not the window.

### 2.2 Maker cross-check
SunnySky KV880 at 14.8 V on "APC9045" against the APC 9x4.5MR rows at the same rpm: thrust ratio 0.80 (5,836 rpm) .. 0.88 (10,972 rpm); the maker reaches 10,972 rpm / 16.3 A at 14.8 V where the model gives 11,555 rpm / 18.8 A. The maker's prop variant is not stated (APC sells E, SF and MR 9x4.5), so this is a cross-check, not a substitute: if TP-1 measures about 0.80-0.88, the window is +3.5 to +8.3 % and the cruise time 157-200 s, so **the bench could fail A-P3 and the cruise-time need**. This is the main risk the X2216 swap leaves.

### 2.3 A-P6 (gap)
Vs = sqrt(2 m g / (rho S CLmax)) = sqrt(2 x 1.9129 x 9.81 / (1.225 x 0.22 x 0.75)) = 13.62 m/s; 1.3 Vs = 17.71 > 17.0. Mass ceiling at CLmax 0.75: 1.762 kg (basic 1,535 g, 135 g below the tally). Needed CLmax at 1.913 kg: 2 m g / (rho S (17/1.3)^2) = 0.81. The X2216 makes this worse than the study's 1.864 kg (17.49) because the mount hardware and the 100 mm stock leads add mass (s6). It cannot be closed by geometry here: the wing area and the mission are fixed. Options for Dillon (the study's two, re-computed): (a) TP stall measurement with a pass line CLmax >= 0.81; (b) re-derive cruise to 17.75 m/s (= 1.3 Vs; need 204.6 x 17 / 17.75 = 196 s; available 223 x (17/17.75)^3 = 196 s EST: **zero margin**, so (b) alone does not close). A-P6 is DERIVED (REQUIREMENTS-A), so the call is the team's under the engineering-team rule, but it touches the mission speed: flagged.

### 2.4 Spin cap and limits (edited; proposed for the TEST-PLAN)
- `sitl/lua/spin_cap.lua`: table 1.0 at every voltage (cap_sched at 24.94 A, 1.912 kg), failsafe 0.90 -> 1.0 (a 0.90 cap cuts the sag window to +4.6 % without download, `gate_prop_sched.txt`); note Q_M_BAT_CURR_MAX 72.
- `A.param`: Q_M_SPIN_MAX 0.90 -> 1.0, Q_M_BAT_CURR_MAX 41 -> 72, BATT_CAPACITY 2300 -> 2800, BATT_LOW_MAH 650 -> 790, BATT_CRT_MAH 345 -> 420 (comments say why). Backups `T083_data/*.p8_backup`.

## 3. CAD (interference geometry; real shapes from the SunnySky drawing)
### 3.1 What the drawing gives (D) and what is marked
| Feature | Value | Label |
|---|---|---|
| Can (rotor) Phi x length, base face to bell top | 27.7 x 32 | D |
| Bell-top boss | Phi 9 x 2 (34 - 32) | D |
| Shaft, short-shaft version | Phi 3.175, stub 2.5 mm behind the base (36.5 - 34) | D |
| **Long-shaft version** | shaft leaves the base 16 mm (50 - 34) with a Phi 9 x 5 collar, labelled "后出轴" (rear output shaft) | D: rules out RMRC 85810 here |
| Base mounting | 4-M3x0.5, depth 2.8; one pair 19 apart, one pair 16 apart, on perpendicular lines 45 deg either side of the lead exit | D |
| Bell-top prop-adapter holes | 3-M2x0.4 EQS depth 2.8 on Phi 12 | D |
| Leads | 3, 100 mm, heat-shrink at the exit, leaving the can radially at the base end; gauge "—" (drawn 20 AWG 1.8 mm, EST); exit height 2.5 mm EST | D / EST |
| Prop adapter (supplied) | flange Phi 17 x 4 with Phi 9 recess (depth "—", 2.2 EST), 3-Phi2.1 / Phi4.1 counterbore on Phi 12, M5x0.8 stud Phi 5 x 18.5 (13 threaded); washer Phi 14.8 / 5.1 x 2 | D (depths EST) |
| X-mount (supplied) | 34 x 34 hole spans, 41 overall, arm width 7 (EST, read off the "7"), 3 thick, R6, centre Phi 10.2, inner 4-Phi3.2 + Phi5.7 countersink on 19 / 16, outer 4-Phi3.1; material "—" (aluminium EST) | D / EST |
| Bullet nut (supplied) | size "—": **not used**; an M5 nyloc ISO 10511 (s 8, m 5) is drawn instead, which also keeps the box | design choice |
| Vent slots, bell spokes, base kidney openings | not modelled (outline only) | marked in the body names |

### 3.2 Why the mount changed (ladder, decision taken here; rung 3 then rung 4)
- Rung 1-2 (keep the printed cup, drill the X2216 pattern): the 19 / 16 cross pattern puts at least one screw head of every orientation inside the arm sleeve / lead collar band (|z| < 7.9 mm behind the plate): best orientation still leaves both -y heads at |z| 6.1 mm, inside the sleeve wall and 0.1 mm from the tube (s3 check in `t083_patch_cup.py` notes). No.
- Rung 3 (rearrange): use the X-mount that ships with the motor, arms on the plate diagonals; the four 34 mm-span bolts land at |y|, |z| 12.0 mm, clear of the sleeve and collar. The motor sits 3 mm higher; the 2.5 mm rear stub sits in the mount's Phi 10.2 hole, so the old Phi 8 relief is removed. **Adopted.** Cost: +9.2 g per motor (mount 3.2 g aluminium EST + M3 hardware), CALC.
- The lead route changed because the X2216 leads leave the can radially: the cup plate lead hole moved from y 5.5 to **y 18.0** (cup frame; 4 mm bend from the can wall at r 13.85), the plate grew from +16.5 to **+22.5 mm**, the lead collar from y 8.0 to **20.5 mm**. About 8.4-8.9 mm of each strand is outside between the can and the hole (s9).
- Cup CGE-003 voxel audit: 7.68 -> **8.96 g** each (`t083_mass_audit.py`, basis S).
- Cage forward (rung 3, A-P4 margin): `T083_DX = -3 mm` moves the cage, pack (`PACK_X`) and tray-wall windows; tallied CG 25.92 -> 24.41 mm (0.50 mm per mm), box 493.9 -> 496.9 mm. 3 mm, not the 6 mm the box allows, because the bridge row B1 and the strut rows lose about 1 % per mm of extra length and they are the closest rows at zeta 0.05.

### 3.3 Files changed (backups in `T083_data/`)
`cad/amodel/propulsion.py` (motor, X-mount PRP-006, adapter + washer, M5 nyloc, edges; patch script `t083_patch_propulsion.py`), `cad/amodel/wing.py` (cup plate, collar, bolt holes, bosses / pockets / relief removed; tray-wall windows), `cad/amodel/common.py` (PH_Y 18.0, T083_DX, CAGE_DX, PACK_X), `cad/amodel/electrical.py` (lead start at the can, stock lead 0.10 m in HRN_ITEMS, contact types), `cad/amodel/printed_mass.json` (CGE-003 8.96), `cad/a_assembly_plan.py` (PRP-006 in the cage group, B0k text), `cad/a_build_steps.py` (B0k, B1, weigh checks), `cad/parts_links_a.py` (PRP-004/005/006 notes), `cad/wire_inventory.py` (X2216 leads in front of the plate outside the can are EXPOSED; before, everything near the motor was counted as ARM), `interfaces/connection_types.json` (CT-A-M3-CSK-MOTOR, CT-A-M3-BOLT-MOUNT; CT-A-PROP-* text). BOM-A.csv is not edited, so `parts-a.csv` still links P01 to the old line.
Fixes from gate run 1 (s8): `electrical.py` CD_WX raceway window +0.4 mm aft (the longer lead route shifts the strand twist; one strand touched the window edge by 0.065 mm); `wing.py` clamp socket slot 0.5 -> 1.5 mm clear (the clamp touched the skin by 0.30 mm during the B1 rise after the strut turned 0.55 deg; 0.095 mm at 1.0 mm); `a_assembly_plan.py` B0j1/B0j2 strut push axis recomputed for the 15 mm shift (hard-coded for 12 mm: the struts were swept 0.81 mm into the hub socket).

## 4. Motor mount and cup rows (hand calculation; `t083_cup_checks.md`)
Prop mid-plane 55.3 mm above the arm axis (was 47.0); cap thrust 13.1 N per motor (fresh, 72 A, derate 0.93), strike 30 N, blade stop 2.4 N m; KF / KP and EST allowables of `T077p6_data` cups.
| Row | MS |
|---|---|
| S2 mount-bolt tension (39.5 N per bolt, M3) | +32.2 |
| S2 nyloc bearing on the PETG plate | +3.02 |
| S2 plate strip at the nut, -y bolts (4.2 mm web) / +y bolts (5.0 mm) | **+0.46** / +0.79 |
| S2 X-mount arm bending at the inner hole (6061 240 MPa assumed: material "—") | +1.23 |
| S2 motor countersunk M3 thread strip in the base, 2.0 mm | +5.77 |
| S3 blade stop, bolt bearing in the plate / bolt shear | +2.31 / +30.4 |
| Arm root bending at cap thrust + torque (x1.49 on p6) | +4.52 |
| S2/S3 cup-to-arm bond (torsion part x1.18) | +1.46 |
Arm tip deflection at the cap 2.0 mm / thrust-line tilt 0.71 deg (info; p6 1.36 / 0.48).

## 5. Landing (rigid-body dynamics + hand calculation)
### 5.1 A bug found in the p6 demand
`t077p6_demand.py` called `landing_a.simulate()` without `m`, so `M_GATE` was used, and that is **1.64 kg**: `t076d_step2_table` sets `LAND_MASS_KG=1.64` at import, before `landing_a` is imported. The p6 demand labelled 1.705 kg was simulated at 1.64 kg (the wrench split used 1.705 kg). `t083_demand.py` passes `m` explicitly. The D-226 rows of T-077 p8 therefore rest on a 4 % lighter simulation than stated. For the record.

### 5.2 Pad plateau and demand (`t083_land_sweep.py`, `t083_demand.py`, `demand_t083_stdout.txt`)
Basis: 1.913 kg predicted, tallied CG 24.41 mm, CAD mass model, 24 mm usable stroke (pad geometry as D-222 s4.1: x_foot 0.3475, z_foot 0.1907), 23 cases x zeta 0.02 / 0.05 / 0.10 x mu 0.40 / 0.30.
| Fp N (1.912 kg, CG 25.92, zeta 0.02, mu 0.40) | worst stroke mm | end tilt deg | peak n g |
|---|---|---|---|
| 33.6 (= 30 x 1.912 / 1.705) | 22.35 | **3.14** | 8.18 |
| **36.0 (chosen)** | 20.85 | 2.91 | 8.73 |
| 38 / 40 / 43 | 19.76 / 19.43 / 17.48 | 2.73 / 2.65 / 2.35 | 9.18 / 9.63 / 10.31 |
Final demand at Fp 36 N (1.913 kg, CG 24.41): stroke 20.87 / 18.27 / 15.20 mm, tilt **2.90** / 2.51 / 2.04 deg, peak n 8.72 / 10.25 / **12.69 g** at zeta 0.02 / 0.05 / 0.10 (A-P5 12 g: the zeta-0.10 exceedance existed at p6, 12.41 g). Foot force max 78.7 N. Static tip-over on the drawn pads (`tipover_t083.txt`): 29.48 deg narrow (29.44 at the p6 CG 23.91: the drawn pads have never met A-P9's 30 deg; the analysis pad geometry is designed for 30.5 deg and is not drawn: pre-existing).

### 5.3 Rows at x2.23 (`strength_table_t083.md`, `strut_clamp_t083.md`; method of t077p8_path.py / t077p7_strength.py, unchanged)
| Part (min RF of class-RF rows) | p8 | T-083 zeta 0.02 | zeta 0.05 | zeta 0.10 |
|---|---|---|---|---|
| Fin node FIN-005 / FIN-009 / straps | 1.12 | 1.24 | **1.11** | 0.83 (N3 fillet, N4a strap lap) |
| Rib FIN-002 25x23 | 1.32 | 1.14 | 1.16 | 1.06 |
| Skin, 3 plies | 1.16 | 1.32 | 1.16 | 0.76 (K1), 0.88 (K2) |
| Centre node CGE-006 + WNG-013 | 1.04 | 1.16 | 1.18 | **0.66** (C3 flange bond), 0.77 (C1), 0.79 (C2) |
| Bridge CGE-004 | 1.03 | 1.39 | 1.21 | 0.93 (B1) |
| Wing section P15 / P16 | 1.23 | 1.39 | 1.23 | 0.80 (P15) |
| Strut CGE-005 + R4 clamp CGE-007 | 1.01 | 1.40 | 1.13 | 0.87 (R4 junction), 0.89, 0.90 (Euler) |
| Root block FIN-003 as drawn | 0.37 | 0.44 | 0.39 | 0.25 |
Governing zeta-0.10 case: "hard 7/7 combo, mu 0.30": half-wing My 15.62 N m (p8 8.76; zeta 0.02: 8.87), fin My into the cell 20.26 (13.29), rib My 18.15 (10.01). The cell as drawn is adequate if TP-3 measures pad zeta <= 0.05; at 0.10 it needs regrowth (centre flange area x1.5, skin +1 ply, sleeve apothem, fillets, bridge and strut sections: EST +35-50 g, CG +1.5-2.5 mm, not drawn).
Rib both ways: 25x23 as drawn: R1 1.14 (z 0.02) / 1.06 (all). 14x12: R1 **0.33** (z 0.02) / 0.30 (all) on tau 30 MPa: **coupon line about 92 MPa** (30 / 0.326, torsion-dominated row, EST; 99 MPa over all zeta), was 79 MPa; and its root-block bond (D14 x 31) is 0.67, so 14x12 also needs a longer socket (about 47 mm, EST). Integrity class (outside the minimum): B3 0.74, C3p 0.46.

## 6. Mass build-up against p8 (drawn, geometry arithmetic)
p8 drawn 1,579.2 g -> T-083 drawn 1,650.6 g (+71.4 g): motors +10.0 (4 x 2.5), X-mounts with M3 hardware +36.8 (4 x 9.2; the old M2.5 screws stay inside the 30 g HRD-001 lump, so this is conservative by about 2.5 g per motor), phase-lead extensions +25.6 (100 mm stock leads: 5.40 m of 20 AWG at 7.1 g/m in HRN-001, was about 1.8 m), cups +5.1, adapters + washers -2.8, nuts -6.0, cage shift +0.9, remainder rounding. CG moves forward 27.03 -> 21.34 mm drawn because almost all of it sits on the cage.

## 7. BOM (`T083_data/BOM-T083.csv`, `bom_t083.py` -> `bom_t083_out.txt`, options `bom_t083_options.txt`)
Changes against BOM-P8: P01 -> X2216 V3 short shaft $22.99 x 5 RMRC (backorder); W10 XT90 pigtails $12.99 (V); W07 x2 (5.4 m of extension); the study's reads V03 $129.01, R09 $15.36, R10 8x6 $8.50; R05 note (M3x14, M3 nyloc, M5 nyloc in the lump). Crash reserve by definition (pack + motor + servo + airframe set incl. R15, x1.1025 + 3 shipments).
| Scenario | Total | Margin |
|---|---|---|
| **T-083 as drawn (rib 25x23)** | **2,006.66** | **-6.66** |
| rib 14x12 after the coupon (R15 dropped) | 1,871.21 | +128.79 |
| no spare motor (P01 qty 4) | 1,981.31 | +18.69 |
| W07 6 m only | 2,004.47 | -4.47 |
| long-shaft 85810 at $18.99 (reference: does not fit the CAD) | 1,980.20 | +19.80 |
U / EST +30 % (information): see `bom_t083_out.txt`. The study's $1,985.76 assumed the long-shaft motor, $10 of adapters, $12 EST of XT90 and 4 m of lead wire.

## 8. Gates (`T083_data/gates/`, driver `run_gates_t083.sh`)
Three runs: run 1 (all gates) found three CAD issues, fixed (s3.3); run 2 re-ran the CAD gates; run 3 re-ran build, collide pose 21 and assembly after the last fix. Run-1 / run-2 outputs are kept in `gates/run1/`, `gates/run2/`; the summary of all runs is `gates/gates_summary.txt`.
| Gate | Run | Exit | Time | Result |
|---|---|---|---|---|
| build_a | standalone after run 3 | 1 | 16 s | 10 modules, **1 error: graph:mass 1,651 g > 1,500 g MASS-GATE limit (not relaxed)**; otherwise clean. Runs 2-3 hit OSError 22 writing `cad/model/wing/interfaces.json` (Windows file lock, cleared on retry) |
| `A_ELEV_POSE=21 collide_a.py` | 3 | 0 | 982 s | **PASS**, 581 bodies, 129 parts, static / -21 / +21: 0 pairs > 0.05 mm; wire ends 0, folds 0. Run 1 FAIL: E-HRN-03 strand x raceway HRN-003-L 0.065 mm (fixed: window +0.4 mm) |
| `collide_a.py --linkage-poses` | 2 | 0 | 1,129 s | **PASS**, 18 poses (run 1: the same static hit) |
| `a_assembly.py` | 3 | 0 | 2,243 s | **PASS**, 66 steps, 129 / 129 parts, 0 blocked. Run 1: struts B0j1/B0j2 0.81 mm (push axis hard-coded for 12 mm) and B1 clamp x skin 0.30 mm; run 2: B1 0.095 mm at 1.0 mm slot clearance; run 3 at 1.5 mm: clear |
| wire_inventory | 2 | 0 | 10 s | exposed 0.609 strand-m (p8 0.502), total 11.909 |
| cad_mass | 2 (and after run 3) | 0 | 8 s | 1,650.6 g, CG 21.34 mm, SM 7.90 % |
| `mission_gate_a.py --o4b` | 1 | 0 | 0 s | O4b CAD basic 1,650.6 g, CG 21.34 mm, SM 7.90 %, 2,800 mAh pack (BATT_LOW at 784 mAh) |
| `prop_a.py --sched --mass 1.912` | 1 | 0 | 8 s | cap 1.000 at every voltage; derate 0.93: T/W fresh 2.696, sag 2.139, window +12.5 % (no download); fixed 0.90 cap +4.6 % |
| `proofs/run_all.py` | 1 | 1 | 1 s | **8 failing claims (11 strict errors), was 15 / 22 at p8**: the 5 known (horn rib foam hold / stall, elevon torsion foam, horn bearing stall, linkage free-play) and 3 mass claims (MASS-PRED 1.89 kg, MASS-GATE-ROOM, CUTS-REQUIRED 417.9 g); plus FLUTTER-ELEVON-NOM UNVERIFIED (as p8). WINDOW-PRED, WINDOW-MASS, CRUISE-AVAIL, CG-HI, CG-TRIM-AFT, TW-FRESH-PRED, TW-SAG-PRED now pass |
| bbox (`t083_bbox.py`) | after run 3 | 0 | 8 s | x 496.9 / y 900.0 / z 465.2 mm |
| drawings | 3 | 0 | 221 s | 49 / 49 composed; "printed parts not in one piece: AVN-010" (as before) |
| build guide | 3 | 0 | 4 s | 2,317 lines, 66 steps, 46.8 h EST |
| parts_links | 2 | 0 | 4 s | written (P01 still links BOM-A's MN2212 line: BOM-A not edited) |
| `tools/ledger_audit.py` | - | 0 | - | 0 errors (`ledger_audit.txt`) |

## 9. Exposed wires (`gates/gate_wire_inventory.txt`, `cad/out/wire_inventory.json`)
Total exposed 0.609 strand-m (p8 0.502). New: each X2216 phase strand, about 8.4-8.9 mm from the can exit (radial, base end) round a 4 mm bend into the cup plate hole; 12 strands = 0.10 strand-m. Reason: the motor's leads leave the can sideways at the base, and the X-mount holds the base 3 mm off the plate, so the lead cannot enter the plate inside the can footprint; heat-shrink from the motor covers the first part (drawing). Pack leads 2 x about 133 mm (+3 mm each from the 3 mm pack shift; reason as p8: the pack must come out of the tray). Unchanged: balance lead 64 mm, battery tail 42 mm, servo lead ends 2 x 12 mm, GPS 3 mm.

## 10. Proposed text (not applied)
**CHANGE-LOG (T-083, D-227 implementation; ladder: rung 3 rearrange for the mount and the cage, rung 2 geometry for the cup and lead hole, no limit change):** "X2216 integrated as the V3 SHORT-shaft 880KV (RMRC 84776, $22.99, backorder): SunnySky's drawing puts the long-shaft (85810) shaft 16 mm out of the base, into the arm tube. Motor modelled from the SunnySky drawing; mounted on its supplied X-mount (arms on the plate diagonals, 4 x M3x14 + nyloc at |y|, |z| 12 mm), because the 19 / 16 base pattern cannot clear the arm sleeve with screws from behind; lead hole moved to y 18 mm, plate +6 mm, collar to 20.5 mm; M5 nyloc instead of the bullet nut (size not published; keeps the box). Cage, pack and tray windows 3 mm forward. Pad plateau 36 N (30 x 1.912 / 1.705 = 33.6 N tilts 3.14 deg). Tallied 1,669.8 g, 1.913 kg, CG 24.41 mm, SM 6.65 %, window +11.0 %, T/W 2.59 / 2.07, cruise 223 s; A-P6 17.71 > 17.0 (gap); D-226 rows pass at pad zeta <= 0.05 (min 1.11), fail at 0.10 (min 0.66); BOM $2,006.66 (-$6.66). p6 demand bug: simulated at 1.64 kg."
**TEST-PLAN-O4B TP-1 (replace the MN2212 lines):** "1 X2216 V3 880KV + APC 9x4.5MR (+ MRP). Model (prop_a EST): sag 14.92 V rest, all four at duty 1.0: 10,343 rpm, 1,185 gf per motor table, 15.15 A per motor, bus 13.10 V; fresh at the 72 A pack limit: 11,358 rpm, 1,434 gf, 18.1 A. Step 5: derate = gf(10,343 rpm) / 1,185. Pass: derate >= 0.889 (the 204.6 s cruise need at 1.913 kg, 1,053 gf at 10,343 rpm; A-P3 alone needs 0.824 = 976 gf); current at that rpm within +-10 % of 15.15 A; rpm at full throttle on a fresh pack <= 11,667 (APC MR limit) with the rpm from the audio FFT or the ESC telemetry; one motor <= 24.9 A EST (450 W / 16.8 V x 12.1/13) and <= 32 A for 30 s (maker). Step 6 hover: about 516 gf at 1.913 kg. Cross-check against SunnySky's 14.8 V table (16.3 A, 1,180 gf at 10,972 rpm, prop variant not stated). Failure branch unchanged (AM-016)."
**TP-2:** "Q_M_BAT_CURR_MAX 72; spin_cap.lua table 1.0 at every voltage, failsafe 1.0; pass: cap reads 1.0 +-0.01 at 16.8 / 16.0 / 15.4 / 14.9 V, the battery-current limiter holds <= 72 A with four motors at full throttle on a fresh pack (needs a 4-motor stand or the built aircraft tethered), the H743-Wing current sensor reads to >= 80 A (range "—")."
**TP-3 (add):** "Pad zeta acceptance: the D-226 cell, struts and clamps as drawn need a pad with zeta <= 0.05 (T-083 s5.3); plateau 36 N at 24 mm usable; drop at 1.913 kg."
**Rib torsion coupon:** line 79 -> about 92 MPa (T-083 demand, zeta 0.02), and the 14x12 root-block socket bond needs about 47 mm (EST).
**MASS-GATE basis:** PRP-001 67.5 x 4 (SunnySky page), PRP-006 9.2 x 4 (CALC / EST), PRP-004 3.6 x 4, PRP-005 1.4 x 4, CGE-003 8.96 x 4 (voxel), HRN-001 phase extensions 38.4 g (5.40 m).
**BOM:** BOM-T083.csv lines P01, W07, W10, V03, R09, R10, R05 note.

## 11. Data index (`T083_data/`)
Propulsion: `t083_prop.py` (-> `prop_t083.md`), `t083_packcap.py` (-> `packcap_t083.md`), `t083_metrics.py`. CAD: `t083_patch_propulsion.py`, `t083_patch_cup.py`, `t083_bbox.py`, `t083_mass_audit.py` (-> `t077_rows_h0.25_only.json`, `mass_audit_cup.txt`), `t083_write_printed_mass.py`, backups `*_p8_backup.*`. Landing: `t083_land_sweep.py` (-> `land_sweep_probe*.txt`), `t083_demand.py` (-> `demand_t083.json`, `demand_t083_stdout.txt`, `fea/demand_t083.npz` git-ignored), `t083_path.py` + `t083_compare.py` (-> `strength_<tag>.json/.txt`, `strength_table_t083.md`), `t083_strut_clamp.py` (-> `strength_sc_*.json`, `strut_clamp_t083.md`), `t083_tipover.py` (-> `tipover_t083.txt`), `t083_cup_checks.py` (-> `t083_cup_checks.md`). BOM: `BOM-T083.csv`, `bom_t083.py`, `bom_t083_out.txt`, `bom_t083_options.txt`. Gates: `run_gates_t083.sh`, `gates/`.

## 12. Limits
- Thrust and current are the repo's EST model with maker Kv / Rm / I0; the maker's table uses an unstated APC 9x4.5 variant. The 24.94 A line and the 9.2 g mount mass are EST; the X-mount material, lead gauge, recess / counterbore depths and the exact lead-exit height are "—".
- The 67.5 g motor mass is taken to include the 100 mm leads (not stated); if it does not, +about 2 g per motor.
- Landing results are rigid-body with the D-222 pad law; strength rows are hand bounds with EST allowables, no FEA. The zeta-0.10 regrowth mass is an estimate, not drawn.
- The 3 % download, derate 0.93, pack R 30 mohm and I0 at all voltages are EST, as before.
