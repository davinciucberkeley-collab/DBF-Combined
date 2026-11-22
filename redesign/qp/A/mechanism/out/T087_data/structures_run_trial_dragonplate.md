> **Scope (T-066, 2026-11-22): re-baselined to the CURRENT concept A geometry** (CAD at commit ac983050; supersedes the T-065 note that this file held the QP-3 iteration-1 baseline). Tubes: spar 12x10, arms 12x10 continuous (D-202), bridge 16x14 + two 8x6 struts, rib 25x22 (D-226), fin tube 16x14; D-226 bulkheads / centre node / 3-ply skin, D-227 / D-228 X2216 V3 880KV on APC 9x4.5MR, D-229 6061 FIN-003 fitting. Mass 1.912 kg predicted (T-083b), CAD basic 1.6621 kg (cad_mass.json 1.66206). Demand and DAF of T-083 / T-083b reused (pad 36 N / 24 mm, 21 cases (landing_path_a.cases(False); the T-083 text says 23, the function returns 21) x zeta 0.02 / 0.05 / 0.10 x mu 0.40 / 0.30; DAF 2.23 wing, 1.97 tubes). The ledger row's geometry list (arms 12x10, rib 14x12, bridge 16x14 + struts 6x4.5) is stale: the CAD has rib 25x23 and struts 8x6.

## 1. Structural mass: CAD declared masses (geometry arithmetic; `a_model.PARTS`, 131 parts)
| Group | CAD declared g | note |
|---|---|---|
| Wing (WNG: core, skins, bulkheads, spar, plugs, elevons, balance, caps, dampers) | 296.0 | |
| Fins (FIN: tube, rib, 6061 root fitting, node, fairings) + feet (GER) | 242.0 | |
| Cage (CGE: hub, arm tubes, cups, doublers, pins, bridge, struts, clamps, centre node, tray) | 240.8 | |
| Propulsion (PRP: motors, props, adapters, nuts, X-mounts, ESC) | 391.0 | |
| Power (PWR: pack, straps, pad) | 282.4 | |
| Avionics (AVN, HWC-001/003) | 68.1 | |
| Mechanisms (MEC, HWC-002) | 47.7 | |
| Harness (HRN) | 66.3 | |
| Hardware lump (HRD) | 27.8 | |
| **Total basic (CAD)** | **1662.1** | cad_mass.json mass_basic_kg 1662.1 g: match |

Predicted = basic x 1.1174 + 0.032 x 1.47 (CALC-A-MASS-PRED, T083b_report.md s4.1): drawn 1.9042 kg; tallied (+7.0 g undrawn shoe cups EST, T-083b) 1.912 kg (used for all loads below). MASS-GATE limit 1.5 kg: the predicted mass exceeds it by 412 g (gate not relaxed; build_a reports it, T-083b s6). The old bottom-up roll-up (iteration-1 tubes, 'MASS-GATE allocation' column) is replaced by the CAD part table above; the structure-only groups (Wing + Fins + Cage + Hardware) are 807 g against the frozen 473 g of iter3_run.md (+ D-187 balance lead 21 g = 494 g).

FE model inputs (all from the CAD part table, g): wing_g 308.64, avionics_g 175.50, centre_extra_g 83.98, pack_g 295.70, hub_extra_g 59.12, motor_g 101.72, foot_pad_m 5.00, root_g 31.88; bridge_yv 0.285 (STRUT_E y), x_hub -78.0 mm, x_fin 294 mm, fin tube foam 3 mm + tape 55 g/m2 carried from the iteration-3 setup (EST).

## 2. C1 loads (hand calculation; limit unless marked; ult = 1.5 x limit; mass 1.912 kg)
Vs 13.62 m/s (CLmax 0.75 EST), VA = Vs sqrt(3.4) = 25.1, VC 17, VD 24 (D-186). a = 3.74/rad, mu_g 15.5, Kg 0.656.
| Case | n | Note |
|---|---|---|
| Gust U 8 m/s at VC | 3.39 -> stall-limited 1.56 | wing cannot make the gust n at 17 m/s |
| Gust U 4 m/s at VD (half, ASM-C1-UDE-D-FRAC) | 2.69 (stall line 3.10) | |
| Manoeuvre limit | +3.4 / -1.5 | A-P13 floor governs; ult +5.1 / -2.25; VA = 25.1 ~ VD |
| Spar root bending, flight n 3.4 (elliptical lift, inertia relief) | 1.73 N m (6.09 unrelieved) | design uses unrelieved 6.09 limit; relief lumps: wing half 154 g at 0.225, 2 motor assemblies 203 g at 0.228, arm half 31 g at 0.114, fin / rib / feet half 121 g at 0.38 |
| Hover 8 m/s gust broadside (plate Cd 2.0): wing force 17.2 N, spar root | 1.94 N m | below flight case |
| Cage pitch moment, upper pair at the cap (13.08 N each, T-083 s4) / lower pair 1.0 N | 3.77 N m on the bridge | the cap is the bound (A-P8 limit); hover thrust per motor 4.69 N |
| Prop strike (blade stops, one motor, 30 N along thrust EST; K09-L P1 fuse idea) | arm root 8.3 N m; bridge 4.7 N m | damage case |
| Transport drop 0.3 m (v 2.43 m/s), cradle stroke s, efficiency 0.5 (ASM-C1-CRUSH-EFF) | n = v^2/(2 g eta s): s 25 mm: 24.0 g; s 35 mm: 17.1 g; s 50 mm: 12.0 g; s 60 mm: 10.0 g | `-` box cradle not designed; s needs >= 40 mm for n <= 15 |
| Landing (see s5) | foot plateau 36 N, 24 mm, 4 feet | worst-case values from landing_a.py are tabulated in s5 |

