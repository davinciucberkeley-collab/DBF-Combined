# Wing structure — K09-L

Owner: C2 (wing structures). Revision C2-R1, 2026-11-09, at params A1-R2 and C1-R2 loads. Status: calculations
`CHECKED` (convergence, two independent methods, hand checks, proof chain with no C2 drift); every material value is
`UNVERIFIED` until the coupons, the tube bend test and the wing proof test run.
Re-run (about 25 s): `python -I redesign/team/C2/wing_struct.py` → `python -I redesign/team/C2/c2_claims.py` →
`python -I redesign/proofs/build_graph.py`.

**Verdict.** The 22 × 20 mm spar, the one-piece XPS core and one layer of tape carry every C1 case with margin. All
bending margins are ≥ +0.8 and tip deflection is 10 % of the allowed value. Three things need action:
1. **Plugs inside the spar** at the through-core blocks and at the brace anchors. Without them the 1 mm wall cracks
   as a ring.
2. **The wing is soft in torsion.** The first two wing modes (12–27 Hz) are the fin stations rocking about the spar.
   They sit in the hover pitch and yaw control path.
3. **Wing modes fall inside the 80–330 Hz rotor band** (`R-VIBRATION` FAIL). No reasonable spar fixes this, so the
   tap test and the F4 harmonic notch close it.

## 1. What the structure is

| Item | Definition | Part | Status |
|---|---|---|---|
| Spar | CF tube 22 × 20 × 1 000 mm, unspliced, \|y\| ≤ 0.50 m, x 0.080, z +0.0066 m; foam cover 5.0 mm upper / 4.3 mm lower | `WNG-002` | `PROPOSED` |
| Core | one-piece XPS F-250, S5010, c 0.32 m; **no ribs**: the core is the rib, the PETG blocks are the hard points at \|y\| 0.32 m | `WNG-001` | `PROPOSED` |
| Skin | packing tape, 1 layer each side, spanwise strips, 10 % overlap, 15 mm round the LE | `WNG-003` | `PROPOSED` |
| Spar plugs | PETG Ø 19.8 × 36 mm at \|y\| 0.32 m (block) and Ø 19.8 × 20 mm at \|y\| 0.242 m (brace anchor), bonded inside the tube | `WNG-002` (new sub-items) | `PROPOSED` |
| Wing joint | **none**: one-piece wing, one-piece transport (P6). The attachments are the 2 through-core blocks, 4 brace anchors, the pod bond and 2 cradle contacts | — | — |

Load path: air load on the skin and foam → spar through the slot bond (98 % of flap bending, 44 % of in-plane
bending, 71–81 % of torsion goes to the spar by stiffness) → across the centreline. Fin-group loads come in through the
block bore and the brace saddles straight onto the spar (C4 load path). Root, centreline and pod carry no joint.

## 2. Basis

| Input | Value | Unit | Source | Status |
|---|---|---|---|---|
| Loads | C1-R2 cut loads on the spar axis, 33 cases × 2 mass configurations, every 5 mm | — | `team/C1/data/wing_spanwise.csv` | `UNVERIFIED` (C1) |
| Factor of safety / fitting / printed-bonded | 1.5 / 1.15 / 1.25 | — | `P:requirements.safety_factor_ult`, C1 | `PROPOSED` |
| Spar E (nominal / low corner used for every stiffness claim) | 100 / 70 | GPa | `ASM-J1-E-TUBE`, `ASM-C4-E-TUBE-LO` | `UNVERIFIED` (T-C4-TUBE-BEND) |
| Spar G (nominal / low) | 5 / 3 | GPa | `ASM-C4-G-TUBE`, `-LO` | `UNVERIFIED` |
| Spar allowables: bending / shear / hoop | 350 / 30 / 40 | MPa | `ASM-C2-SPAR-SIGMA`, `-TAU`, `-HOOP` | `UNVERIFIED` |
| XPS: E, G / allowable compression, tension, shear | 10, 4 / 0.12, 0.15, 0.10 | MPa | `ASM-C2-XPS` | `UNVERIFIED` (T-C2-XPS-COUPON) |
| Tape: E, t, allowable; stiffness effectiveness | 2 GPa, 44 µm, 60 MPa; 50 % | — | `ASM-C2-TAPE`, `-TAPE-EFF` | `UNVERIFIED` |
| PETG bearing allowable | 20 | MPa | `ASM-C4-PETG-BEARING` (C4) | `UNVERIFIED` |
| Rotor forcing: hover 1P / 2P, cruise 1P / 2P | 89.9 / 179.9, 100 / 200 | Hz | `CL-B4-HOVER-RPM`, `CL-B4-CRUISE-RPM` | `UNVERIFIED` |

