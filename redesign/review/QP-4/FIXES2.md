# QP-4 fixes 2: elevon flutter by design, caps and mechanical stops, foam allowable (D6 / C2 / A5, concept A, 2026-11-15)

Labels: `CALC` computed here, `EST` estimate, `V` vendor / data sheet, `-` unknown. Edited only in `redesign/qp/A/` and this report. No git. Nothing bought, built or flown.
Reproduce (all `python -I`): `structures/fixes2_run.py` (about 6 min, 3 processes, writes `fixes2_run.md`), `structures/fixes2_cdamp.py` (`fixes2_cdamp.md`), `structures/foam_103.py` (`foam_103.md`), `cad/build_a.py`, `cad/collide_a.py` (env `A_ELEV_POSE=20|22` for the other poses), `cad/a_assembly.py`, `cad/stop_check.py` (`cad/out/STOP_CHECK.md`), `bom_a.py`, `sitl/cad_mass.py`, `mission_gate_a.py`.

## Verdict

| Item | Result |
|---|---|
| 1 Elevon flutter, K 0.01-20, 0 % damping, none below 28.8 m/s | **No passive balance, chord, hinge or elevon-mass option does it at a mass the aircraft can carry** (s1). It passes only with 73.5 g of lead per elevon (4.7 x the selected 15.6 g). **Solved with a hinge viscous damper**, drawn in the CAD: c = 1.03e-3 N m s/rad per elevon at 25 C (silicone fluid 12,500 cSt, coaxial shear drum on the hinge axis, 2.5 g per elevon). With it the selected D-187 v2 balance has **no instability anywhere on the K grid, all three wing corners, hot / nominal / cold**; lowest onset 35.5 m/s (kd, 50 C `EST`), 40.5 m/s (kd, 25 C) against 28.8. Because the damper sits across the hinge, **free play and K do not matter**. Preload strips remove the low-amplitude slack. Servo torque check passes at 7.2 V (1.56, s2). |
| 2 G10 caps and stops | **Done.** Four lens caps drawn (wall 0.6 mm, clearance to the lead and tabs **0.50 mm** over the whole travel), **mechanical stops at +-21 deg** (stop bosses on the caps, touching the balance tabs), collision **0 at the stop, at +-20 and at neutral; at +-22 only the stop bosses engage (0.25 mm = 1 deg at 14 mm)**; 25 -> 28 step assembly (s3). Finding: the caps weigh **12.4 g for four, not the 2 g** FIXES carried. |
| 3 Foam at 103 kPa | One check falls to MARGINAL at the board allowable (spar bond zone, +0.11); **fixed by design** (bond over |y| <= 0.20 m, +0.48). All other foam checks pass (s6). |
| Mass, cost | Basic **1,231.3 g** (+15.4 g); predicted **1,423.9 g** (<= 1,440 needs >= **27.2 g** of the 41.6 g `EST` cuts real, was 11.8 g). BOM **$1,775.09 total, +30 % margin +$105.08: G7 PASS** (s7). |
| Two findings outside the three items | (a) the CAD servo arm was 19 mm against a 12.9 mm horn radius, while the torque check assumed equal arms: **arm shortened to 12 mm**; (b) the elevon-core cove did not clear a +21 deg pose by 0.07 mm: cove re-cut for the stop. |

## 1. Elevon flutter robust to stiffness and free play

### 1.1 Method (so the sweep can be trusted)
`structures/flutter_a.py` is unchanged. `fixes2_run.py` re-solves its 3-DOF Theodorsen-Garrick section as a **p-method**: stability of the 8-state system (3 DOF + 2 Jones aerodynamic lag states, C(k) about 0.5 + 0.165 a1/(s+a1) + 0.335 a2/(s+a2)). No mode tracking, so the ">100" and "4 m/s" tracker artefacts of FIXES / BOARD are gone. The aero matrix is the repo's own `aero3` (identical to 1e-20 at omega 1); the Jones lag approximation is **1.7-2.4 %** off Theodorsen. Cross-check against the repo k-method, reference balance (nom): K 0.5 / 1.0 / 1.3 / 2.0 give 32.5 / 22.0 / 13.0 / 51.5 m/s, k-method 32.3 / 21.7 / 12.5 / 50.1.
Grid: K 0.01-20 N m/rad, **600 log points** (about 180 per decade), each at V = 2-60 m/s in 0.5 m/s steps, g_s = 0, wing corners **kd / nom / hi** (f_h 10.5 / 12.2 / 14.1 Hz, f_alpha 41.2 / 45.1 / 51.5 Hz from the Ritz run with the balance lump). "Unstable at V": an oscillatory root above 3 Hz with Re(s) > 0. "Worst damping ratio needed" is the largest Re(s)/|s| for V <= 28.8.
Limits, all `EST`: 2-D typical section at 0.7 span; elevon 9.6 g with its CG 0.35 chord aft of the hinge; the span-wise spread of the strip (y 0.232-0.338 of an elevon y 0.04-0.35) is smeared over the elevon; the damper sits at the elevon tip (y 0.35) but is modelled as spread over the span (the elevon is rigid in beta).