## 3. C2 wing: spar and foam (spar 12x10, tube alone: the D-226 skin, bulkheads and foam stiffen it, none credited here)
| Check | Stress | Allowable | MS | Result |
|---|---|---|---|---|
| Spar root bending, ult x fitting, unrelieved 10.5 N m | 120 MPa | 350 | +1.93 | PASS |
| Spar shear at root (V / (A/2), KF) | 3.2 MPa | 30 | +8.4 | PASS |
| Spar tip deflection at n 3.4, elliptical load (CALC, E 70 GPa, EI 36.9 N m2, tube alone) | 7.6 mm of 450 mm semispan (1.7 %) | 5 % (EST) | | PASS |
| Same, tip-load bound (all lift at the tip, not physical) | 26.3 mm (5.8 %) | 5 % (EST) | | info (bound) |
| Spar wall under the clamp / plug zones (hoop) | PETG plugs WNG-003..005 (1.42 g each, parts table) at y = 0, +-0.285 (strut clamp), +-0.38 (rib clamp): C2 rule (unplugged ring failed by 20x) | - | - | plugs in the mass table |
| Foam shear around the spar from the bridge moment 3.77 N m (zone |y| <= 0.1, r 6 mm, x KP): the iteration-1 row | 180 kPa | 86 | -0.52 | **NOT A LOAD PATH since D-226**: the centre node (CGE-006, sleeve slip-fit on the spar, not bonded) and the bulkheads take the centre torque; judged by the C1-C7 rows of T083b s6 (min 1.09 at zeta 0.05); value shown for the record, not counted |
| Foam bearing at the fin slot (2 x 20 N side load, 65 x 23 mm, x KP): iteration-1 row | 57 kPa | 103 | +0.81 | PASS; the fin node is now the D-226 bulkhead + plates (rows N1-N6, T083b) so this is secondary |
| Foam shear, lift into spar slot (n 3.4, 1.912 kg, 32 mm of bond, x1.5) | 3.3 kPa | 86 | +25 | PASS |
| Arm / motor attachments | none in foam: the cage hangs from the spar through the 6061 centre node (D-226) and the strut clamps; foam sees only the node pocket (R >= 3 mm corners, C6 rule) | - | - | - |
Fin elevon note: elevon span y 0.04-0.35 (common.py ELEV_Y0 / ELEV_Y1); the fin tube plane is y 0.38 (inner flank of the rib 0.3705).

## 4. C4 modes vs rotor orders (FEA-lite: 3-D Euler-Bernoulli beam frame, free-free, fe_a.py; no shell or solid model)
- hover derate 1.0 (1.912 kg, prop_a.py hover): 6850 rpm: 1P 114 Hz, 2P 228 Hz
- hover derate 0.93 (1.912 kg): 7104 rpm: 1P 118 Hz, 2P 237 Hz
- hover lean 1.3 W (8 m/s gust, derate 0.93): 8093 rpm: 1P 135 Hz, 2P 270 Hz
- cruise 17 m/s (QP-3, EST carried, mid): 7450 rpm: 1P 124 Hz, 2P 248 Hz
- all four at the 72 A limit, fresh: 11358 rpm: 1P 189 Hz, 2P 379 Hz
- all four duty 1.0, sag 14.92 V: 10343 rpm: 1P 172 Hz, 2P 345 Hz
Excluded band for strongly coupled modes (iter3 rule: f <= band_low / 1.2 or f >= 1.2 band_high over the hover and cruise rpm above): **95-324 Hz** (iter3_run.md MN2212: 84-304 Hz). The capped / full-duty states (10343-11358 rpm, 1P 172-189 Hz, 2P 345-379 Hz) are transients judged by the forced-response sweep, as iter3 did for 9,349 / 10,142 rpm.
FE model mass 1673 g vs CAD basic 1662 g (the model carries the declared masses; tubes by A x rho, lumps as above). Modes solved: 130 per corner, highest 4532 Hz (nom).

Modes with strong coupling to the motors (|phi| at motors in plane cy or thrust cx >= 0.5, mass-normalised), kd = E_CF 61 GPa, nom 70, hi 90 (fe_a corners; the PETG moduli are unused because the FE has no printed beam any more):
| Corner | f (Hz) | group | cx / cy (2 decimals) | worst separation to 1P / 2P at the five operating rpm | inside excluded band? | single-mode FC accel on resonance if a rotor order reaches it (m/s2, zeta 0.5 %, info) | Result |
|---|---|---|---|---|---|---|---|
| kd | 8 | spar 54% | 0.00 / 1.75 | 93 % | no | - | PASS (strong, outside the band) |
| kd | 12 | spar 65% | 1.89 / 0.17 | 90 % | no | - | PASS (strong, outside the band) |
| kd | 18 | bridge 61% | 0.00 / 1.72 | 84 % | no | - | PASS (strong, outside the band) |
| kd | 24 | spar 78% | 0.73 / 0.75 | 79 % | no | - | PASS (strong, outside the band) |
| kd | 28 | arm 53% | 2.56 / 0.57 | 75 % | no | - | PASS (strong, outside the band) |
| kd | 29 | spar 86% | 0.56 / 0.00 | 75 % | no | - | PASS (strong, outside the band) |
| kd | 33 | arm 100% | 3.06 / 0.35 | 71 % | no | - | PASS (strong, outside the band) |
| kd | 33 | arm 100% | 0.35 / 3.06 | 71 % | no | - | PASS (strong, outside the band) |
| kd | 35 | arm 99% | 0.31 / 2.92 | 69 % | no | - | PASS (strong, outside the band) |
| kd | 37 | arm 90% | 0.89 / 2.49 | 67 % | no | - | PASS (strong, outside the band) |
| kd | 39 | arm 97% | 2.60 / 0.00 | 66 % | no | - | PASS (strong, outside the band) |
| kd | 47 | spar 64% | 0.89 / 0.00 | 59 % | no | - | PASS (strong, outside the band) |
| kd | 57 | arm 63% | 1.24 / 1.23 | 50 % | no | - | PASS (strong, outside the band) |
| kd | 72 | rib 42% | 0.56 / 0.36 | 37 % | no | - | PASS (strong, outside the band) |
| kd | 203 | spar 68% | 0.02 / 0.54 | 11 % | YES | 0.12 (0.004 of 30) | **FAIL** (strong by the 0.5 rule, in band; limit not relaxed) |
| kd | 439 | spar 48% | 0.13 / 0.67 | 63 % | no | - | PASS (strong, outside the band) |
| kd | 526 | bridge 77% | 0.06 / 0.63 | 95 % | no | - | PASS (strong, outside the band) |
| nom | 8 | spar 54% | 0.00 / 1.73 | 93 % | no | - | PASS (strong, outside the band) |
| nom | 12 | spar 65% | 1.87 / 0.18 | 89 % | no | - | PASS (strong, outside the band) |
| nom | 19 | bridge 62% | 0.00 / 1.74 | 83 % | no | - | PASS (strong, outside the band) |
| nom | 26 | spar 78% | 0.75 / 0.75 | 77 % | no | - | PASS (strong, outside the band) |
| nom | 30 | arm 53% | 2.56 / 0.57 | 73 % | no | - | PASS (strong, outside the band) |
| nom | 31 | spar 86% | 0.56 / 0.00 | 73 % | no | - | PASS (strong, outside the band) |
| nom | 35 | arm 100% | 1.85 / 2.46 | 69 % | no | - | PASS (strong, outside the band) |
| nom | 35 | arm 100% | 2.46 / 1.85 | 69 % | no | - | PASS (strong, outside the band) |
| nom | 38 | arm 99% | 0.31 / 2.92 | 67 % | no | - | PASS (strong, outside the band) |
| nom | 40 | arm 90% | 0.90 / 2.48 | 65 % | no | - | PASS (strong, outside the band) |
| nom | 42 | arm 97% | 2.60 / 0.00 | 64 % | no | - | PASS (strong, outside the band) |
| nom | 50 | spar 64% | 0.89 / 0.00 | 56 % | no | - | PASS (strong, outside the band) |
| nom | 60 | arm 60% | 1.20 / 1.22 | 47 % | no | - | PASS (strong, outside the band) |
| nom | 75 | rib 41% | 0.65 / 0.43 | 35 % | no | - | PASS (strong, outside the band) |
| nom | 217 | spar 68% | 0.02 / 0.54 | 5 % | YES | 0.14 (0.005 of 30) | **FAIL** (strong by the 0.5 rule, in band; limit not relaxed) |
| nom | 475 | spar 43% | 0.10 / 0.65 | 76 % | no | - | PASS (strong, outside the band) |
| nom | 564 | bridge 77% | 0.06 / 0.63 | 109 % | no | - | PASS (strong, outside the band) |
| hi | 10 | spar 54% | 0.00 / 1.75 | 91 % | no | - | PASS (strong, outside the band) |
| hi | 14 | spar 65% | 1.89 / 0.17 | 87 % | no | - | PASS (strong, outside the band) |
| hi | 23 | bridge 61% | 0.00 / 1.72 | 80 % | no | - | PASS (strong, outside the band) |
| hi | 30 | spar 78% | 0.72 / 0.75 | 74 % | no | - | PASS (strong, outside the band) |
| hi | 34 | arm 53% | 2.56 / 0.57 | 70 % | no | - | PASS (strong, outside the band) |
| hi | 35 | spar 86% | 0.56 / 0.00 | 69 % | no | - | PASS (strong, outside the band) |
| hi | 40 | arm 100% | 3.08 / 0.09 | 65 % | no | - | PASS (strong, outside the band) |
| hi | 40 | arm 100% | 0.09 / 3.08 | 65 % | no | - | PASS (strong, outside the band) |
| hi | 43 | arm 99% | 0.31 / 2.92 | 63 % | no | - | PASS (strong, outside the band) |
| hi | 45 | arm 90% | 0.89 / 2.49 | 60 % | no | - | PASS (strong, outside the band) |
| hi | 47 | arm 97% | 2.60 / 0.00 | 59 % | no | - | PASS (strong, outside the band) |
| hi | 57 | spar 64% | 0.89 / 0.00 | 51 % | no | - | PASS (strong, outside the band) |
| hi | 69 | arm 64% | 1.24 / 1.23 | 40 % | no | - | PASS (strong, outside the band) |
| hi | 88 | rib 42% | 0.55 / 0.35 | 23 % | no | - | PASS (strong, outside the band) |
| hi | 246 | spar 68% | 0.02 / 0.54 | 1 % | YES | 0.18 (0.006 of 30) | **FAIL** (strong by the 0.5 rule, in band; limit not relaxed) |
| hi | 533 | spar 48% | 0.13 / 0.68 | 98 % | no | - | PASS (strong, outside the band) |
| hi | 639 | bridge 77% | 0.06 / 0.63 | 137 % | no | - | PASS (strong, outside the band) |

