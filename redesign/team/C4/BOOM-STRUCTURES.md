# Fin and motor-tube structures — K09-L

Owner C4 (fin / motor-tube structures). Revision **C4-R2**, 2026-11-09: re-run on D3's as-designed fin (CR-D3-10),
params A1-R2, `subsystems/fins/params.json` (D3 R2), C1 loads and B4 rpm of 2026-11-09. Analysis `MODELLED`; every
input that is not a catalogue value is `UNVERIFIED` until the tests at the end have run.

Re-run (about 40 s): `python -I redesign/team/C4/fin_structures_d3.py`, then `python -I redesign/proofs/build_graph.py`
(no C4 errors; other roles' drift still fails the build). Every number below is in `claims.d3.json` (`CL-C4-D3-…`)
or `out/results_d3.json`. R1 (`fin_structures.py`, `claims.json`) is kept only because D3's `CALC-D3-BRACE` reads it;
its claims no longer verify requirements.

## Verdict

| Question | Answer | Claim | Status |
|---|---|---|---|
| Does D3's fin as drawn (one board layer) meet `R-VIBRATION`? | **No.** First station mode 228 Hz (lower quarter), 14 % from 2P cruise (200 Hz) | `CL-C4-D3-SEP-1L` 0.14 | `FAIL` |
| Why did R1's 296 Hz drop? | The tube now stops 18 mm below the motor axis and the fin top 30 mm below it (CR-D3-01), and the cambered wing leaves 14 mm more free tube below than above. The governing mode is motor twist about the tube plus fore-aft nodding; the one-layer board stores 45–70 % of its strain energy, the brace 2–3 % | `out/results_d3.json#configs` | `MODELLED` |
| What fixes it? | **Keep two board layers** (as `params.json` `fins.layers` = 2 already says), with the brace and the edge strips. All three are needed: drop the brace → 0.01, drop the strips → 0.02 | `CL-C4-D3-SEP` | `UNVERIFIED` |
| Separation, recommended design | **0.41** nominal (281 Hz lower, 289 Hz upper); **0.33** at the worst tube E/G corner; **0.40** with prop gyroscopics | `CL-C4-D3-SEP`, `-WORST`, `-WHIRL` | `UNVERIFIED` |
| B4's whole-band rule (80–330 Hz) | Not met (−0.15); needs every station mode ≥ 396 Hz. `R-VIBRATION` on the operating points is the criterion; rpm notch is the backup (CR-C4-06/07) | `CL-C4-D3-SEP-BAND` | `FAIL` |
| Strength, every part | Positive; tightest is the brace anchor on the spar, **+0.33** with a 0.5 peel knock-down | `CL-C4-D3-MS-*` | `UNVERIFIED` |
| Through-core block | **+0.55** (tube-bore shear-out), bosses not credited for strength | `CL-C4-D3-BLOCK-MS` | `UNVERIFIED` |
| Mass | Second layer +37.5 g: fins **402 g** vs 370 g allocated (−9 %). A 10 × 2 brace instead of 10 × 3 saves about 10 g `EST` | `CL-C4-D3-FINS-MASS` | `FAIL` |

## Forcing and criterion

| Point | rpm | 1P Hz | 2P Hz | Source |
|---|---|---|---|---|
| Hover, 2.6 kg | 5 396 | 89.9 | 179.9 | `CL-B4-HOVER-RPM` |
| Cruise, 16 m/s | 6 000 | 100.0 | 200.0 | `CL-B4-CRUISE-RPM` |
| F4 cap | 9 319 | 155.3 | 310.6 (transient, not counted) | `CL-B4-RPM-MAX` |

`R-VIBRATION`: every station mode ≥ `P:requirements.vibration_sep_frac` 0.20 from each point above. A station mode
has ≥ 10 % of its kinetic energy in the motor + prop + mount body.

## Model (`fin_fe.build_q`, one quarter, upper UR and lower LR)

| Item | Value | Source | Status |
|---|---|---|---|
| Tube | CF 22 × 20, frame elements, clamp at the bore ends z +30.4 / −16.6 mm, root spring 10 000 N·m/rad (swept 3 000–rigid) | `ASM-C4-BORE-Z`, `ASM-C4-ROOT-K` | `UNVERIFIED` |
| Tube E, G | 100 GPa (70–135), 5 GPa (3–10) | `ASM-J1-E-TUBE`, `ASM-C4-G-TUBE` | `UNVERIFIED` |
| Tube end / motor axis | z 0.172 / 0.190 m | `fin_detail.tube_length_m`, params | `PROPOSED` |
| Mount | spring tube end → motor body: rocking 3 000, twist 30 000 N·m/rad | `ASM-C4-MOUNT-K-ROCK`, `-TWIST` | `UNVERIFIED` |
| Motor body | motor 81 g (face x 0.0309), prop + adapter 22 g (x −0.0082), mount 11.3 g at its CAD CG | `CL-D3-X-FACE`, `CL-D3-X-PROP`, `ASM-C4-MOUNT-CAD` | `PROPOSED` |
| Half-fin | mapped Q4 Mindlin shell between the S5010 skin and a straight top edge (collar top 0.1595 m → TE tip 0.19 m); lower root free over the link slot | `ASM-C4-SKIN-PTS`, `fin_detail` | `PROPOSED` |
| Board | 1 or 2 layers × 4.8 mm, faces 0.10 mm paper E 4 GPa, core E 10 / G 4 MPa | `ASM-C4-FACE-*`, `-CORE-*` | `UNVERIFIED` |
| Edge strips | CF 10 × 1, both faces, top edge, collar to foot | `fin_detail.edge_strip` | `PROPOSED` |
| Brace | CF 10 × 3, ear (0, −17.8, 0) mm at the collar z 0.1535, anchor (0.080, ±0.242, skin + 4 mm); L 0.145 / 0.157 m; anchor + spar 3e7 N/m in series | `fin_detail.brace`, `ASM-C4-ANCHOR-K` | `PROPOSED` |

| Check | Result | Limit | Claim | Status |
|---|---|---|---|---|
| Quad shell = R1 rectangle element on a rectangle | 1e-15 | ≤ 1e-9 | `CL-C4-D3-Q4-RECT` | `CHECKED` |
| Skewed 16 × 16 mesh cantilever plate vs Leissa | 69.7 vs 69.1 Hz, 0.9 % | ≤ 2 % | `CL-C4-D3-Q4-SKEW` | `CHECKED` |
| Mesh 12 × 10 / 24 × 20 (used) / 36 × 30 | f1 lower 281.1 / 281.1 / 280.9 Hz; change 0.24 % | ≤ 3 % | `CL-C4-D3-MESH-CONV` | `CHECKED` |
| R1 checks (tube vs Blevins 0.03 %, plate vs Leissa 0.7 %) | unchanged | — | `CL-C4-FE-CHECK-*` | `CHECKED` |

## Modes (nominal E, G; first three station modes, Hz; separation = nearest operating point)

| Configuration | Upper | Lower | Separation | Source |
|---|---|---|---|---|
| D3 as designed, 1 layer | 237, 304, 504 | 228, 296, 485 | **0.14** `FAIL` | `CL-C4-D3-SEP-1L` |
| **Recommended: 2 layers + brace + strips** | **289**, 360, 378 | **281**, 356, 373 | **0.41** | `CL-C4-D3-SEP` |
| same, brace 10 × 2 | 287, 358, 373 | 279, 352, 369 | 0.39 | `results_d3.json` |
| 2 layers, no brace | 158, 317, 522 | 143, 310, 517 | 0.01 `FAIL` | same |
| 2 layers, no edge strips | 196, 228, 283 | 190, 224, 274 | 0.02 `FAIL` | same |
| 2 layers, mount 1 000 N·m/rad | 259 | 255 | 0.27 | same |
| 2 layers, root 3 000 N·m/rad | 278 | 272 | 0.36 | same |
| 2 layers, half height 0.21 m (CR-B3-14) | 283 | 276 | 0.38 | same |
| 1 layer, rigid mount **and** rigid root | 257 | 248 | 0.24 (not credible: both springs rigid) | same |

Panel mode (TE tip with the foot) 70.7 Hz, below the band, < 10 % energy at the motor (`CL-C4-D3-PANEL`).
Mount rocking stiffness needed for 0.20: **894 N·m/rad** (low E/G corner; 778 nominal), estimate 3 000
(`CL-C4-D3-MOUNT-K-REQ`, margin +70 %). At 500 N·m/rad the separation collapses to 0.07.

![Campbell diagram](fig-c4-02-campbell-d3.svg)

`FIG FIN-C4-02 — Station whirl frequency vs rpm, against 1P and 2P ± 20 %; dashed: D3 as designed (1 layer).`
The recommended curves stay above 2P cruise at every steady point; gyroscopic split is under 3 %.

## Strength (recommended design; ultimate = 1.5 × C1 limit; joints × 1.15 × 1.25)

Cases per quarter: L1 level foot 38.2 N; L4 foot 32.9 N + μ 0.5 across the fin (both senses); L5 the same along;
G2 51 N lateral at the tube end (both senses); H2 thrust 21.1 N + 0.42 N·m. Foot load over 30 mm.

| Item | Ultimate | Allowable | MS | Governing | Claim |
|---|---|---|---|---|---|
| Fin face (paper), 2 layers | 5.0 MPa | 10 MPa | +0.99 | L4 | `CL-C4-D3-MS-FACE` |
| Edge strips 10 × 1 | 49 MPa | 400 MPa | +7.2 | L4 | `CL-C4-D3-MS-EDGE` |
| Tube at the bore end | 15.9 MPa | 400 MPa | +24 | G2 | `CL-C4-D3-MS-TUBE` |
| Brace buckling, 10 × 3 (10 × 2) | 166 N design (G2; limit 89 / 96 N upper / lower) | P_cr 989 N (293 N) | +4.9 (+0.76) | G2 | `CL-C4-D3-MS-BRACE` |
| Brace-end bond, 10 mm engagement | 0.80 MPa | 2 MPa | +1.50 | G2 | `CL-C4-D3-MS-BRACE-END` |
| Station-collar bond on the tube (3.5 N·m limit torque + brace shear) | 1.07 MPa | 2 MPa | +0.87 | L4 / G2 | `CL-C4-D3-MS-COLLAR` |
| Collar ear root, interlayer bending | — | 15 MPa | +2.96 | G2 | `CL-C4-D3-MS-EAR` |
| **Anchor bond on the spar (pull-off)** | 0.75 MPa | 1 MPa (2 × 0.5 peel) | **+0.33** | G2 | `CL-C4-D3-MS-ANCHOR` |
| Foot deflection, L4 limit | 5.2 mm | — | — | L4 | `CL-C4-D3-FOOT-DEFL` |

## Through-core block (`FIN-004-R/L`, D3 geometry)

Bore credited for strength = core depth at the tube, 27.7 mm (S5010). The 8 mm bosses add root fixity, not strength
(2.4 mm C-rings, open at the board slot).

| Check | Stress | Allowable | MS | Claim |
|---|---|---|---|---|
| Design moment 23.1 N·m (= 10.7 × 1.5 × 1.15 × 1.25 > C1 20.3); force 121 N | — | — | — | `CALC-C4-D3-BLOCK` |
| Tube-bore wall shear-out (7 mm walls) | 6.4 MPa | 10 MPa | **+0.55** | `CL-C4-D3-BLOCK-MS` |
| Tube-bore bearing | 8.4 MPa | 20 MPa | +1.38 | same |
| Spar-bore bearing | 5.0 MPa | 20 MPa | +2.99 | same |
| Bond on the spar, torsion | — | 2 MPa | +3.9 | same |
| Couple on the spar / on the tube (design) | 961 N / 1 249 N | — | — | `CL-C4-D3-SPAR-COUPLE` |

## Sizing sheet for D3

| Feature | Size | Basis | Status |
|---|---|---|---|
| Board | **2 layers** (9.6 mm), laminated with spray adhesive, all four half-fins | `CL-C4-D3-SEP` 0.41 vs 0.14 with 1 | `PROPOSED` |
| Edge strips | CF 10 × 1, both faces, on the top edge from inside the collar to the foot (no free band above) | no strips → 0.02 | `PROPOSED` |
| Brace | CF 10 × 3 as drawn, or 10 × 2 (−10 g `EST`, P_cr 293 N, separation 0.39); ear and anchor as drawn | `CL-C4-D3-MS-BRACE` | `PROPOSED` |
| Brace ends | ≥ 10 mm bonded in each slot | +1.50 | `PROPOSED` |
| Station collar | 12 mm tall, ≥ 1.6 mm ring, bonded on the scuffed tube; layers in x-y | +0.87 | `PROPOSED` |
| Anchor | 20 × 16 mm saddle bonded on the spar top; do not shrink | +0.33 (tightest) | `PROPOSED` |
| Mount | rocking stiffness ≥ **900 N·m/rad** about x and y: keep the 12 mm grip, 2 mm wall, lip cap | `CL-C4-D3-MOUNT-K-REQ` | `UNVERIFIED` |
| Tube | 22 × 20 × 0.344 m accepted (CR-D3-01), CF 20 × 18 plug over the 47 mm bore | modes above | `PROPOSED` |
| Block | 69 × 36 mm, full core depth, 7 mm walls each side of the tube bore | +0.55 | `PROPOSED` |

## Open issues

| # | Issue | Owner | Status |
|---|---|---|---|
| 1 | Fins 402 g vs 370 g allocated: allocation or reserve decision | A1, A3 | open (CR-C4-15) |
| 2 | Tube E, G, board faces, mount and root stiffness, prop inertia are assumptions | I1, H1 | `UNVERIFIED` |
| 3 | Band rule (80–330 Hz) not met; `R-VIBRATION` is met | A2, B4, F4 | open (CR-C4-06/07) |
| 4 | Wing modes with four 125 g stations, and the spar under the anchor, are C2's | C2 | open (CR-C4-18) |
| 5 | Anchor margin rests on a 0.5 peel factor; joint stacks for collar, ear, anchor | C6 | open (CR-C4-10) |

## How to verify (planned tests in `claims.d3.json` / `claims.json`)

| Test | What | Verifies |
|---|---|---|
| `T-C4-TUBE-BEND`, `-TORSION` | E, G of the bought tube (I1 by 10 Dec, CR-I1-08) | `CL-C4-D3-SEP-WORST` |
| `T-C4-MOUNT-STIFF` | mount rocking stiffness ≥ 900 N·m/rad | `CL-C4-D3-MOUNT-K-REQ` |
| `T-C4-TAP-D3` | tap each motor bell of the finished wing, FFT vs 1P/2P | every frequency claim |
| `T-C4-BOARD-COUPON` | face allowable, D, areal mass (1 and 2 layers) | `CL-C4-D3-MS-FACE` |
| `T-C4-FIN-PROOF` | 1.5 × L4 at the foot, 1.5 × G2 at the tube end, both senses | face, strips, brace, collar, anchor |
| `T-C4-BLOCK-PROOF` | 30 N·m on a block in a core offcut, 1 min | `CL-C4-D3-BLOCK-MS` |
| `T-C4-PROP-SWING` | prop polar inertia | `CL-C4-D3-SEP-WHIRL` |