### 1.2 The undamped dip is a mass-coupled coalescence, not fixable by balance at a sensible mass
Selected D-187 v2 (15.6 g at 20 mm, ob 1.56) at 0 % damping: **unstable band K 0.70-1.54 (nom), 0.47-1.27 (kd), 1.14-1.99 (hi)**, worst damping ratio needed 0.8-1.0 % at 28.8 m/s. The band sits where the hinge mode crosses the wing torsion mode (f_beta about f_alpha). Switching the steady aero coupling terms off removes it, so the driver is the elevon's own pitching moment on the wing (the property that makes it a control surface), not the mass balance only.

| Design (g_s = 0, K 0.01-20) | Lead per elevon | Result, nom (kd / hi are in `fixes2_run.md`) |
|---|---|---|
| 0 D-187 v2 as drawn, ob 1.56 | 15.6 g | FAIL, 63 of 600 K points, band 0.70-1.54, lowest onset 2.5 m/s |
| 1 overbalance 2.5, 20 mm | 25.7 g | FAIL, band 1.56-2.37, onset 13.5 m/s |
| 2 overbalance 4, 14 mm | 58.8 g | FAIL (13 points), band 3.34-3.89, damping needed 1.2e-4, onset 21.5 m/s |
| **3 overbalance 5, 14 mm** | **73.5 g** | **PASS on all three corners** |
| 4 lighter elevon 6.0 g (-3.6 g), ob 2.5 | 12.9 g | FAIL, band 0.79-1.24, onset 22 m/s |
| 5 lighter elevon 4.5 g, ob 6, 14 mm | 41 g | FAIL, band 1.79-2.76 |
| 6 chord 0.20 c (hinge 0.80 c), ob 2.5 | 17.8 g | FAIL, band 0.98-1.34; also roll authority x about 0.79 (thin-airfoil flap effectiveness 0.48 vs 0.61): roll 92.9 -> about 73 deg/s, fails 90 |
| 7 chord 0.30 c (hinge 0.70 c), ob 2.5 | 35 g | FAIL, band 2.23-3.47 |

Rules of thumb from a wider scan (400-point K grid, scratch script, not in the repo; the table above is reproducible): the damping needed falls with lead mass and, at equal lead moment, with a shorter arm (more mass); a lighter elevon at the same overbalance ratio changes little; hinge position moves the band but never empties it. **Statement: no passive geometry passes below about 73 g of lead per elevon at 14 mm.** That is +58 g per elevon, +116 g for the pair, and a 14 mm reach, which pokes 1.0 mm more than the 20 mm reach. Rejected.

### 1.3 Chosen: hinge viscous damper, plus preload strips and a corrected linkage
**Damper required** (selected balance, per elevon, N m s/rad; minimum c with no instability below the stated speed, whole K grid):

| Lead per elevon | corner | c for <= 28.8 m/s | c for <= 37 m/s (1.54 VD, the QP-4 target) |
|---|---|---|---|
| 12.8 g | kd / nom / hi | 4.2e-4 / 3.6e-4 / 2.9e-4 | 9.0e-4 / 7.3e-4 / 5.8e-4 |
| **15.6 g (kept)** | kd / nom / hi | **3.3e-4** / 2.8e-4 / 2.2e-4 | **7.1e-4** / 5.8e-4 / 4.5e-4 |
| 20.0 g | kd / nom / hi | 2.4e-4 / 2.0e-4 / 1.5e-4 | 5.4e-4 / 4.4e-4 / 3.4e-4 |