Strongly coupled modes inside the excluded band: kd 203 Hz, nom 217 Hz, hi 246 Hz.
Reading of the FAIL rows (T-084 root cause, `mechanism/out/T084_report.md` s2, `T084_data/modes_final.txt`): the mode is the wing's antisymmetric IN-PLANE (chordwise) bending with the cage swaying sideways on the bridge and struts. In this model the wing's in-plane stiffness is the 12x10 spar alone (EI 37 N m2); the drawn D-226 wing (foam core + 3-ply glass skin + cove CF strip) has 330-6,800 N m2 nominal and 185-1,650 N m2 at the lower bound (`T084_data/cell_props.txt`), so this mode is an artifact of the beam model: with the cell credited it leaves the band at every corner (s4b). Its coupling grew 0.45 -> 0.52 mainly because the strut end moved inboard 0.300 -> 0.285 m (0.42 -> 0.55) and the fin-root lumps grew 6 -> 32 g (0.48 -> 0.53). The rule is not relaxed here; s4b shows what the cell-credited model fails instead.
- kd: highest strongly coupled mode below the band 72 Hz (limit 95, margin 33 %); lowest above the band 439 Hz (limit 324, margin 36 %)
- nom: highest strongly coupled mode below the band 75 Hz (limit 95, margin 27 %); lowest above the band 475 Hz (limit 324, margin 47 %)
- hi: highest strongly coupled mode below the band 88 Hz (limit 95, margin 9 %); lowest above the band 533 Hz (limit 324, margin 65 %)

