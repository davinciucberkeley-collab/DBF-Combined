# Fin and motor-tube structures — K09-L

Owner C4. Revision **C4-R4**, 2026-11-10. Geometry: D3-R4 fin (`subsystems/fins/params.json`): two board layers,
CF 10 × 2 brace, 12 mm station collar with a 40 mm strip tail, Ø 2 mm strip pins at 15 mm, D5 square tip (step at
|z| 0.2005 m from x 0.2746 m, strips end at the step front). Loads: C1 and B4 claims as of 2026-11-10. Analysis
`MODELLED`; every input that is not a catalogue value is `UNVERIFIED` until the tests at the end have run.

Re-run (about 2 min): `python -I redesign/team/C4/fin_structures_d3.py`, `python -I redesign/team/C4/fin_structures.py`,
then `python -I redesign/proofs/build_graph.py`. Numbers: `claims.d3.json` (`CL-C4-D3-…`), `out/results_d3.json`.
`fin_structures.py` (R1 concept model, `claims.json`) stays only for the shared assumptions, sources and tube tests
that C2, C3, C6 and H1 read; none of its claims verifies a requirement.

## S1 simulation round (2026-11-10) — read first

3-D solid FE of the as-designed quarters (`SIMULATION-REPORT.md`, `claims.sim.json`) supersedes two R4 answers below:
the drawn-shoe face is **MS +0.11** in 3-D (R4 shell −0.54; CR-C4-30 held until `T-C4-FIN-PROOF` on an as-drawn
article, CR-C4-36), and the separation is **0.29** (3-D, today's cruise rpm 5 946 and A3 masses). The R4 tables stay as
the sizing record; `fin_structures_d3.py` was re-run today (separation 0.35, mount need 1 030 N·m/rad, fins 434.8 g).

## What R4 changed

| Item | R3 | R4 | Claim |
|---|---|---|---|
| Corner foot load × μ 0.7 (CR-C1-21) | 29.1 N × 0.7 = 20.4 N | **32.6 N × 0.7 = 22.8 N** | `CL-C4-D3-SIDE-LOAD` |
| Foot load path | 30 mm patch at the tip | D5 shoe on the square tip, rigid, load at the C1 ground point (x 0.368, z 0.218 m) | `ASM-C4-SHOE-Z0` |
| B4 swirl (CR-B4-19), misbuilt 1.43 N scaled to T_lim | — | 4.73 N per half-fin at the B4 cp, both senses, with H2c | `CL-C4-D3-SWIRL-F` |
| G3 set-down, lower can (CR-C1-24) | — | 23.2 N toward the wing | `CL-C4-D3-BRACE-G3`, `-MS-CAP-G3` |
| Station collar | 16 mm | **12 mm** (16 mm kept as a check) | `CL-C4-D3-MS-COLLAR`, `-MS-COLLAR-16` |
| Face criterion | envelope at ultimate | intact at ultimate; LE fillet cracked = fail-safe at limit | `CL-C4-D3-MS-FACE` |
| Section-torque check vs C1 (CR-C1-21) | — | FE 7.37 N·m = C1 7.37 N·m (0.08 %) | `CL-C4-D3-SEC-T-VS-C1` |
| NaN / singular matrix (CR-C6-20) | build stopped | fixed ARPACK start vector + guard; 0 C4 calculation errors | build log |
| Part ids (CR-A4-47) | `FIN-001-LU/LD/RU/RD` | `FIN-001-UR/UL/LR/LL` (both scripts) | — |
| `T-C4-FIN-PROOF` (CR-H1-17) | flight quarter, in both claim files | test article, `claims.d3.json` only | — |

## Verdict

| Question | Answer | Claim | Status |
|---|---|---|---|
| `R-VIBRATION` (2 layers, 10 × 2 brace, strips) | **Met.** 275 Hz upper / 268 Hz lower; **0.37** from 2P cruise (196.5 Hz) | `CL-C4-D3-SEP` | `UNVERIFIED` |
| Worst tube E/G corner; with prop gyroscopics | 0.29; 0.36 | `-SEP-WORST`, `-SEP-WHIRL` | `UNVERIFIED` |
| Fin face, D5 shoe as drawn (cheeks to \|z\| 0.196 m) | **Fails: MS −0.54** (21.8 MPa ult vs 10 MPa) below the cheek edge on the square tip, L4 | `CL-C4-D3-MS-FACE` | `FAIL` |
| Fin face, cheeks extended to \|z\| 0.171 m (CR-C4-30) | intact **+0.18** (ult); LE fillet cracked **+0.01** (limit, see below) | `-MS-FACE-SHOE-INTACT`, `-MS-FACE-SHOE-FS` | `PROPOSED` |
| Other strength items | all positive; tightest collar +0.16, anchor +0.35 | `CL-C4-D3-MS-*` | `UNVERIFIED` |
| Edge strip on bare paper | fails without pins (MS −0.79); pins carry **72 N** each | `-MS-STRIP-PAPER`, `-STRIP-PIN-F` | pins `PROPOSED` |
| Collar torque for C6 | **6.24 N·m limit** (fillet cracked; 6.12 intact) + brace 95 N limit | `CL-C4-D3-COLLAR-T` | `UNVERIFIED` |
| Brace section (CR-B1-18) | keep 10 × 2 and **fair with tape** (1.4 g for four); sanding the edges round cuts I by 8 % | `-BRACE-ROUND-I`, `-BRACE-TAPE-MASS` | `PROPOSED` |
| Mass | fins **436.4 g** vs 418 g allocated (−18.4 g) | `CL-C4-D3-FINS-MASS` | `FAIL` (A1) |

## Why the tip fails, and the fix

The strips now stop at the step front (x 0.2746 m). Between there and the TE the 45 mm square tip is bare board. The
side load (22.8 N) acts at the pad, 17.5 mm above the step, and enters the board through the shoe cheeks. The board
carries it as plate bending just below the cheek edge: about 10 N·m/m, face stress 14.5 MPa limit. That moment is the
same on every mesh (9–11 N·m/m); the peak element rises from 15 to 24 MPa ult as the mesh refines (stiffness step at
the cheek edge). The overload is real, not a mesh artefact.

| Cheek lower edge \|z\|, m (36 × 30 mesh) | 0.196 (drawn) | 0.186 | 0.181 | 0.176 | **0.171** | 0.166 |
|---|---|---|---|---|---|---|
| Face MS intact, ultimate | −0.50 | −0.29 | −0.24 | +0.04 | **+0.18** | +0.18 |
| Face MS LE fillet cracked, limit | −0.25 | 0.00 | 0.00 | +0.01 | **+0.01** | +0.02 |

Extending the cheeks 25 mm toward the wing makes the shoe overlap the strip ends over the full strip band, so the
foot load enters the strips. From 0.171 m down the tip no longer governs; the peak moves to the LE root. The cracked
case (+0.01) peaks at the end of the bonded LE band (x 0.060, z 0.033 / 0.149 m), a corner that does not converge
with mesh (7.9 / 9.9 MPa limit at 24 × 20 / 36 × 30). The test-article quarter is built with the fillet unbonded, so
`T-C4-FIN-PROOF` decides it.

## Forcing and criterion

| Point | rpm | 1P Hz | 2P Hz | Source |
|---|---|---|---|---|
| Hover | 5 416 | 90.3 | 180.5 | `CL-B4-HOVER-RPM` |
| Cruise, 16 m/s | 5 894 | 98.2 | 196.5 | `CL-B4-CRUISE-RPM` |
| F4 cap | 9 319 | 155.3 | 310.6 (transient, not counted) | `CL-B4-RPM-MAX` |

`R-VIBRATION`: every station mode ≥ `P:requirements.vibration_sep_frac` 0.20 from each point above. The B4 band rule
(80–330 Hz, −0.19) is not met by intent (D-45: operating points + tap test, rpm notch as backup).

## Modes (nominal E, G; first three station modes, Hz)

| Configuration | Upper | Lower | Separation | Source |
|---|---|---|---|---|
| **As drawn: 2 layers, 10 × 2 brace, strips** | **275**, 319, 373 | **268**, 315, 366 | **0.37** | `CL-C4-D3-SEP` |
| same, 10 × 3 brace | 278 | 271 | 0.38 | `CL-C4-D3-BRACE-10X3-SEP` |
| same, LE fillet cracked | 260 | 252 | 0.28 | `out/results_d3.json` |
| same, mount 1 000 N·m/rad | 251 | 247 | 0.26 | same |
| same, root 3 000 N·m/rad | 266 | 260 | 0.32 | same |
| 2 layers, no brace | 154 | 140 | 0.01 `FAIL` | same |
| 2 layers, no edge strips | 205 | 195 | 0.01 `FAIL` | same |
| 1 layer (rejected) | 219 | 214 | 0.09 `FAIL` | `CL-C4-D3-SEP-1L` |

Panel mode 76.5 Hz (< 10 % energy at the motor). Mount rocking stiffness needed for 0.20: **971 N·m/rad**
(`CL-C4-D3-MOUNT-K-REQ`; estimate 3 000); the bench pass level stays **≥ 1 000 N·m/rad**. Whirl at cruise rpm, both
cant senses: 267 Hz (`CL-C4-D3-F-WHIRL-CRUISE`).

![Campbell diagram](fig-c4-02-campbell-d3.svg)

`FIG FIN-C4-02 — Station whirl frequency vs rpm with the 7° spin axis, against 1P and 2P ± 20 %; dashed: one layer (rejected).`

## Strength (ultimate = 1.5 × C1 limit; joints × 1.15 × 1.25; both quarters, LE fillet intact and cracked)

Limit cases per quarter: L1 level foot (`CL-C1-FOOT-MAX`); L4 corner 32.6 N + side 22.8 N, both senses; L5 the same
along; G2 51 N lateral at the tube end, both senses; H2c thrust along the 7° shaft + motor torque (4 sign
combinations); H2s = H2c + swirl 4.73 N, both senses; G3 23.2 N on the lower can toward the wing.

| Item | Ultimate / design | Allowable | MS | Governing | Claim |
|---|---|---|---|---|---|
| Fin face, shoe as drawn | 21.8 MPa | 10 MPa | **−0.54** | L4 | `CL-C4-D3-MS-FACE` |
| Fin face, cheeks to 0.171 m: intact ult / cracked limit | 8.5 / 9.9 MPa | 10 MPa | +0.18 / +0.01 | L4 | `-MS-FACE-SHOE-INTACT`, `-MS-FACE-SHOE-FS` |
| Edge strips 10 × 1 | — | 400 MPa | +3.63 | L4 | `CL-C4-D3-MS-EDGE` |
| Tube at the bore end | — | 400 MPa | +14.7 | L4 | `CL-C4-D3-MS-TUBE` |
| Brace buckling, 10 × 2 | 163 N | P_cr 293 N | +0.79 | G2 | `CL-C4-D3-MS-BRACE` |
| Brace, edges sanded round (rejected) | 163 N | 269 N | +0.65 | G2 | `-BRACE-ROUND-MS` |
| Brace-end bond, 10 mm | — | 2 MPa | +1.35 | G2 | `-MS-BRACE-END` |
| Station-collar bond, 12 mm (16 mm) | 13.4 N·m + brace shear | 2 MPa | **+0.16** (+0.55); needs 10.3 mm | L4 | `-MS-COLLAR`, `-COLLAR-H-REQ` |
| Collar ear root | — | 15 MPa | +3.03 | G2 | `-MS-EAR` |
| Anchor on the spar (0.5 peel) | — | 1 MPa | +0.35 | G2 | `-MS-ANCHOR` |
| Edge strip on paper, no pins | 0.48 MPa | 0.10 MPa | **−0.79** | L4 | `-MS-STRIP-PAPER` |
| Mount slip clamp with the cant | use 0.66 | 1 | +0.52 | H2c | `-MS-MOUNT-SLIP` |
| Lip cap bearing, G3 | 0.76 MPa | 30 MPa | +38.6 | G3 | `-MS-CAP-G3` |
| Through-core block | 6.4 MPa | 10 MPa | +0.55 | C1 | `CL-C4-D3-BLOCK-MS` |
| Foot deflection, L4 limit | 9.3 mm | — | — | L4 | `CL-C4-D3-FOOT-DEFL` |

Swirl and G3 never govern: swirl face stress 2.6 MPa ult, brace 17.9 N limit, collar torque 0.55 N·m; G3 brace
0.61 N, mount rocking 1.45 N·m design.

### Loads published for C6, C1 and D3

| Quantity | Value | Claim |
|---|---|---|
| Collar torque into the tube, limit (envelope; intact) | **6.24 N·m** (6.12) | `CL-C4-D3-COLLAR-T`, `-COLLAR-T-INTACT` |
| Brace force, design | 163 N | `CL-C4-D3-BRACE-F` |
| Strip shear flow per face, limit | 2 240 N/m | `CL-C4-D3-STRIP-Q` |
| Strip force per face into the collar tail, design | 1 243 N | `CL-C4-D3-STRIP-END-F` |
| Pin shear, Ø 2 mm at 15 mm, design | 72.4 N | `CL-C4-D3-STRIP-PIN-F` |
| Wing-plane half-fin torsion, L4 limit; difference to C1 | 7.37 N·m; 0.08 % | `-SEC-T-L4`, `-SEC-T-VS-C1` |
| Spar couple at each block, design | 961 N | `CL-C4-D3-SPAR-COUPLE` |

## Sizing sheet for D3 / D5 (R4)

| Feature | Size | Basis | Status |
|---|---|---|---|
| Board | 2 layers (9.6 mm), laminated | sep 0.37 vs 0.09 with one | `PROPOSED` |
| Edge strips | CF 10 × 1 both faces, collar to step front, Ø 2 mm CF pins ≤ 15 mm pitch | MS −0.79 bare; 72 N/pin | `PROPOSED` |
| Strip tail in the collar | 40 mm, both faces | 1 243 N/face design | `PROPOSED` |
| **D5 shoe cheeks** | **lower edge at \|z\| ≤ 0.171 m** (25 mm deeper), x 0.2666–0.320, bonded to both faces | face MS −0.54 → +0.18 | `PROPOSED` (CR-C4-30) |
| Brace | CF 10 × 2 flat, wrapped in packing tape as a fairing; edges not sanded | MS +0.79, sep 0.37 | `PROPOSED` |
| Station collar | 12 mm (needs 10.3 mm) | MS +0.16 | `PROPOSED` |
| LE fillet | keep; credited only in the intact case | fail-safe +0.01 at limit | `PROPOSED` |
| Mount | rocking ≥ 1 000 N·m/rad; slip 2.5 N·m | needs 971 | `UNVERIFIED` |

## Open issues

| # | Issue | Owner | Status |
|---|---|---|---|
| 1 | Square tip fails with the cheeks as drawn | D5 (CR-C4-30) | open |
| 2 | Fins 436.4 g vs 418 g | A1, A3 (CR-C4-34) | open |
| 3 | Fail-safe face +0.01 rests on a non-converging corner | H1 (`T-C4-FIN-PROOF`) | open |
| 4 | Tube E/G, faces, paper bond, mount and root stiffness, prop inertia are assumptions | I1, H1, C6 | `UNVERIFIED` |
| 5 | G3 force is an assumption until C1 publishes it | C1 (CR-C4-29) | open |
| 6 | C2 still reads `CL-C4-SPAR-COUPLE` (R1) | C2 (CR-C4-26) | open |

## How to verify

| Test | What | Verifies |
|---|---|---|
| `T-C4-FIN-PROOF` | **test article** lower quarter (never flown), cheeks to 0.171 m, LE fillet unbonded: 1.5 × L4 49 N + 34 N both senses, G2 77 N both senses, G3 35 N, 30 s each, then L4 to failure | face, strips, pins, brace, collar, anchor, cap |
| `T-C4-MOUNT-STIFF` | mount rocking ≥ 1 000 N·m/rad both directions | `CL-C4-D3-MOUNT-K-REQ` |
| `T-C4-TAP-D3` | tap each bell of the finished wing, FFT vs 1P/2P | every frequency claim |
| `T-C4-TUBE-BEND`, `-TORSION` | E, G of the bought tube | `CL-C4-D3-SEP-WORST` |
| `T-C6-BOARD-LAP`, `T-C6-STRIP-ANCHOR` | paper allowable; strip tail pull-out | `-MS-STRIP-PAPER`, `-STRIP-END-F` |
| `T-C4-BLOCK-PROOF` | 30 N·m on a block in a core offcut | `CL-C4-D3-BLOCK-MS` |