**Design damper (drawn, `a_model.py` `DMP_*`, parts WNG-009 stator + WNG-010 rotor):** a coaxial shear drum **on the hinge axis**, in the 22 mm gap between the elevon tip (y 0.3495) and the fin: printed housing bore R 5.55 mm, rotor sleeve R 5.0 mm x 0.5 mm wall bonded by a flange to the elevon tip face, stator pin R 4.45 mm, gaps 0.30 mm each side, active length 16 mm, filled with **dimethicone 12,500 cSt, 0.974 g/mL, mu = 12.2 Pa s at 25 C** (Dow PMX-200 and Clearco PSF-12500 data sheets, read 2026-11-15 `V`). c = 2 pi mu L (R_i^3 / h_i + R_o^3 / h_o) = **1.03e-3 N m s/rad** `CALC` (edge and end effects ignored). Mass 2.0 g stator (incl. fluid and strips) + 0.5 g rotor = **2.5 g per elevon, 5.0 g for the pair**. The housing is bonded in a notch cut in the core at the tip and slides in from aft before the elevon (assembly step B4).

Result, selected D-187 v2, whole K grid, g_s = 0 (`fixes2_run.md` case 8, `fixes2_cdamp.md`):

| Damper state | c (N m s/rad) | kd | nom | hi |
|---|---|---|---|---|
| none | 0 | FAIL (80 K points, band 0.47-1.27) | FAIL (63, 0.70-1.54) | FAIL (45, 1.14-1.99) |
| c = 8e-4 (case 8) | 8.0e-4 | **PASS**, lowest onset 38.5 m/s | **PASS**, 41.0 | **PASS**, 45.0 |
| hot 50 C (viscosity x 0.6, `EST`) | 6.2e-4 | **PASS**, 35.5 | **PASS**, 38.0 | **PASS**, 41.5 |
| **nominal 25 C** | **1.03e-3** | **PASS**, **40.5** | **PASS**, 43.5 | **PASS**, 48.5 |
| cold 0 C (x 2, `EST`) | 2.06e-3 | **PASS**, 44.5 | **PASS**, 48.5 | **PASS**, 54.5 |
| leak: half of hot | 3.1e-4 | FAIL (16 points, band 0.72-0.87, 28.5 m/s, 0.045 % damping short) | PASS, 30.0 | PASS, 32.5 |

All of these hold for **every K from 0.01 N m/rad (free play) to 20**, which is why free play no longer matters: the damper acts between the elevon and the wing, in parallel with whatever the servo does. The two `EST` temperature factors (PDMS viscosity-temperature coefficient) must be measured on the coupon (E1 step 6). A leaking damper loses the margin: seal with the two O-rings in BOM R13 and check the fill at every preflight.

**K in service and the preload (what the spring can and cannot do).** A stiff parallel spring is not available: for K >= 2 N m/rad the spring torque at 20 deg would be 2 x 0.349 = **0.70 N m, against a servo that holds 0.397 N m**. So K in service is the servo-chain stiffness, `-` until E1 measures it (the 1.2 mm steel pushrod is 885 N m/rad at the 12.9 mm horn `CALC`, the horn and rod are not the limit), and the design no longer depends on it. The preload is a **light elastic bias to take up gear and clevis slack**:
- Two silicone-rubber strips per elevon (0.25 x 2 mm section, 25 mm free length, E about 1.5 MPa `EST`, not looked up), bonded from the elevon lower nose to the core lower cove at y 0.07 and 0.14 (inboard of the servo pocket, no cap there), 12.3 mm below the hinge axis, pre-stretched 8.1 mm (33 %).
- Rate: 2 E A / L0 = 60 N/m, **k_s = 60 x 0.0123^2 = 0.0091 N m/rad**; preload **T0 = 0.006 N m**; stays taut through +-20 deg (torque 0.006 +- 0.0032, strain swing 17 % against 33 % pre-strain). Resulting K from the spring: **0.009 N m/rad** (negligible). The preload removes slack for hinge-moment excursions below 0.006 N m, about 0.1 deg at K 4.5 and 0.35 deg at K 1 (`CALC`): it **does not stay closed at flutter amplitudes**, so the damper, not the preload, is the flutter fix.
- Why so weak: the servo torque budget (s2) allows spring plus damper torque of only about 0.026 N m.

**Pushrod geometry (changed):** servo arm 19 -> **12 mm** (`ARM_X1`), horn pushrod radius 12.9 mm, rod 1.2 mm steel 42.5 mm long: elevon torque capacity = servo torque x 12.9 / 12 = 1.075 x. The QP-4 CAD arm was 19 mm, which would have cut the servo torque at the elevon to 0.68 x and failed the SERVO.md check that assumed equal arms. Rod load at stall 0.427 N m / 12.9 mm = 33 N, buckling 111 N `CALC` (MS +0.9 on 1.725 x).