Weakly coupled modes (cx, cy < 0.5: fin out-of-plane, rib, spar, centre) 20-800 Hz. Each row carries its coupling and the FORCED-RESPONSE verdict (the 20 % separation screen is not the test for these, D-185 as ruled): single mode on resonance, zeta 0.5 % (EST), 4 rotors in the worst phase, U 1.0 g mm per rotor for 1P, 2P ripple 5 % of the static thrust at that rpm (EST); FC acceleration summed over the three axes (a bound on the per-axis VIBE, limit 30 m/s2, ardupilot.org/copter/docs/common-measuring-vibration.html, 2026-11-15):
| Corner | f (Hz) | group | coupling max(cx, cy) (cx / cy) | rotor order reaches it in 6,000-11,415 rpm? | single-mode FC accel on resonance (m/s2) | fraction of 30 | separation to the five operating rpm | Verdict |
|---|---|---|---|---|---|---|---|---|
| kd | 148 | spar 57%, rib 31% | 0.07 (0.00 / 0.07) | 1P at 8,859 rpm | 0.00 | 0.000 | 9 % | PASS by forced response |
| kd | 165 | spar 64%, bridge 18% | 0.06 (0.06 / 0.00) | 1P at 9,876 rpm | 0.00 | 0.000 | 22 % | PASS by forced response |
| kd | 204 | spar 67%, rib 23% | 0.03 (0.03 / 0.01) | 2P at 6,127 rpm | 0.67 | 0.022 | 11 % | PASS by forced response |
| kd | 290 | fin 66%, rib 31% | 0.00 (0.00 / 0.00) | 2P at 8,688 rpm | 0.00 | 0.000 | 7 % | PASS by forced response |
| kd | 290 | fin 64%, rib 31% | 0.00 (0.00 / 0.00) | 2P at 8,711 rpm | 0.01 | 0.000 | 8 % | PASS by forced response |
| kd | 327 | fin 92%, spar 6% | 0.11 (0.02 / 0.11) | 2P at 9,806 rpm | 0.18 | 0.006 | 21 % | PASS by forced response |
| kd | 330 | fin 89%, spar 9% | 0.01 (0.01 / 0.00) | 2P at 9,885 rpm | 0.08 | 0.003 | 22 % | PASS by forced response |
| kd | 360 | fin 95%, spar 4% | 0.07 (0.02 / 0.07) | 2P at 10,793 rpm | 0.17 | 0.006 | 33 % | PASS by forced response |
| kd | 360 | fin 78%, spar 19% | 0.02 (0.02 / 0.00) | 2P at 10,799 rpm | 0.44 | 0.015 | 33 % | PASS by forced response |
| kd | 371 | spar 53%, fin 23% | 0.04 (0.04 / 0.00) | 2P at 11,142 rpm | 2.58 | 0.086 | 38 % | PASS by forced response |
| kd | 373 | spar 78%, bridge 11% | 0.07 (0.00 / 0.07) | 2P at 11,183 rpm | 0.00 | 0.000 | 38 % | PASS by forced response |
| kd | 419 | bridge 46%, arm 26% | 0.25 (0.00 / 0.25) | no (unreachable) | - | - | 55 % | PASS (no rotor order reaches it) |
| kd | 440 | bridge 68%, spar 28% | 0.10 (0.04 / 0.10) | no (unreachable) | - | - | 63 % | PASS (no rotor order reaches it) |
| kd | 459 | arm 92%, bridge 7% | 0.05 (0.04 / 0.05) | no (unreachable) | - | - | 70 % | PASS (no rotor order reaches it) |
| kd | 464 | arm 100%, spar 0% | 0.00 (0.00 / 0.00) | no (unreachable) | - | - | 72 % | PASS (no rotor order reaches it) |
| kd | 464 | arm 100%, bridge 0% | 0.00 (0.00 / 0.00) | no (unreachable) | - | - | 72 % | PASS (no rotor order reaches it) |
| kd | 464 | arm 92%, spar 5% | 0.24 (0.01 / 0.24) | no (unreachable) | - | - | 72 % | PASS (no rotor order reaches it) |
| kd | 478 | spar 79%, bridge 13% | 0.02 (0.01 / 0.02) | no (unreachable) | - | - | 77 % | PASS (no rotor order reaches it) |
| kd | 486 | bridge 89%, arm 9% | 0.15 (0.00 / 0.15) | no (unreachable) | - | - | 80 % | PASS (no rotor order reaches it) |
| kd | 495 | bridge 89%, spar 7% | 0.06 (0.04 / 0.06) | no (unreachable) | - | - | 84 % | PASS (no rotor order reaches it) |
| kd | 520 | bridge 86%, spar 14% | 0.00 (0.00 / 0.00) | no (unreachable) | - | - | 93 % | PASS (no rotor order reaches it) |
| kd | 553 | arm 59%, bridge 35% | 0.38 (0.00 / 0.38) | no (unreachable) | - | - | 105 % | PASS (no rotor order reaches it) |
| kd | 660 | arm 74%, bridge 23% | 0.38 (0.38 / 0.07) | no (unreachable) | - | - | 145 % | PASS (no rotor order reaches it) |
| kd | 683 | arm 81%, bridge 19% | 0.39 (0.39 / 0.07) | no (unreachable) | - | - | 153 % | PASS (no rotor order reaches it) |
| kd | 719 | spar 70%, bridge 19% | 0.01 (0.01 / 0.00) | no (unreachable) | - | - | 167 % | PASS (no rotor order reaches it) |
| kd | 738 | spar 92%, bridge 3% | 0.02 (0.00 / 0.02) | no (unreachable) | - | - | 174 % | PASS (no rotor order reaches it) |
| kd | 766 | arm 100%, spar 0% | 0.32 (0.19 / 0.32) | no (unreachable) | - | - | 184 % | PASS (no rotor order reaches it) |
| kd | 766 | arm 100%, spar 0% | 0.32 (0.32 / 0.19) | no (unreachable) | - | - | 184 % | PASS (no rotor order reaches it) |
| kd | 766 | arm 93%, spar 5% | 0.36 (0.00 / 0.36) | no (unreachable) | - | - | 184 % | PASS (no rotor order reaches it) |
| kd | 773 | arm 100%, bridge 0% | 0.47 (0.01 / 0.47) | no (unreachable) | - | - | 187 % | PASS (no rotor order reaches it) |
| kd | 773 | arm 98%, spar 1% | 0.37 (0.37 / 0.00) | no (unreachable) | - | - | 187 % | PASS (no rotor order reaches it) |
| kd | 781 | spar 76%, rib 14% | 0.32 (0.01 / 0.32) | no (unreachable) | - | - | 190 % | PASS (no rotor order reaches it) |
| nom | 155 | spar 59%, rib 30% | 0.07 (0.00 / 0.07) | 1P at 9,271 rpm | 0.00 | 0.000 | 15 % | PASS by forced response |
| nom | 176 | spar 64%, bridge 18% | 0.06 (0.06 / 0.00) | 1P at 10,580 rpm | 0.00 | 0.000 | 23 % | PASS by forced response |
| nom | 216 | spar 69%, rib 21% | 0.03 (0.03 / 0.01) | 2P at 6,465 rpm | 0.79 | 0.026 | 6 % | PASS by forced response |
| nom | 310 | fin 66%, rib 31% | 0.01 (0.00 / 0.01) | 2P at 9,297 rpm | 0.00 | 0.000 | 15 % | PASS by forced response |
| nom | 311 | fin 65%, rib 31% | 0.00 (0.00 / 0.00) | 2P at 9,316 rpm | 0.01 | 0.000 | 15 % | PASS by forced response |
| nom | 350 | fin 92%, spar 6% | 0.11 (0.02 / 0.11) | 2P at 10,504 rpm | 0.20 | 0.007 | 30 % | PASS by forced response |
| nom | 353 | fin 89%, spar 9% | 0.01 (0.01 / 0.00) | 2P at 10,589 rpm | 0.09 | 0.003 | 31 % | PASS by forced response |
| nom | 385 | fin 95%, spar 4% | 0.07 (0.02 / 0.07) | no (unreachable) | - | - | 43 % | PASS (no rotor order reaches it) |
| nom | 386 | fin 78%, spar 19% | 0.02 (0.02 / 0.00) | no (unreachable) | - | - | 43 % | PASS (no rotor order reaches it) |
| nom | 396 | spar 78%, bridge 12% | 0.08 (0.00 / 0.08) | no (unreachable) | - | - | 47 % | PASS (no rotor order reaches it) |
| nom | 398 | spar 53%, fin 23% | 0.04 (0.04 / 0.00) | no (unreachable) | - | - | 47 % | PASS (no rotor order reaches it) |
| nom | 439 | bridge 51%, spar 27% | 0.22 (0.00 / 0.22) | no (unreachable) | - | - | 63 % | PASS (no rotor order reaches it) |
| nom | 454 | bridge 65%, spar 18% | 0.07 (0.03 / 0.07) | no (unreachable) | - | - | 68 % | PASS (no rotor order reaches it) |
| nom | 459 | arm 81%, spar 10% | 0.30 (0.08 / 0.30) | no (unreachable) | - | - | 70 % | PASS (no rotor order reaches it) |
| nom | 460 | arm 80%, bridge 17% | 0.06 (0.03 / 0.06) | no (unreachable) | - | - | 71 % | PASS (no rotor order reaches it) |
| nom | 464 | arm 100%, fin 0% | 0.00 (0.00 / 0.00) | no (unreachable) | - | - | 72 % | PASS (no rotor order reaches it) |
| nom | 464 | arm 100%, bridge 0% | 0.00 (0.00 / 0.00) | no (unreachable) | - | - | 72 % | PASS (no rotor order reaches it) |
| nom | 493 | bridge 85%, arm 12% | 0.17 (0.00 / 0.17) | no (unreachable) | - | - | 83 % | PASS (no rotor order reaches it) |
| nom | 502 | bridge 50%, spar 46% | 0.05 (0.04 / 0.05) | no (unreachable) | - | - | 86 % | PASS (no rotor order reaches it) |
| nom | 515 | spar 49%, bridge 45% | 0.07 (0.02 / 0.07) | no (unreachable) | - | - | 91 % | PASS (no rotor order reaches it) |
| nom | 557 | bridge 86%, spar 14% | 0.00 (0.00 / 0.00) | no (unreachable) | - | - | 106 % | PASS (no rotor order reaches it) |
| nom | 589 | arm 61%, bridge 33% | 0.39 (0.00 / 0.39) | no (unreachable) | - | - | 118 % | PASS (no rotor order reaches it) |
| nom | 707 | arm 73%, bridge 23% | 0.38 (0.38 / 0.07) | no (unreachable) | - | - | 162 % | PASS (no rotor order reaches it) |
| nom | 730 | arm 81%, bridge 19% | 0.39 (0.39 / 0.07) | no (unreachable) | - | - | 171 % | PASS (no rotor order reaches it) |
| nom | 771 | spar 70%, bridge 19% | 0.01 (0.01 / 0.00) | no (unreachable) | - | - | 186 % | PASS (no rotor order reaches it) |
| nom | 787 | spar 91%, bridge 5% | 0.01 (0.00 / 0.01) | no (unreachable) | - | - | 192 % | PASS (no rotor order reaches it) |
| hi | 70 | spar 47%, rib 42% | 0.16 (0.00 / 0.16) | no (unreachable) | - | - | 39 % | PASS (no rotor order reaches it) |
| hi | 180 | spar 56%, rib 31% | 0.07 (0.00 / 0.07) | 1P at 10,792 rpm | 0.00 | 0.000 | 21 % | PASS by forced response |
| hi | 200 | spar 64%, bridge 18% | 0.06 (0.06 / 0.00) | no (unreachable) | - | - | 12 % | PASS (no rotor order reaches it) |
| hi | 249 | spar 67%, rib 23% | 0.03 (0.03 / 0.01) | 2P at 7,456 rpm | 0.98 | 0.033 | 2 % | PASS by forced response |
| hi | 352 | fin 66%, rib 31% | 0.00 (0.00 / 0.00) | 2P at 10,555 rpm | 0.00 | 0.000 | 30 % | PASS by forced response |
| hi | 353 | fin 64%, rib 31% | 0.00 (0.00 / 0.00) | 2P at 10,584 rpm | 0.02 | 0.001 | 31 % | PASS by forced response |
| hi | 397 | fin 92%, spar 6% | 0.11 (0.02 / 0.11) | no (unreachable) | - | - | 47 % | PASS (no rotor order reaches it) |
| hi | 400 | fin 89%, spar 9% | 0.01 (0.01 / 0.00) | no (unreachable) | - | - | 48 % | PASS (no rotor order reaches it) |
| hi | 437 | fin 95%, spar 4% | 0.07 (0.02 / 0.07) | no (unreachable) | - | - | 62 % | PASS (no rotor order reaches it) |
| hi | 437 | fin 78%, spar 19% | 0.02 (0.02 / 0.00) | no (unreachable) | - | - | 62 % | PASS (no rotor order reaches it) |
| hi | 451 | spar 53%, fin 23% | 0.04 (0.04 / 0.00) | no (unreachable) | - | - | 67 % | PASS (no rotor order reaches it) |
| hi | 453 | spar 78%, bridge 10% | 0.07 (0.00 / 0.07) | no (unreachable) | - | - | 68 % | PASS (no rotor order reaches it) |
| hi | 510 | bridge 46%, arm 26% | 0.25 (0.00 / 0.25) | no (unreachable) | - | - | 89 % | PASS (no rotor order reaches it) |
| hi | 536 | bridge 67%, spar 29% | 0.10 (0.04 / 0.10) | no (unreachable) | - | - | 99 % | PASS (no rotor order reaches it) |
| hi | 562 | arm 93%, bridge 7% | 0.05 (0.04 / 0.05) | no (unreachable) | - | - | 108 % | PASS (no rotor order reaches it) |
| hi | 568 | arm 100%, bridge 0% | 0.00 (0.00 / 0.00) | no (unreachable) | - | - | 110 % | PASS (no rotor order reaches it) |
| hi | 568 | arm 100%, spar 0% | 0.00 (0.00 / 0.00) | no (unreachable) | - | - | 110 % | PASS (no rotor order reaches it) |
| hi | 568 | arm 93%, spar 4% | 0.22 (0.00 / 0.22) | no (unreachable) | - | - | 111 % | PASS (no rotor order reaches it) |
| hi | 581 | spar 80%, bridge 12% | 0.02 (0.01 / 0.02) | no (unreachable) | - | - | 115 % | PASS (no rotor order reaches it) |
| hi | 595 | bridge 89%, arm 9% | 0.15 (0.00 / 0.15) | no (unreachable) | - | - | 120 % | PASS (no rotor order reaches it) |
| hi | 605 | bridge 91%, spar 6% | 0.06 (0.04 / 0.06) | no (unreachable) | - | - | 124 % | PASS (no rotor order reaches it) |
| hi | 631 | bridge 86%, spar 14% | 0.00 (0.00 / 0.00) | no (unreachable) | - | - | 134 % | PASS (no rotor order reaches it) |
| hi | 672 | arm 58%, bridge 36% | 0.38 (0.00 / 0.38) | no (unreachable) | - | - | 149 % | PASS (no rotor order reaches it) |