All inputs sit in `params.json#c2.inputs` (one place); the claims read them from there.

## 3. Section properties (S5010, structural box LE → hinge x 0.2496 m)

| Property | Low corner (E 70, G 3) | Nominal (E 100, G 5) | Unit | Spar share (nominal) |
|---|---|---|---|---|
| EI flap | 262 | 372 | N·m² | 98 % |
| EI in-plane (chordwise) | 723 | 833 | N·m² | 44 % |
| GJ (foam 4.6 + tape cell 4.2 + spar) | 30.7 | 45.2 | N·m² | 71–81 % |
| Shear centre x / modulus-weighted x | 0.0800 / 0.0807 | 0.0800 / 0.0805 | m | spar at 0.080 (25 % c) |
| Mass per metre (core, tape, spar, fill) | 0.333 | 0.333 | kg/m | section CG x 0.114 m |
| Outboard of the spar end (\|y\| > 0.50): EI flap, GJ | 7.0, 8.8 | — | N·m² | — |

## 4. Strength (ultimate = 1.5 × limit; MS = allowable / stress − 1)

| Check | Stress | Allowable | MS | Claim | Status |
|---|---|---|---|---|---|
| Spar root bending, spar alone, envelope (L1, 20.4 N·m) | 61.5 MPa | 350 MPa | +4.7 | `CL-C2-SPAR-SIGMA-ULT`, `-ENV` | `UNVERIFIED` (allowable) |
| Spar shear: all torsion (6.9 N·m) + shear (42.7 N) on the spar | 11.8 MPa | 30 MPa | +1.5 | `CL-C2-SPAR-TAU-ULT` | `UNVERIFIED` |
| Spar local buckling vs bending stress | 2 000 vs 61.5 MPa | — | +31 | `CL-C2-SPAR-BUCKLE` | `CHECKED` |
| Spar between anchor and block, brace couple added | 66.2 MPa | 350 MPa | +4.3 | `CL-C2-SPAR-SIGMA-BRACE` | `UNVERIFIED` |
| Spar wall ring bending at the block bore, **no plug** (961 N design couple, C4) | 911 MPa | 40 MPa | **−0.96** | `CL-C2-RING-NO-PLUG` | `FAIL` → plug |
| Spar wall under the brace saddle, **no plug** (146 N design, 16 mm saddle) | 77.8 MPa | 40 MPa | **−0.49** | `CL-C2-RING-ANCHOR` | `FAIL` → plug |
| Plug bearing with the plug fitted (block, design) | 5.3 MPa | 20 MPa | +2.7 | `CL-C2-PLUG-BEARING` | `UNVERIFIED` |
| Slot bond / foam shear, air load into the spar (186 N/m) | 8.1 kPa | 100 kPa | +11 | `CL-C2-SPAR-BOND-TAU` | `UNVERIFIED` |
| Tape at the root, in-plane + flap, full tape stiffness | 7.5 MPa | 60 MPa | +7.0 | `CL-C2-ROOT-TAPE` | `UNVERIFIED` |
| Chordwise bending of the core aft of the spar, CN 1 at q_VD 454 Pa: tape faces | 13.0 MPa | 60 MPa | +3.6 | `CL-C2-CHORD-TAPE` | `UNVERIFIED` |
| Same with the tape lost (bare foam) | 109 kPa | 150 kPa | +0.37 | `CL-C2-CHORD-FOAM` | `UNVERIFIED` |
| Foam outboard of the spar end (y 0.50–0.575), flight/landing | 4.9 kPa | 150 kPa | +29 | `CL-C2-TIP-FOAM` | `UNVERIFIED` |
| Pod bond shear in the wing foam (175 N design over 0.2 × 0.1 m) | 8.7 kPa | 100 kPa | +10 | `CL-C2-POD-FOAM` | `UNVERIFIED` |
| Transport cradle: pad area for the X3 drop (86 N limit per cradle × 1.5) | ≥ 1 080 mm² | — | — | `CL-C2-CRADLE-AREA` | `PROPOSED` (D7: 40 × 40 mm) |
| Damage case L6 wingtip strike (86 N at the TE tip) | tape 157 MPa at y 0.50 | 60 MPa | fails | `out/results.json#tip_foam` | the tip is the fuse: re-cut 75 mm, re-tape |

The spar is sized by **stiffness, torsion and robustness, not strength**. Spar trade at the same loads
(`out/results.json#spar_trade`):