### 1.4 Mass and the lighter-balance option
Damper pair 5.0 g (above); preload strips are inside the stator mass (0.4 g). With the damper carrying the margin, a **12.8 g lead strip** (-5.6 g pair) still passes the 28.8 line everywhere (c needed 4.2e-4 vs 6.2e-4 hot) but not the 37 m/s target when hot (needs 9.0e-4). Kept at 15.6 g; the 12.8 g strip is the mass fallback in s7.

## 2. Servo torque check, ES3054HV at 7.2 V, factor 1.5

SERVO.md convention: required = 1.5 x (load), pass if servo / required >= 1.5 (SERVO.md s1: arm = horn). Servo 0.397 N m at 7.2 V (`EST`, interpolated from the `V` 6.0 / 8.4 V figures), 0.333 N m at 6.0 V.

| Term (N m) | Value | Basis |
|---|---|---|
| Hinge moment at VD, +-20 deg | 0.151 | FIXES s2 (0.146 x 0.31 / 0.30) |
| Preload strips, worst: T0 + k_s x 21 deg | 0.0093 | s1.3 |
| Damper at servo slew, 60 deg in 0.11 s (8.0-9.5 rad/s) x 1.03e-3 | 0.0098 at 25 C; 0.0196 at 0 C (`EST` x 2) | ES3054HV 0.13 s / 60 deg at 6.0 V `V` (SERVO.md), faster at 7.2 V `EST` |
| Required, 25 C | 1.5 x 0.1701 = **0.255** | |
| **Factor at 7.2 V** | **1.56 PASS** | 0.397 / 0.255 |
| Factor at 7.2 V, 0 C | 1.47 (2 % short) | passes at 1.58 with the real 12 / 12.9 arm ratio |
| Factor at 6.0 V | 1.30 FAIL | the 7.2 V rail jumper stays a requirement (BOARD s3) |

All three terms at their worst together (VD hinge moment, full slew, 0 C) is a bounding case. The margin is thin: the damper and the preload together use 0.019 of the 0.026 N m the budget allows. A heavier preload or a stiffer damper does not fit.

## 3. G10: caps, stops, collision, assembly

### 3.1 What is drawn (`cad/a_model.py`, `FIXES2` block)
- **Stops: +-21 deg** (`ELEV_STOP`), 1 deg beyond the 20 deg control authority (software limit SERVO5/6, plant `EL_MAX` 20), so a mis-set endpoint or a servo test at full PWM runs into the stop, not into the cap. Two stop bosses per cap, one on each balance tab (y 0.250 and 0.320), bottom face coplanar with the tab face rotated to +-21 deg: **boss-to-tab gap 0.002 mm (contact) at the stop, boss-to-lead 1.26-1.43 mm** (`stop_check.py`). At +-22 deg (past the stop) only the boss meets the tab, 0.25 mm = 1 deg at 14 mm: the geometry stops the elevon, not the clearance.
- **Caps:** 4 PETG lens caps (WNG-008-RU/RL/LU/LL), single wall 0.6 mm (vase-mode print, `EST`), over the strip window y 0.230-0.340. Upper 2.41 mm high over the skin, x 144-178 mm; lower 2.96 mm high, x 147-182 mm (the lower poke is larger: 1.86 mm beyond the airfoil at -21 deg against 1.31 mm on the upper). **Clearance of the lead and tabs to the cavity: 0.50 mm minimum over -21..+21 deg** in 0.25 deg steps (both caps, `stop_check.py`), the design value. 3 mm bonding flange on the two sides and the fore end, none aft (it faces the elevon). Cap mass 3.0 g upper, 3.2 g lower: **12.4 g for four** `CALC` (FIXES carried 2 g).
- **No-protrusion alternative checked and rejected:** the lead must sit within 12-14 mm of the hinge to stay inside the 12-15 mm section, i.e. 25 g per elevon (FIXES s1.1); with the damper in place it would also need the elevon-tip pocket. Caps cost 12.4 g and about 1-2 % cruise drag (`EST`, add to the MISSION power line: the 4 caps plus the 2 damper housings, which stand 6.4 mm above the upper skin at the elevon tips, about 1.3 cm2 each).
- Core pockets for the bosses (grown 0.3 mm) and the damper notches are cut in the core; elevon-core cove re-cut for stop + 4 deg.