Forced response, full rpm sweep (all four rotors at the same rpm, 1P + 2P of all rotors added, worst-phase modal sum, all modes solved above; static thrust law for the 2P term at every rpm = conservative in cruise). Hard-mounted FC (D-186): foam tape taken rigid (mount frequency not measured, EST):
| Corner | zeta | worst FC accel 6,000-11,415 rpm, sum of axes (m/s2) at rpm | per-axis max / sqrt2 (VIBE-like) | MS vs 30 (sum of axes bound) | worst up to 10,343 rpm (all four duty 1.0, sag) | worst up to 9,349 rpm | cruise 7,300-7,600 (T 0.5 N EST) |
|---|---|---|---|---|---|---|---|
| kd | 1.0 % | 26.2 at 11,400 | 11.2 | +0.15 | 19.4 at 10,325 | 15.4 | 7.4 |
| kd | 0.5 % | 26.2 at 11,150 | 11.2 | +0.14 | 19.4 at 10,325 | 15.4 | 7.4 |
| nom | 1.0 % | 24.2 at 11,400 | 11.2 | +0.24 | 19.0 at 10,325 | 15.3 | 7.5 |
| nom | 0.5 % | 24.2 at 11,400 | 11.2 | +0.24 | 19.0 at 10,325 | 15.4 | 7.5 |
| hi | 1.0 % | 23.1 at 11,400 | 11.3 | +0.30 | 18.9 at 10,325 | 15.5 | 7.9 |
| hi | 0.5 % | 23.1 at 11,400 | 11.3 | +0.30 | 18.9 at 10,325 | 15.5 | 7.9 |
Sweep verdict: worst sum-of-axes 26.2 m/s2 (MS +0.14 vs 30 as a bound), worst per-axis rms-like 11.3 m/s2 (MS +1.65): PASS. Closes the T-083 open item 'extend the A-P10(b) sweep to 11,400 rpm' for the beam-FE model.