| Tube | Spar mass | σ ult | Tip w, G2 | First mode (torsion) | Verdict |
|---|---|---|---|---|---|
| 16 × 14 | 73 g | 122 MPa | 7.6 mm | 8.6 Hz | strong enough, −29 g, torsion mode −26 %, own stock |
| 20 × 18 | 93 g | 75 MPa | 3.9 mm | 10.6 Hz | −10 g |
| **22 × 20** | **102 g** | **62 MPa** | **2.9 mm** | **11.7 Hz** | **kept**: same stock as the motor tubes (one order), the block bores are drawn for it |
| 25 × 23 | 117 g | 47 MPa | 1.9 mm | 13.6 Hz | +15 g, cover 3.1 mm |

## 5. Deflection and twist (limit, low corner E 70 / G 3, tape 50 %)

| Quantity | Value | Limit | Case | Claim | Status |
|---|---|---|---|---|---|
| Tip deflection / semi-span, all envelope cases | 0.0050 (2.9 mm) | 0.05 | G2 hang by a motor | `CL-C2-TIP-DEFL-FRAC` | `UNVERIFIED` |
| Tip deflection, flight cases | 1.08 mm | — | F1 pull-up at VD | `params.json#c2.fe.w_tip_flight_m` | `UNVERIFIED` |
| In-plane deflection, max | 1.48 mm | — | L1 landing | `c2.fe.u_max_env_m` | `UNVERIFIED` |
| Twist, flight (nose-down at the tip under full elevon) | 2.77° | — | F7 rolling pull-up at VD | `CL-C2-TWIST-FLIGHT` | `UNVERIFIED` (T-C2-TWIST) |
| Elevon roll effectiveness at VD, flexible / rigid | 0.78 | — | strip theory, root held | `CL-C2-ROLL-EFF-VD` | `UNVERIFIED` |
| Roll reversal (spar-only GJ bound) | 53.3 m/s | ≥ 1.2 VD = 32.7 | — | `CL-C2-V-REVERSAL` | `UNVERIFIED` |
| Divergence (spar-only GJ, shear centre 20 mm aft) | 91.1 m/s | ≥ 32.7 | (at the computed shear centre: none below 3 000 m/s) | `CL-C2-V-DIVERGENCE` | `UNVERIFIED` |
| Flutter screen, modal p-k, 6 modes, Theodorsen strips | no unstable root to 81.6 m/s (3 VD) | ≥ 32.7 | every mode damps more with speed | `CL-C2-V-FLUTTER` | `UNVERIFIED` (tap test) |

![Deflection envelope](fig/C2-01-deflection-envelope.svg)

`FIG C2-01 — Limit-load envelope along the half-span: flap w, in-plane u, twist (all sizing cases, both sides, low corner).`

## 6. Modes (free-free, all 2.6 kg on board, motor stations rigid)

| Mode (nominal / low corner) | Hz | Motor/mount energy | Nearest rotor order, separation | Meaning |
|---|---|---|---|---|
| Antisymmetric torsion: fin stations rock in opposite senses | 14.2 / 11.7 | 65 % | — | `CL-C2-F-TORSION-ANTI`; in the hover yaw path |
| Symmetric torsion: both stations pitch against the pod | 26.2 / 21.7 | 35 % | — | `CL-C2-F-TORSION-SYM`; in the hover pitch path (upper/lower differential twists the wing) |
| Symmetric flap | 40.2 / 33.7 | 44 % | — | — |
| Symmetric in-plane | 62.6 / 57.6 | 16 % | hover 1P, 0.30 | — |
| **Antisymmetric flap** | **82.3** / 69.0 | 61 % | hover 1P, **0.085** | `FAIL` at nominal stiffness; 0.23 at the low corner |
| In-plane antisym / flap sym | 146.7 / 154.0 | 25 / 31 % | hover 2P, 0.18 / 0.14 | `FAIL` |
| In-plane sym | 215.3 | 12 % | cruise 2P, **0.077** | `CL-C2-WING-MODE-SEP` = 0.077 vs ≥ 0.20: `FAIL` |

Over the 12 stiffness corners (E 70/100 GPa × G 3/5 GPa × tape 0/50/100 %) some station mode always sits within 2 %
of a rotor order. A ±20 % window round four forcing lines leaves little room between 70 and 240 Hz, and the spar E is
uncertain by ±20 %. Re-sizing the spar cannot clear the band reliably (trade table above). The route is the one
`R-VIBRATION` already allows: measure (T-C2-TAP-TEST), then let F4 notch the measured peaks. CR-C2-04.

![Wing modes](fig/C2-02-wing-modes.svg)

`FIG C2-02 — Wing modes below 400 Hz at nominal stiffness against the ±20 % windows round hover and cruise 1P and 2P; orange = station mode inside a window.`

## 7. Method and checks