### 3.2 Gates re-run on the final geometry
| Gate | Result |
|---|---|
| `build_a.py` | PASS, 10 modules, 0 errors, 0 warnings; declared mass 1,231 g |
| `collide_a.py` at the stop (+-21 deg), 78 parts, 175 bodies, 0.05 mm | **PASS: static 0, -21 deg 0, +21 deg 0**, wire ends 0, folds 0 |
| `collide_a.py` at +-20 deg | **PASS, 0 / 0 / 0** |
| `collide_a.py` at +-22 deg (past the stop) | 6 hits: the stop bosses on the tabs, 0.25 mm each (4), and the elevon foam on the core cove, 0.07 mm (2). The elevon cannot reach 22 deg; this is the stop working |
| `a_assembly.py` | **PASS: 28 of 28 steps, 78 of 78 parts**, 0 blocked, 0 unsupported, no wire before its ends. New: B4 damper units from aft (a first version from outboard was blocked by the wing tip, 0.67 mm, and was changed), C2a / C2b caps lowered / raised onto the skin after the elevons |

## 4-5. Structure and what changes for the board
CAD structure with the cuts (wing 223.4 + fins 109 + feet 8.4 + hardware 30 + cage 113.3) = **484.1 g**, ceiling 494 g (9.9 g under); without the `EST` cuts about 521 g. The caps (12.4 g) and dampers (5.0 g) are the additions. The weigh-in (BOARD s1) now has to confirm more: **>= 27.2 g of the 41.6 g cuts** (foam density 16.6 g, printed parts 18 g, hardware 7 g), up from 11.8 g.

## 6. Foam allowable, FOAMULAR 150 at 103 kPa (`foam_103.py`, `foam_103.md`)
Compressive **103 kPa** (15.0 psi min, Owens Corning data sheet, ASTM D1621, board read 2026-11-15) at any density, so the 25 kg/m3 core has the same rating as 30. Tension (129 kPa) and shear (86 kPa) are the old 150 / 100 scaled by 103 / 120 (`EST`): the data sheet has no FOAMULAR 150 tension or shear row (searched 2026-11-15; the PINKCORE shear rows are another product and were not used). Loads and factors as structures iterations 2 and 3 (KP 2.156).

| Check | Stress (kPa) | MS at 120 basis | MS at 103 basis | Result |
|---|---|---|---|---|
| Foam shear around the spar from the bridge torque 2.44 N m, bond over |y| <= 0.15 m (iteration 3) | 78 | +0.29 | **+0.11** | **MARGINAL** |
| Same, **FIXES2 rule: bond over |y| <= 0.20 m** (0.40 m of bond) | 58 | +0.72 | **+0.48** | PASS (fix by design, build rule, +1 g epoxy `EST`; `a_model.py` E-WNG-01) |
| Foam bearing at the fin slot, 2 x 20 N on 65 x 23 mm | 57 | +1.11 | +0.81 | PASS |
| Foam shear, lift into the spar slot | 3 | +37 | +32 | PASS |
| Pack tray on the LE slot floor, 12 g crash, full floor (32.5 x 111 mm) | 19 | +5.3 | +4.4 | PASS |
| Same, only a quarter of the floor carrying | 76 | +0.58 | +0.36 | PASS |
| Servo stalled into the stop (0.427 N m at the elevon), epoxy on all four pocket walls (new check) | 50 | +1.0 | +0.73 | PASS (build rule: all four walls, not two) |
| Stop reaction at stall, 30 N peeling a cap (flange 3 mm + wall footprint 698 mm2) | 94 | +0.59 | +0.37 | PASS on the foam; **tape-skin peel has no allowable**: cap pull coupon (E1 step 5) |

C1's other re-checks (30 N prop strike on 1.0 mm cups) are untouched by this pass.

## 7. Mass and cost
- **Basic 1,231.3 g** (`cad_mass.json`; was 1,215.9, +15.4 g): caps 12.4, dampers 5.0, balance 32.2 (was 34.2 with caps), servo arm no change. CG **24.4 mm** (band 20-26, trim +-10 mm in the tray slots). Predicted (basic x 1.1174 + 48): **1,423.9 g**; `mission_gate_a.py` 1,419 g (wing line 223.4 g); capped +-5 % window mass limit 1.486 kg; uncapped sag window needs <= 1.441 kg. Headroom 16-21 g to 1,440. **Needs >= 27.2 g of the 41.6 g cuts to be real.** Fallback: lead 12.8 g (-5.6 g); thinner or shorter caps.
- `sitl/cad_mass.json` regenerated (balance mass 16.1 g, hinge inertia of the balance unchanged at 6.9e-6 kg m2 per elevon; the damper rotor adds about 0.3e-6 kg m2, not in the plant).
- **BOM-A.csv:** R12 silicone fluid $15 `EST` (data sheets give viscosity and density only; small-bottle price **not found**), R13 silicone cord and O-rings $6 `EST`, R11 note (caps 12 g of PETG), G04 yaw-test foam-board $10 -> $0 (cut from the R01 sheet offcut). `bom_a.py`: total **$1,775.09** (was 1,762.96), +30 % margin **+$105.08** (was +120.85), **G7 PASS**. The two new lines are `EST`; if either rises by more than $9 the +30 % margin falls under $100.
- `MASS-GATE.md` has a new section 7; `mission_gate_a.py`, `cad_mass.py`, `a_model.py`, `a_assembly_plan.py`, `BOM-A.csv` edited.