### 4b. T-084: same beam FE with the D-226 wing cell credited (FEA-lite sensitivity of the wing model; band and coupling rule unchanged)
Wing beam = spar + XPS core + glass +-45 skin plies (1 ply |y| <= 0.075, 3 plies to 0.40) + cove CF strip, spar + foam outboard of 0.40 (`T084_data/t084_cell_props.py`: the section model of landing_path_a P15 / P16; foam E 30 / G 8 MPa EST, ACP glass x Vf 0.70, strip 120 GPa EST). Lower bound: foam x0.5, skin x0.7, no strip. Corners scale the CF parts only. Pack, hub and lumps as above.
| wing model | corner | strong modes IN the band (f Hz, cx / cy) | highest strong below (margin to 95) | lowest strong above (margin to 324) | D-185 (a) |
|---|---|---|---|---|---|
| cell nominal | kd | none | 86.8 (+10 %) | 654 (+102 %) | PASS |
| cell nominal | nom | none | 89.9 (+6 %) | 699 (+116 %) | PASS |
| cell nominal | hi | 100.2 (0.64 / 0.69) | 88.2 (+8 %) | 792 (+145 %) | **FAIL** |
| cell lower bound | kd | none | 82.4 (+15 %) | 632 (+95 %) | PASS |
| cell lower bound | nom | none | 85.3 (+12 %) | 668 (+106 %) | PASS |
| cell lower bound | hi | 96.6 (0.61 / 0.58) | 83.9 (+13 %) | 736 (+127 %) | **FAIL** |
Reading (T-084): with the cell credited the in-plane spar mode leaves the band (largest in-band coupling 0.21-0.27), but the symmetric wing-flap / cage-bounce mode (hub and pack bouncing on the bridge, arms flexing; 79-96 Hz) rises to the band's lower edge 95 Hz: in band at cell nominal hi 100.2 Hz, cell lower bound hi 96.6 Hz. With the pack placed at its drawn x (rigid on the hub) instead of at the hub node it moves up further (94-107 Hz, `T084_report.md` s2.4). No lever within the BOM moves it robustly below 95 Hz (bridge 12x10 fails D-206 torsion). D-185 (a) is therefore NOT shown to pass by the beam FE in either wing model; the rule is not relaxed: open, T-084 report s2 options (tap test T-A-TAP on the built structure).

Not re-run here (listed in T066_record.md): the control-band gain-margin clause of iter3_run.md (`sitl/fu_cage.py`) with the X2216 masses / inertias, and a tap test of the built cage.

Fin out-of-plane EI 81.2 N m2 (kd, 16x14 tube), mass/length 99 g/m (tube + 3 mm foam fairing + tape); rib EI (25x23) 592 N m2 (was 14x12: 61). D-202 arm crossing: arms modelled as four 12x10 beams meeting at one hub node (see limits in T066_record.md).

### Mount stiffness and strength (limit load at the cap, design = x1.5 x1.15 x1.25 on printed / bonded, x1.5 x1.15 on CF)
| Item | Value | Allowable | MS | Result |
|---|---|---|---|---|
| Arm 12x10 root bending, thrust 13.08 N at 0.246 m = 3.22 N m | 63 MPa | 350 | +4.53 | PASS (T-083 cup checks: 63.38 MPa, MS +4.52 with torque) |
| Arm, prop strike 30 N (EST) at lever 0.246 + 0.080 m = 9.8 N m (lever as t083_cup_checks.md: MS +0.82) | 192 MPa | 350 | +0.82 | PASS |
| Bridge 16x14 in prop strike, 4.7 N m | 49 MPa | 350 | +6.21 | PASS |
| Bridge 16x14, max control pitch moment 3.77 N m | 39 MPa | 350 | +7.96 | PASS |
| Bridge, pack + hub + tray + doublers at 12 g crash (355 g x 12 g x 0.1295 m = 5.4 N m, A-P5), struts ignored | 56 MPa | 350 | +5.24 | PASS |
| Arm tip stiffness 7.4 N/mm: thrust deflection | 1.77 mm (T-083: 2.0 mm) | - | - | info |
| Hub pitch rotation under the max control moment: M L / EI (bridge 16x14, 93.2 N m2, bridge alone, no struts) | 0.3 deg | - | - | info; soft-mount note of the iteration-1 row is superseded: the pitch mode is in the FE table above |
| Bridge buckling under the thrust sum at the cap 4 x 13.08 x cos 17 deg = 50 N (cantilever-pin K=2, L 0.1295 m, x KF) | P_cr 13711 N | | +157.9 | PASS |
| Motor screws / X-mount / cup rows | carried from `mechanism/out/T083_data/t083_cup_checks.md` (X2216 on the X-mount, 4 x M3): min MS +0.46 (plate strip at the nut, -y bolts), all PASS | | +0.46 | PASS (carried, s6) |

