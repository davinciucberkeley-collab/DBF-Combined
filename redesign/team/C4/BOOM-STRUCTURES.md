# Fin and motor-tube structures — K09-L

Owner C4 (fin / motor-tube structures). Status `PROPOSED` design change, analysis `MODELLED`, every input
`UNVERIFIED` until the tests at the end have run. Revision C4-R1, 2026-11-09, against params A1-R2 and C1 loads of
2026-11-09 09:39. Re-run in about 5 s: `python -I redesign/team/C4/fin_structures.py`, then
`python -I redesign/proofs/build_graph.py`. That build reports no C4 errors; other roles' drift still fails it.
Every number below is in `claims.json` (`CL-C4-…`) or `out/results.json`.

## Verdict

| Question (A1 action item) | Answer | Claim | Status |
|---|---|---|---|
| Does the bonded fin, acting as a shear web, move the tube modes out of the forcing? | **No.** It lifts the fore-aft mode (x, in the fin plane) from 180 to 329 Hz. The first mode is the **lateral-torsion** mode (tube bends out of the fin plane and twists, because the motor and prop sit 24–50 mm ahead of the tube axis). It stays at **149 Hz**, 4 % from 1P at the F4 rpm cap | `CL-C4-F-LT-2L`, `CL-C4-SEP-2L` | `FAIL` |
| What fixes it? | One **10 × 2 mm CF strip brace** per motor station, from a collar under the mount to the spar line 0.12 m inboard, plus **10 × 1 mm CF edge strips** on both faces of the fin top edge, from the same collar to the foot. First station mode **296 Hz** with 1 layer, **392 Hz** with 2 layers | `CL-C4-F1-1LB`, `CL-C4-F-LT-REC` | `PROPOSED` |
| ≥ 20 % from 1P/2P at hover, cruise and 1P at the F4 cap (`R-VIBRATION`)? | **Yes** with the brace and edge strips: 0.48 (1 layer) / 0.96 (2 layers). Over the whole tube E 70–135 GPa × G 3–10 GPa range: 0.43 / 0.90. With prop gyroscopics: 0.96 | `CL-C4-SEP-1LB`, `-1LB-WORST`, `-REC-WHIRL` | `UNVERIFIED` |
| ≥ 20 % outside the whole 80–330 Hz band (B4's rule)? | **No.** 1 layer: first mode inside the band (−0.10). 2 layers: 392 Hz, 1 % short of the 396 Hz the rule needs (+0.19). No 22 mm tube design reaches it without the brace | `CL-C4-SEP-BAND-1LB`, `-REC` | `FAIL` |
| Tube modulus used | E = **100 GPa** (`ASM-J1-E-TUBE`), corners 70 / 135 GPa; G = **5 GPa** (`ASM-C4-G-TUBE`), corners 3 / 10 GPa. I1 buys the US-stock tube and runs the bend and torsion tests (CR-C4-03) | — | `UNVERIFIED` |
| Through-core block sized to the fin-joint moment? | **Yes.** Design moment 23.1 N·m = 10.7 N·m (A1 value; C1 now reports 9.4 N·m) × 1.5 × 1.15 × 1.25. Block 69 × 36 × 27 mm, minimum margin **+0.47** (tube-bore wall shear-out), 30 g each | `CL-C4-BLOCK-MS`, `CL-C4-BLOCK-MASS` | `UNVERIFIED` |
| Spar bearing (with C2) | Bearing on the spar 5.0 MPa, margin +2.0. The spar takes a **961 N** design couple across the 36 mm bore. The 1 mm wall needs an internal plug at each block (CR-C4-02) | `CL-C4-SPAR-COUPLE` | `UNVERIFIED` |
| One foam-board layer per half-fin (−42 g)? | **Passes only with the brace and edge strips:** separation 0.48 / 0.43 worst case, face margin +0.28 against a 10 MPa face allowable that is still a guess. Without them neither 1 nor 2 layers pass: foot side load L4 gives an ultimate face stress of 26 MPa (2 layers) / 58 MPa (1 layer) on the bare board | `CL-C4-MS-FACE-1L`, `CL-C4-SEP-1LB` | `UNVERIFIED` |
| Mass | Recommended (1 layer + braces + edge strips + heavier blocks): **+67 g** on the fins allocation (370 → 437 g). The 2-layer version adds 109 g | `CL-C4-FINS-DELTA-1L`, `-DELTA` | `UNVERIFIED` |

## Forcing and criterion

| Point | rpm | 1P Hz | 2P Hz | Source |
|---|---|---|---|---|
| Hover, 2.6 kg | 5 396 | 89.9 | 179.9 | `CL-B4-HOVER-RPM` |
| Cruise, 16 m/s | 6 000 | 100.0 | 200.0 | `CL-B4-CRUISE-RPM` |
| F4 output cap | 9 319 | 155.3 | 310.6 (transient, not a dwell point) | `CL-B4-RPM-MAX` |

Criterion: `R-VIBRATION` (A2), separation ≥ `P:requirements.vibration_sep_frac` 0.20 from each steady point. A
station mode is any mode with ≥ 10 % of its kinetic energy in the motor, prop and mount body. Fin-panel modes
(< 10 %) are reported but do not count. The 80–330 Hz band rule (CR-B4-07) is reported as a second, stricter claim.

## Model

| Item | Value | Source | Status |
|---|---|---|---|
| Method | FE quarter model, UR station; tube 3-D frame elements; half-fin flat shell (Q4 membrane + Mindlin plate, selective reduced integration); LE bond = rigid link to the tube; fin root pinned on the skin; motor + prop + mount as one rigid body at its true offsets; brace = axial element; edge strips = beam on the top fin row | `fin_fe.py` | `MODELLED` |
| Tube clamp | at the block face, z = ±13.5 mm (core 27 mm at x 0.045 m) | `ASM-C4-CORE-T-TUBE` | `UNVERIFIED` |
| Tube 22 × 20 mm, 0.102 kg/m | E 100 GPa, G 5 GPa | `ASM-J1-E-TUBE`, `ASM-C4-G-TUBE` | `UNVERIFIED` |
| Station masses | motor 81 g at −23.5 mm, prop + adapter 22 g at −50 mm (Ip 7.5e-5 kg·m², diametral Ip/2), mount 18 g at −5 mm (x from the tube axis) | params, `ASM-C4-PROP-IP` | `UNVERIFIED` |
| Fin masses | ESC 6.6 g on the fin, foot 10 g at the TE tip | params (A3 placement) | `PROPOSED` |
| Foam board, per layer | faces 0.10 mm paper, E 4 GPa; core E 10 MPa, G 4 MPa; 0.2 kg/m² | `ASM-C4-FACE-*`, `-CORE-*` | `UNVERIFIED` |
| Brace | 10 × 2 mm pultruded CF strip, E 110 GPa, from (−11, −11, −25) mm off the station to the spar line at y = 0.20 m; length 0.191 m | `ASM-C4-STRUT-*` | `PROPOSED` |
| Edge strips | 10 × 1 mm CF on both outer faces along the fin top edge, collar to foot | `ASM-C4-EDGE-*` | `PROPOSED` |
| Gyroscopics | spin inertia = prop + bell 9.0e-5 kg·m²; modal reduction on 16 modes | `CALC-C4-CAMPBELL` | `MODELLED` |

| Check | Result | Limit | Claim | Status |
|---|---|---|---|---|
| Bare tube + tip mass vs Blevins (and J1's formula) | 183.0 vs 183.0 Hz, error 0.03 % | ≤ 1 % | `CL-C4-FE-CHECK-TUBE` | `CHECKED` |
| Cantilever foam-board plate vs Leissa (stiff core) | 68.6 vs 69.1 Hz, 0.7 % | ≤ 2 % | `CL-C4-FE-CHECK-PLATE` | `CHECKED` |
| Mesh 6×5 / 12×10 (used) / 24×20, braced design | 392 / 392 / 392 Hz and 517 / 514 / 502 Hz; change 2.5 % | ≤ 3 % | `CL-C4-MESH-CONV` | `CHECKED` |

## Modes by configuration (E 100 GPa, G 5 GPa)

| Configuration | Station modes, Hz | First fin-panel mode, Hz | Separation (nearest) | Worst over E/G | Band rule | Claim |
|---|---|---|---|---|---|---|
| Bare tube | 144 (lateral-torsion), 180 (fore-aft) | — | 0.00 (2P hover) | — | −0.56 | `out/results.json` |
| 1 layer, no brace | 146, 274 | 21 | 0.06 (1P cap) | — | −0.56 | `CL-C4-SEP-1L` `FAIL` |
| 2 layers, no brace (current) | 149, 329 | 38 | 0.04 (1P cap) | 0.02 | −0.55 | `CL-C4-SEP-2L` `FAIL` |
| **1 layer + brace + edge strips (recommended)** | **296, 307** | 56 | **0.48** (2P cruise) | **0.43** | −0.10 | `CL-C4-SEP-1LB`, `-1LB-WORST` |
| 2 layers + brace + edge strips | 392, 514 | 68 | 0.96 (2P cruise) | 0.90 | +0.19 | `CL-C4-SEP-REC`, `-REC-WORST` |

![Campbell diagram](fig-c4-campbell.svg)

`FIG C4-01 — Station whirl frequencies vs rpm against 1P and 2P ± 20 %; dashed: current design.` The braced
modes sit above 2P at every steady point and hardly move with rpm: gyroscopic split is under 3 %.

What each part of the fix does (development runs, `out/results.json`):

| Change | Effect |
|---|---|
| Fin bonded to the tube | fore-aft mode 180 → 274 (1 layer) / 329 Hz (2 layers); lateral-torsion unchanged (+2 %) |
| Thicker tube 22 × 18, or a 25 × 23 sleeve | lateral-torsion 193 / 229 Hz: still within 20 % of 2P cruise; +50–80 g |
| Brace alone | lateral-torsion 248–288 Hz; fails at low E/G (0.06) |
| Edge strips placed 25–35 mm below the fin top edge | a 170–260 Hz panel mode that moves the motor (≥ 10 % energy) appears: **the strips must be the top edge** |
| Brace + edge strips on the top edge | above; both modes move out of 1P/2P for all E/G corners |

Root fixity (block + wing compliance, rotational springs at the clamp): first station mode with 1 layer 261 / 273 /
283 / 296 Hz at 2 000 / 5 000 / 10 000 N·m/rad / rigid. Separation stays ≥ 0.30 at 2 000 N·m/rad. A PETG bore only
27 mm long gives about 3 000 N·m/rad (foundation estimate), so D3 extends the tube bore with 8 mm bosses above and
below the skin (43 mm, about 4× stiffer) where the fin root fillet allows (CR-C4-04).

## Strength (ultimate = 1.5 × C1 limit; joints × 1.15 × 1.25)

Cases at the UR quarter: L1 level foot 38.2 N; L4 foot 32.9 N + 0.5 friction across the fin; L5 the same along the
fin; G2 2 × 2.6 kg × g = 51 N lateral at the tube end; H2 T_lim 21.1 N + 0.42 N·m. Foot load spread over 30 mm.

| Item, recommended 1-layer design | Ultimate | Allowable | MS | Governing | Claim | Status |
|---|---|---|---|---|---|---|
| Fin face (paper), max principal | 7.8 MPa | 10 MPa (`ASM-C4-FACE-SIGMA`) | +0.28 | L4 at the LE top | `CL-C4-MS-FACE-1L` | `UNVERIFIED` |
| Same, 2 layers | 3.7 MPa | 10 MPa | +1.68 | L4 | `CL-C4-MS-FACE-2L` | `UNVERIFIED` |
| Same, no edge strips (development run) | 26 MPa (2 layers) / 58 MPa (1 layer) | 10 MPa | −0.62 / −0.83 | L4 | — | `FAIL` |
| Edge strips 10 × 1 CF | 94 MPa | 400 MPa | +3.3 | L4 | `CL-C4-MS-EDGE` | `UNVERIFIED` |
| Motor tube at the block face | 42 MPa | 400 MPa | +8.5 | L4 | `CL-C4-MS-TUBE` | `UNVERIFIED` |
| Brace buckling (pinned, weak axis), design load incl. 1.15 | 142 N compression (G2) | P_cr 199 N | +0.40 (2 layers +0.36) | G2 | `CL-C4-MS-STRUT` | `UNVERIFIED` |
| Foot deflection, L4 limit | 8.9 mm (2 layers 5.2 mm) | — | — | L4 | `CL-C4-FOOT-DEFL-L4` | `UNVERIFIED` |

The worst face stress sits where the fin leaves the tube near the top edge: the foot side load makes the half-fin a
0.26 m cantilever off the tube. Without strips even 2 layers reach 2.6 × the face allowable. The edge strips carry it as flanges,
and the collar passes it into the tube as torsion (9.3 N·m limit at the block face in L4, covered above).

## Through-core block (`FIN-004-L/R`)

Geometry: printed PETG, 69 mm (x) × 36 mm (y, spar bore length) × 27 mm (z, core thickness). Vertical tube bore at
x 0.045 m and spanwise spar bore at x 0.080 m, 13 mm of web between them, 6–7 mm walls. Layers in the x-y plane,
4 perimeters, 40 % gyroid (fill 0.55). Load path: all fin-group loads go through the block into the spar. The root
bond to the skin and the brace are not counted.

| Check | Stress | Allowable | MS | Claim |
|---|---|---|---|---|
| Design moment, force | 23.1 N·m = max(C1 20.3, 10.7 × 1.5 × 1.15 × 1.25); 121 N | — | — | `CL-C4-BLOCK-M-DESIGN` |
| Tube bore bearing, 6M/(d h²) + F/(d h) | 8.8 MPa | 20 MPa | +1.26 | `CALC-C4-BLOCK` |
| Tube-bore wall shear-out, 7 mm walls | 6.8 MPa | 10 MPa | **+0.47** | `CL-C4-BLOCK-MS` |
| Spar bore bearing, 6M/(d W²) + F/(d W) | 5.0 MPa | 20 MPa | +3.0 | `CALC-C4-BLOCK` |
| Web bending / torsion (36 × 27 mm) | 5.3 / 4.2 MPa | 15 / 10 MPa | +1.84 / +1.39 | `CALC-C4-BLOCK` |
| Bond on the spar, torsion My 5.2 N·m limit | 0.41 MPa | 2 MPa | +3.9 | `CALC-C4-BLOCK` |
| Bond on the tube, axial | 0.07 MPa | 2 MPa | +30 | `CALC-C4-BLOCK` |
| Couple on the spar / on the motor tube (design) | 961 N / 1 282 N | — | — | `CL-C4-SPAR-COUPLE` |
| Mass each (EST, 0.55 fill) | 30 g vs 20 g allocated | — | — | `CL-C4-BLOCK-MASS` |

Both CF walls are 1 mm. Line loads near 1 kN at the bore ends risk crushing the ring, so **a 20 mm printed plug
goes inside each tube over the bore length**: motor tube 27 mm (43 mm with bosses), spar 36 mm, bonded
(CR-C4-02, CR-C4-04).

## Mass

| Item | Δ g | Basis | Claim |
|---|---|---|---|
| One board layer instead of two (4 half-fins) | −41.8 | 0.2 kg/m² × 0.275 × 0.38 m × 2 fins | `CALC-C4-MASS` |
| 4 braces (strip 5.9 g + two 4 g fittings) | +55.6 | `ASM-C4-STRUT-FIT-MASS` | `CALC-C4-MASS` |
| 8 edge strips 10 × 1 × 264 mm | +32.7 | CF 1 550 kg/m³ | `CALC-C4-MASS` |
| 2 blocks 30 g vs 20 g | +20.2 | `CL-C4-BLOCK-MASS` | `CALC-C4-MASS` |
| **Recommended total** | **+66.8** | fins 370 → 437 g | `CL-C4-FINS-DELTA-1L` |

## Open issues

| # | Issue | Owner | Status |
|---|---|---|---|
| 1 | Tube E and G, board face allowable and prop inertia are assumptions; the 1-layer face margin (+0.28) needs a face allowable ≥ 7.8 MPa | I1, H1 | `UNVERIFIED` |
| 2 | The band rule (80–330 Hz) is not met; R-VIBRATION is. Backup: rpm-tracking harmonic notch (F4) | A2, B4, F4 | open |
| 3 | Wing modes (spar flap and torsion with four 120 g stations) are not in this quarter model; C2 owns them | C2 | open |
| 4 | Brace adds about 0.07 N cruise drag with rounded edges, 0.24 N with square edges, about 1.5–5 % of the 4.6 N cruise drag | B1, B4 | open |
| 5 | +67 g on the fins against a 105 g gate margin | A1, A3 | open |
| 6 | Bond-line moment at the fin LE (modelled rigid) and the collar bonds need C6 joint stacks | C6 | open |

## How to verify (planned tests, `claims.json`)

| Test | What | Verifies |
|---|---|---|
| `T-C4-TUBE-BEND` | 3-point bend of the US-stock 22 × 20 tube, span 0.80 m, to 4 kg: E | separation worst-case claims |
| `T-C4-TUBE-TORSION` | 0.40 m tube, 0.30 m lever, laser on a wall: G | same |
| `T-C4-BOARD-COUPON` | 4-point bend of 50 × 300 mm foam-board strips, 1 and 2 layers: face allowable, D, areal mass | `CL-C4-MS-FACE-*` |
| `T-C4-TAP` | one finished quarter on a core offcut; tap the bell in x and y; FFT | every frequency claim |
| `T-C4-FIN-PROOF` | 1.5 × L4 at the foot, 1.5 × G2 at the tube end | face, edge, tube, brace, deflection |
| `T-C4-BLOCK-PROOF` | block on a spar stub in a core offcut, 30 N·m for 1 min | `CL-C4-BLOCK-MS` |
| `T-C4-PROP-SWING` | bifilar swing of one prop | `ASM-C4-PROP-IP` |