## 8. The board's elevon coupon test E1 (replaces and extends BOARD s2.3)
A 300 mm wing-section coupon with the **real** elevon, 15.6 g lead strip and tabs, both caps with bosses, the damper unit and its fluid fill, the preload strips, the ES3054HV at 7.2 V (rail measured under load), the 12 mm arm and 12.9 mm horn, and the 1.2 mm rod. Servos are in Order 1 (+$46.27); foam, PETG and lead are local.

| # | Measure | Method | Pass |
|---|---|---|---|
| 1 | Static hinge stiffness K | spring scale 30 mm behind the hinge, servo powered and holding, K = F r^2 / x; also with the preload strips off | Record K (`-` today). It no longer decides flutter. Require K >= 1 N m/rad for control accuracy; < 0.3 stops the build |
| 2 | **Free play** | dial gauge or laser on the trailing edge, push both ways to 0.5 N with the servo powered | **<= 0.5 deg total** (0.26 mm at 30 mm), strips fitted |
| 3 | **Ring-down damping** | pluck the TE with the servo holding; phone accelerometer or 240 fps video; log f and the decrement; c = 2 zeta sqrt(K I_beta), I_beta 1.69e-5 kg m2 (balance included) | **c >= 7.1e-4 N m s/rad at 25 C** (zeta = c / (2 sqrt(K I)); about 4.8 % at K 4.5). Absolute floor c >= 3.3e-4 (28.8 m/s line) |
| 4 | **Lead bond pull** | pull each tab root and the strip to 1.84 N x 1.5 = 2.8 N (15.6 g at the 12 g crash, `EST`) | >= **3.0 N** per tab, no creep after 10 min |
| 5 | **Mechanical stop and cap bond** | with the lead fitted, drive the servo to full PWM both ways on a current-limited supply; protractor | elevon stops at **21.0 +- 0.5 deg**, no jam, caps unmoved; cap pull test 45 N (30 N stall reaction x 1.5) on the tape skin: no peel |
| 6 | **Damper over temperature, life** | repeat step 3 at 0 C (freezer) and 50 C (heat gun, thermocouple); 1 h at 45 Hz on a shaker or vibrating plate; leak check | **c(50 C) >= 4.0e-4** and c(0 C) servo factor still >= 1.5; no weeping; fill within 10 % after the shake |
| 7 | Free-play flutter probe | strips off, free play deliberately 1 deg, tap and fan at a wind speed near 20 m/s if a fan allows | no sustained oscillation; the model predicts margin at every K |

**Fail actions:** step 3 or 6 low: raise c by narrowing the gap (0.30 -> 0.25 mm gives x 1.2), lengthening the sleeve (limit 17 mm), or a higher-viscosity fluid; step 2 high: fit a stiffer horn clevis, replace the servo arm bearing; step 5 peel: enlarge the flange or add a second boss row.

## 9. Open items for the board
1. Weigh-in must now show >= 27.2 g real cuts (s5, s7); decide the 12.8 g lead fallback in advance.
2. The damper is modelled as spread over the span and sits at the tip (`EST`); E1 step 3 measures the elevon-mode damping, but a 3-D elevon torsion mode is not modelled.
3. Cap and damper drag, about 1-2 % of cruise each (`EST`): add to the MISSION power line.
4. Silicone fluid price (`-`) and viscosity-temperature factors (`EST`) are not looked up.
5. The cold-case servo factor is 1.47 on equal arms (1.58 with the real arm ratio): confirm the slew-plus-VD-hinge-moment bounding case on the bench.
6. `A.param` SERVO5/6 MIN/MAX stay at +-20 deg; they must be calibrated with the lead on and the stop measured (M13).