## 5. C5 landing on fin-tip feet (rigid-body dynamics + hand calculation)
Static (drawn pads, CG 24.66 mm aft of LE from cad_mass.json, ground plane x 0.3375): tip-over narrow axis **31.4 deg: PASS vs A-P9 30 deg** (T-084: fin tube ends at FIN_H 0.1937 m, option T3 of the T-068 decision s4; was 29.2 deg at FIN_H 0.180. Pad centre, CG z ignored, as T-066; the D-215 A-P9 pivot, the outer pad edge on the CG z side, gives 31.32 deg here and >= 31.00 deg over both trim ends, drawn and tallied CG: `mechanism/out/T084_data/tipover_t084.txt`), wide axis 50.5 deg. Parked broadside to the wind: tips at 7.6 m/s; restoring / overturning at 5 m/s 2.33. I (kg m2, CAD part-table model scaled to 1.912 kg): [0.105, 0.0405, 0.1182].
Demand basis (T-083, reused): pad plateau 36 N, usable stroke 24 mm, pad x 0.3475 m, z 0.1905 m (analysis pad of D-222 s4.1, not the drawn pad), mass 1.912 kg, CG from cad_mass.json (24.66 mm), CAD part-table mass model rebuilt from the current CAD (`T066_data/cad_part_table_T066.json`, 131 parts, basic 1.6330 kg), friction mu 0.40 / 0.30, pad zeta 0.02 / 0.05 / 0.10 (EST, TP-3 measures it), dt 0.2 ms.
Sim = `landing_a.py` (6 dof, 4 elasto-plastic feet, Coulomb friction, rotor lift 2/3 W to 0.3 s then 0 at 0.6 s), 21 cases x 3 zeta x 2 mu = 126 runs. Rib-root check: the 25x23 CF rib (OD 25 / ID 22 mm, root x 70.5 mm) under bending, torsion and axial load, all four feet resolved in the body frame at every step, RF = 1 / sqrt((KF (M/Z + N/A) / 350 MPa)^2 + (KF T r / J / 30 MPa)^2), KF 1.725, both allowables EST (no coupon); the RB value is then divided by the DAF 2.23 (D-223 wing / rib; x1.5 floor stays).

Table at pad zeta 0.05, mu 0.40 (the iteration-1 basis):
| Case | max stroke (mm) of 24 | permanent set (mm) | peak foot load (N) | side load (N) | n at CG | end tilt (deg) | drift (mm) | rib-root RF, rigid-body | rib-root RF x2.23 |
|---|---|---|---|---|---|---|---|---|---|
| hard level | 8.9 | 7.4 | 48 | 15 | 10.3 | 0.1 | 12 | 8.97 | 4.02 |
| hard 10 narrow | 15.4 | 13.9 | 48 | 19 | 5.2 | 1.9 | 118 | 20.94 | 9.39 |
| hard 10 narrow neg | 15.1 | 13.6 | 48 | 19 | 6.2 | 1.8 | 113 | 37.23 | 16.70 |
| hard 10 wide | 9.5 | 8.0 | 51 | 21 | 5.4 | 0.1 | 60 | 5.46 | 2.45 |
| hard 7/7 combo | 13.2 | 11.7 | 54 | 21 | 6.7 | 1.2 | 16 | 5.30 | 2.38 |
| hard 10 narrow + drift .5 | 18.2 | 16.7 | 49 | 19 | 5.2 | 2.5 | 74 | 15.03 | 6.74 |
| hard 10 wide + drift .5 y | 12.2 | 10.7 | 54 | 21 | 5.6 | 0.4 | 131 | 7.84 | 3.52 |
| normal level .5 | 2.4 | 0.9 | 40 | 12 | 8.5 | 0.0 | 7 | 9.23 | 4.14 |
| normal 10 narrow .5 | 3.6 | 2.1 | 41 | 15 | 6.9 | 0.2 | 98 | 13.36 | 5.99 |
| normal 10 wide .5 + drift | 7.1 | 5.6 | 48 | 19 | 5.0 | 0.4 | 115 | 6.95 | 3.12 |
| SITL Tb_h5 wide (y drift) | 6.6 | 5.1 | 48 | 19 | 4.8 | 0.3 | 89 | 3.74 | 1.68 |
| SITL Tb_h5 narrow (z drift) | 5.5 | 4.0 | 44 | 18 | 6.1 | 0.3 | 114 | 8.27 | 3.71 |
| SITL Ta_h5 wide (y drift) | 7.6 | 6.1 | 48 | 19 | 4.8 | 0.4 | 105 | 5.61 | 2.51 |
| SITL Ta_h5 narrow (z drift) | 5.5 | 4.0 | 43 | 17 | 4.6 | 0.5 | 119 | 9.25 | 4.15 |
| SITL Z5_b45 wide (y drift) | 7.2 | 5.7 | 48 | 19 | 4.9 | 0.4 | 112 | 4.35 | 1.95 |
| SITL Z5_b45 narrow (z drift) | 6.5 | 5.0 | 44 | 17 | 6.4 | 0.6 | 120 | 9.25 | 4.15 |
| SITL Lb_5e wide (y drift) | 8.1 | 6.6 | 48 | 17 | 7.2 | 0.5 | 97 | 13.65 | 6.12 |
| SITL Lb_5e narrow (z drift) | 7.1 | 5.6 | 44 | 18 | 5.7 | 0.7 | 103 | 8.43 | 3.78 |
| SITL Z5_gb45 wide (y drift) | 6.4 | 4.9 | 47 | 19 | 5.0 | 0.4 | 105 | 9.69 | 4.34 |
| SITL Z5_gb45 narrow (z drift) | 7.1 | 5.6 | 45 | 18 | 5.5 | 0.7 | 91 | 8.99 | 4.03 |
| hard 16 wide + drift .5 y | 12.3 | 10.8 | 53 | 21 | 5.6 | 0.3 | 178 | 6.61 | 2.96 |