| Step | Method | Check | Result | Status |
|---|---|---|---|---|
| Hand calcs | spar σ = M r / I, τ = T r / J + 2V/A, Roark buckling, ring | proof chain re-runs them from C1's claims | 0 drift | `CHECKED` |
| Beam integration (every case, both sides) | curvature M/EI + shear V/GA, twist rate T/GJ, integrated from the centreline on C1's cut loads | step 20 / 10 / 5 mm: 0.693 / 0.707 / 0.714 mm; left = right on F1 | 1.1 % last step | `CHECKED` |
| Hand check on F1 tip deflection | uniform-load cantilever from C1's root moment, w = M₀ L² / 4EI | 0.79 mm hand vs 0.71 mm model: −10 %, because the fin-station inertia at y 0.32 relieves the outer moment | as expected | `CHECKED` |
| NumPy 3-D Timoshenko frame FE | 6 dof/node, Timoshenko in-plane (L/c = 1.8 there), lumped rigid items at their true offsets; 6 / 12 / 24 / 48 / 96 elements per half | static F1 w: 0.695 → 0.713 mm, change 0.05 %; first 4 modes change 0.02 % (48 → 96) | `CL-C2-FE-CONV-STATIC`, `-FREQ` | `CHECKED` |
| FE vs beam integration | independent: FE loaded by strip forces from C1's cut-load differences | F1 w 0.22 %, L1 u 0.01 %, F7 twist 0.18 % | `CL-C2-FE-VS-BEAM` | `CHECKED` |
| Ring model | thin ring, cosine bearing over ±30°, reacted by beam shear flow; Castigliano redundants | vs Roark two-point ring P R/π: 0.37 % | `CL-C2-RING-VALIDATION` | `CHECKED` |
| Aeroelastic statics | strip theory on the FE (no downwash: conservative) at 12 / 24 / 48 elements | q_rev 2 003 / 2 018 / 2 012 Pa | 0.3 % | `CHECKED` |
| Flutter screen | modal p-k, Theodorsen C(k), 6 cantilever modes, 12 and 24 elements | no crossing either mesh | — | `CHECKED` |

**Why a beam model and not gmsh + SU2 ELASTICITY.** The wing is a prismatic foam section on one dominant tube, so beam
theory with composite section properties captures the deflection, twist and modes the design depends on. Two
independent beam methods agree within 0.25 %. The stresses that matter are in the spar, where beam theory is exact;
foam and tape stresses are below 25 % of their allowables. The one region where a solid model would add information
is the through-core block on the spar. That geometry is still being designed by D3/C4 (SIM-TOOLS: no detailed FEA on
unsettled geometry), and the ring model plus the plug removes the risk there.

Not modelled: elevon control-surface flutter (elevons are servo-held; keep free play < 1°, D6); station flexibility
(C4 station modes ≥ 296 Hz sit above the wing modes in the table); the pod's stiffening of the centre section
(conservative); higher modes above ~200 Hz are beam-theory estimates, so trust the tap test there.

## 8. Tests (planned)

| Test | What | Closes |
|---|---|---|
| `T-C2-WING-PROOF` | wing on padded V-blocks under the spar at \|y\| 0.32; F1-equivalent sand bags; then G2: 51 N on one upper tube end; no crack, set < 0.5 mm | strength, deflection |
| `T-C2-TAP-TEST` | aircraft on bungees, phone accelerometer at the pod and a fin tip, tap motors and fin tips, FFT to 400 Hz | modes, notch frequencies, flutter model |
| `T-C2-TWIST` | pod clamped, 2.9 N·m on a lever at one block, inclinometer at the block and the tip; pass GJ ≥ 25 N·m² | twist, reversal, divergence |
| `T-C2-XPS-COUPON` | density block; bare and taped 300 × 40 × 30 mm strips in 3-point bending to failure | all foam and tape allowables |
| `T-C4-TUBE-BEND` (C4) | spar E | every stiffness claim: re-run at the measured E |

## 9. Open issues

| # | Issue | Owner |
|---|---|---|
| 1 | Wing modes inside the rotor band (`CL-C2-WING-MODE-SEP` FAIL): tap test + harmonic notch (CR-C2-04) | F4, A2, H1 |
| 2 | Wing torsion modes 12–27 Hz sit in the hover pitch/yaw control path (CR-C2-03) | B3, F4 |
| 3 | All material values unverified; re-run after T-C4-TUBE-BEND and T-C2-XPS-COUPON | H1, G2 |
| 4 | C1 loads rest on B2's c 0.30 strip loads (C1 open issue 1); C2 re-runs when C1 does | C1 |
| 5 | Brace anchor y: D3 uses 0.242 m, C4 modelled 0.20 m; the plug goes where D3 puts the saddle | D3, C4 |