Envelope over all 21 cases, by pad zeta and friction:
| zeta | mu | worst stroke (mm) of 24 | worst end tilt (deg, limit 3.0) | peak n (g, A-P5 limit 12) | peak foot load (N) | worst side load (N) | min rib-root RF (RB) | min rib-root RF x2.23 | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 0.02 | 0.4 | 20.8 | 2.88 | 8.7 | 43 | 17 | 4.00 | 1.79 | PASS |
| 0.02 | 0.3 | 17.4 | 2.34 | 8.7 | 45 | 13 | 6.04 | 2.71 | PASS |
| 0.05 | 0.4 | 18.2 | 2.51 | 10.3 | 54 | 21 | 3.74 | 1.68 | PASS |
| 0.05 | 0.3 | 15.3 | 2.04 | 10.3 | 57 | 17 | 4.71 | 2.11 | PASS |
| 0.1 | 0.4 | 15.2 | 2.03 | 12.7 | 70 | 28 | 3.70 | 1.66 | FAIL: n > 12 g (A-P5) |
| 0.1 | 0.3 | 12.8 | 1.68 | 12.7 | 78 | 23 | 4.90 | 2.20 | FAIL: n > 12 g (A-P5) |

Rib-root RF at x2.23 (this file, rib 25x23 hand row) vs T-083 R1 / R2 rows: T-083 min 1.16 at zeta 0.05 and 1.06 over all zeta (rib at the node exit x 176 and at the root-fitting mouth); T-083b sensitivity at 1.873 kg: 1.12-1.13. This row is the rib at x 70.5 mm with feet resolved about the rib root, a different station, so the numbers are compared, not equated. Pad life: normal landings set the permanent set shown above; replace the pad at 10 mm cumulative set (EST carried from iteration 1; the pad is specified by its dynamic force, D-222).
Side load per foot: worst 28.1 N at mu 0.40 / 0.30 (pad friction is an assumption, not measured: drag-test the EVA/PE pad, TP-3). Limits: pad plateau, stroke, zeta and friction are specification values pending the bench drop test; the drawn pad is not the analysis pad (T083_report.md s5.2).

## 6. C6 joints, fasteners, bonds: CARRIED FORWARD from the records that replaced the iteration-1 hand rows (not recomputed here)
The iteration-1 rows of this section judged the PETG hub, PETG saddles, PETG root block, 0.1 mm CFRP fin skins, M3 motor screws and the PETG pack-tray flange. None of those parts exists in the current CAD (CGE-001 is a machined 6061 hub, D-220 / D-221; the D-226 centre node CGE-006 and bulkheads replace the saddles; FIN-003 is a 6061 fitting, D-229; the fin is a 16x14 tube + foam fairing; the motors sit on the SunnySky X-mount, T-083; the tray CGE-008 is a 1.2 mm windowed plate, T-077). Re-running the old formulas on parts that are not drawn would give no information, so each row is replaced by the judging record's value (all at KF 1.725 / KP 2.156, x2.23 on the T-083 demand unless stated; EST allowables except where marked V):
| Joint / part | Judging record | Min RF or MS (pad zeta 0.02 / 0.05 / 0.10 unless one value) | Basis | Verdict |
|---|---|---|---|---|
| FIN-003 6061 root fitting (ring, plug, plate, bonds Q1-Q8) | T083b_report.md s3 | RF 1.21 (zeta <= 0.05), 1.40 (0.02), 0.89 (0.10) | T-083 demand, x2.23, 6061 yield 240 MPa | PASS zeta <= 0.05; **FAIL at 0.10 (0.89)**; integrity-class peel rows 0.15-0.16 (outside the RF minimum, T-069 F-3, TP-4) |
| Whole D-226 cell, rib, bridge, strut, R4 clamp at the new 1.873 kg / CG 22.26 mm | T083b_report.md s4.3 | min 1.09 (R4 junction, zeta 0.05); zeta 0.10 min 0.66 (C3) | sensitivity re-run of the T-083 demand | PASS zeta <= 0.05; **FAIL at 0.10** |
| Centre node CGE-006 + bulkheads WNG-013 (C1-C7) | T083_report.md s5.3 / strength_table_t083.md (1.913 kg) | RF 1.16 (0.02) / 1.18 (0.05) / **0.66 (0.10, C3 flange bond)** | x2.23 | PASS zeta <= 0.05; FAIL at 0.10 |
| Fin node FIN-005 / FIN-009 / straps (N1-N6) | same | RF 1.24 / **1.11** / 0.83 (N3, N4a) | x2.23 | PASS zeta <= 0.05; FAIL at 0.10 |
| Rib FIN-002 25x23 (R1, R2) | same | RF 1.14 / 1.16 / 1.06 | x2.23, tau 30 MPa EST | PASS all zeta |
| Skin WNG-011 + WNG-014 (3 plies) K1-K3 | same | RF 1.32 / 1.16 / 0.76 (K1), 0.87 (K2) | x2.23, S 70 MPa lower bound EST | PASS zeta <= 0.05; FAIL at 0.10 |
| Wing section P15 / P16 | same | RF 1.39 / 1.23 / 0.80 (P15 foam shear) | x2.23 | PASS zeta <= 0.05; FAIL at 0.10 |
| Bridge CGE-004 16x14 (B1 bending at the socket mouth) | same | RF 1.39 / 1.21 / 0.93 | x2.23 | PASS zeta <= 0.05; FAIL at 0.10 |
| Strut CGE-005 8x6 + R4 clamp CGE-007 | same + strut_clamp_t083.md; T083b s4.3 | RF 1.40 / 1.13 (1.09 at 1.873 kg) / 0.87-0.90 | x2.23 | PASS zeta <= 0.05; FAIL at 0.10 |
| Motor mount + cup rows (X-mount, M3, plate strip, cup-to-arm bond) | T083_report.md s4, t083_cup_checks.md | MS +0.46 (plate strip at the nut) | limit x KF / KP, strike 30 N EST, cap 13.08 N | PASS |
| Arm tubes, arm bond, hub sockets and sleeves (landing, DAF 1.97) | T083_report.md s5; hub FEA (fea_hub.py runs d209 / d210) | see those records; G1 arm-tube B axial RF 0.94 passes only if measured pad zeta < about 0.088 (D-223) | DAF 1.97 on the arm tubes | see the record |

Summary of the carried landing rows: every class-RF row passes at pad zeta <= 0.05 (min 1.09); at zeta 0.10 nine row groups fail (min 0.66) and A-P5 12 g is exceeded (12.7 g). The pad zeta is an EST until the TP-3 drop test; this is a test gap, not a design change made here.