# QP-4 fixes: elevon balance (D-187 v2), roll rate, mass headroom, concept A (D6 / D1 / A3 / B3, 2026-11-15)

Labels: `CALC` computed here, `EST` estimate, `SITL` this machine, `V` vendor/source page, `-` unknown. Files edited only in `redesign/qp/A/` (list in s6) and this report. No git. Reproduce: `python -I redesign/qp/A/structures/fixes_run.py` (1.5 min, writes `fixes_run.md`), `cad/build_a.py`, `collide_a.py`, `a_assembly.py`, `sitl/cad_mass.py`, `python -I mission_gate_a.py`, `SCR=<scratch> jobq.py jobs_z5.txt` then `fwd_sum.py Z5_*`.

## Verdict

| Item | Result |
|---|---|
| 1 Balance fits and passes flutter | **Done, with one open flag.** 15.6 g lead strip per elevon, 20 mm ahead of the hinge, two tabs, two printed lens caps over the skin window (2.0 mm pokes at the stops, 1.4 mm outside the outer skin `CALC`). Elevon flutter 41 / 38 / 54 m/s at K 0.02 / 0.2 / 5 (target >= 37, undamped, same basis as FLUTTER.md). Open: K about 0.5-1 N m/rad gives 32 / 22 m/s undamped (the as-drawn QP-4 balance gave 32 / 22 too; FLUTTER.md never swept K = 1). |
| 2 Roll rate | **PASS.** Elevon outboard end y 0.34 -> 0.35 (+10 mm). SITL 92.9 deg/s (1.41 kg) and 94.1 deg/s (1.50 kg), was 89.3 / 89.8. |
| 3 Mass headroom | **33 g net saved while paying for the heavier balance**: predicted 1,439.7 -> **1,406.7 g** (ASDRAWN script method), CAD method 1,432.5 -> about 1,399.6 g. Gross savings 41.6 g basic, balance +11.6 g basic, net 29.6 g basic (s3). Structure vs 494 g still goes to the board (s3.4). |
| CAD check / collision / 25-step assembly | PASS / PASS (0 at -20, 0 at +20 deg) / PASS (25 of 25, 70 of 70) |
| SITL re-run (roll, transition at 1.41 and 1.50 kg, back-transition) | all pass; see s5 |
| `A.param` | `Q_WVANE_ENABLE` back to **0** (failed turbulence; heading is pilot yaw per D-184) |

## 1. D-187 balance that fits (item 1)

### 1.1 Why the QP-4 balance did not fit, and what is possible
The lead sweeps an arc about the hinge, so its vertical travel is 2 r sin 20 deg = 0.68 r, while the section at x = XH - r is only 12-15 mm thick and the skins take 0.6 mm each (`CALC`, CAD airfoil `zu`/`zl`, hinge axis on the upper skin). The poke through the skin, minimised over the lead height, is almost linear in r (0.3 mm per mm of reach), `CALC` for a strip 10 mm long, 1.0-1.2 mm thick:

| Reach r (mm) | 12 | 14 | 16 | 18 | 20 | 22 | 26 | 30 |
|---|---|---|---|---|---|---|---|---|
| Poke beyond the inner skin line (mm) | 0 | 0.4 | 1.0 | 1.4 | 2.0 | 2.6 | 4.1 | 5.1 |

A lead strip that fits entirely inside the section needs r <= 12-14 mm, i.e. 322 g mm / 13 mm = **25 g per elevon** (50 g pair): rejected, 1.5x the QP-4 balance. Density does not help (mass = moment / reach for any material); it only thins the strip, and the strip thickness is a small part of the poke (1.2 -> 1.0 mm gains 0.3 mm). A horn below the wing in a fairing was checked on geometry: the pod would rotate 0.34 r up into the skin at +20 deg, so it still needs a window in the lower skin plus a pod 14 mm below it, which is a larger drag item than the caps (not drawn).

### 1.2 Chosen design (lightest that passes): distributed lead strip at 20 mm, thin tabs, lens caps
Per elevon (CAD `WNG-007-R/L`, parameters `BAL_*` in `a_model.py`):

| Part | Size | Mass g |
|---|---|---|
| Lead strip, 11.34 g/cm3 | 10 x 1.3 mm section, 106 mm long, y 0.232-0.338, centre 20 mm ahead of the hinge, 6 mm below the hinge axis | 15.6 |
| Two PETG/CF tabs (to the elevon nose) | 6 x 1.2 mm, 11 mm long, at y 0.285 +-0.035 | 0.5 |
| Two printed lens caps over the pocket window (upper and lower skin), fixed on the wing | about 100 x 22 mm, 1.8 mm high `EST` | 1.0 |
| **Total** | | **17.1** (was 11.3) |

The strip starts 9.5 mm outboard of the servo-pocket wall (y 0.2225) and 12 mm inside the elevon tip (0.35). The strip spreads the moment over 106 mm of span, so the elevon nose is not loaded at one point. Core pocket is now the sweep hull over the 108 mm window (the spar at x 60 stays the torsion path, `EST`, C1 to confirm). The elevon balance moment is 322 g mm (lead 15.6 g x 20 mm plus tabs) against 206 g mm for the foam elevon (9.6 g x 21.4 mm): 1.5x, the same ratio FLUTTER.md recommended. Elevon CG falls 6.1 mm ahead of the hinge.

Open caveats: caps are **not drawn** in the CAD (mass is in `WNG-007`); lens-cap drag not computed (frontal area about 2 cm2 per cap, `EST`, roughly 1-2 % of cruise drag if all four stand proud at the stops only; at neutral the lead sits inside the skin line over most of the window); lead to the elevon nose is epoxy plus the tabs, bond strength unmeasured; lead is `EST` $10 (BOM R11, price not looked up).

### 1.3 Flutter (`structures/flutter_a.py` extended: `FOAM_RHO`, `ritz(lumps=)`, `first_flutter(gthr=)`; run `structures/fixes_run.py`, output `fixes_run.md`)
Elevon 3-DOF section, wing f_h 12.2 and f_alpha 45.1 Hz from the Ritz run with the balance on the wing; elevon 9.6 g `EST` (foam 25 and 10 mm more span), CG 0.35 of its chord. Speeds m/s, G8 line 28.8, K = hinge stiffness per elevon in N m/rad:

| Case | g_s | K 0.02 | 0.05 | 0.1 | 0.2 | 0.5 | 1 | 2 | 5 |
|---|---|---|---|---|---|---|---|---|---|
| QP-4 as drawn (10.7 g at 30 mm) | 0 | 40 | 39 | 38 | 37 | 32 | 22 | 49 | 53 |
| **D-187 v2 (15.6 g + tabs at 20 mm)** | 0 | **41** | 40 | 39 | **38** | 32 | 22 | 50 | **54** |
| D-187 v2 | 0.02 | 44 | 43 | 43 | 41 | 37 | 46 | 52 | 55 |
| lighter, 12.8 g + tabs | 0 | 37 | 37 | 36 | 34 | 27 | 13 | 51 | 54 |
| lighter, 12.8 g + tabs | 0.02 | 40 | 39 | 39 | 37 | 32 | 46 | 52 | 55 |
| heavier, 17.0 g + tabs | 0 | 42 | 42 | 41 | 39 | 34 | 25 | >100 | 54 |

- **Target >= 37 at K 0.02 / 0.2 / 5 (FLUTTER.md basis, undamped): met, 41 / 38 / 54.** The 12.8 g strip fails that basis (K 0.2: 34) and passes only if 2 % structural damping is credited; not taken (damping of a servo-hinge joint is unmeasured).
- **New finding:** the balanced elevon has a dip at K about 0.5-1 N m/rad (32 and 22 m/s undamped, below the 28.8 line at K = 1), where f_beta crosses the 45 Hz wing torsion. The unbalanced elevon is fine at K = 1 (43 m/s). In the undamped model the instability is a weak coalescence (aero g 0.001-0.011 at low speed); with 2 % structural damping it is gone (46 m/s). A servo-driven elevon with <= 1 deg free play has K above 1 `EST` (FLUTTER.md), so K = 1 is the edge; FLUTTER step 5 (spring-scale K test) is now **required before the elevons are glued**, with the acceptance K >= 2 N m/rad (52 m/s) instead of 1.
- Wing bending-torsion with the balance lumps (2 x 18.1 g incl. caps at x 164, y 0.285) and foam 25: kd / nom / hi **46.2 / 49.7 / 56.4** (QP-4 46.0 / 49.3 / 56.2); fins off 34.6 / 41.4 / 48.3; 3-D lift 57-70. All >= 28.8. Divergence unchanged (the elastic axis is the spar).
- Control reversal, y 0.04-0.35: 37 / 42 m/s (kd / nom, 3-D, e/c 0.10), 28 / 32 on the 2-D bound: **unchanged** from y 0.34 (marginal on the 2-D bound as before).

## 2. Roll rate (item 2)

Options with the SITL's finding (surface-limited: an elevon at the 20 deg stop with 13 deg differential plus trim):

| Option | Effect | Cost | Verdict |
|---|---|---|---|
| **Elevon outboard end 0.34 -> 0.35 (span 0.30 -> 0.31)** | roll authority (integral of y over the elevon) x 1.069 (`CALC`: (0.35^2-0.04^2)/(0.34^2-0.04^2)); steady 77 deg/s at 8.7 deg (was 72), 90 deg/s needs 10.2 deg differential (was 10.8) | +0.26 g per elevon; tip is 22 mm from the fin plane, no conflict | **chosen** |
| Chord 0.25 -> 0.26 c | about +4 % | balance moment x 1.08 (c^2) | rejected, loads the balance |
| Travel beyond +-20 deg | needs the C1 hinge-moment rule at VD 24 | pitch margin, servo | not needed |
| Aileron differential | cuts the up-going elevon's loss | little at a stop | not needed |

SITL `case=roll` (FBWA full stick right 3 s then left 4 s, A.param limits, 17 m/s): `fwd_sum.py` prints the peak in column units of deg/s x 57.3 (its `p_peak_deg_s` of 5,117 for the QP-4 run is 89.3 deg/s):

| Run | Peak roll rate | Differential at the peak | Elevon max | Bank |
|---|---|---|---|---|
| Z5_roll 1.41 kg | **92.9 deg/s** (5,323 / 57.3) | 13.0 deg | 20.0 deg | 49 deg |
| Z5_rollg 1.50 kg | **94.1 deg/s** (5,392 / 57.3) | 13.0 deg | 20.0 deg | 50 deg |

Rating: **pass, +3 to +5 % over 90.** (QP-4: 89.3 / 89.8.)
- Pitch use: transition 0.58-0.62 of the 15 deg basis, 0.44-0.47 of the 20 deg stop (s5.1), unchanged within 0.02; the 0.62 at 1.50 kg is still 0.02 over the old 15 deg basis, a board basis call as in ASDRAWN s3. Cruise trim 2.6-3.1 deg TE up (`fwd_checks.py`, CG 22.5 mm).
- **Servo torque at the new geometry** (ES3054HV, SERVO.md method): hinge moment 0.146 N m x (0.31 / 0.30) = **0.151 N m** `CALC`; x 1.5 = **0.226 N m** required. ES3054HV 0.333 N m at 6.0 V, 0.397 at 7.2 V (SERVO.md, V): 2.2x / 2.6x the hinge moment, **1.5x factor met** (1.47 / 1.76 on the 0.226). SITL peak hinge moment in transition 0.019-0.020 N m. Servo arm unchanged (<= horn arm).
- Elevon inertia with the balance at the hinge 1.7e-5 kg m2 per elevon (plant has no hinge dynamics; inertial torque 0.8 % of servo, negligible).
- Flutter at the new span: elevon table above (span 0.31 in the model).

## 3. Mass headroom (item 3)

Basic mass 1,245.5 -> **1,215.9 g** (CAD, `cad_mass.py`). CG **22.5 mm** (was 23.0; trim range 20.4-24.7 mm with the +-10 mm pack slots, still inside 20-26; the pack can move 2 mm aft to re-centre at 23, not done). Inertia 0.0617 / 0.0254 / 0.0683 kg m2 (roll / pitch / yaw).

### 3.1 Savings and costs (basic g, `EST` unless noted; every number is a CAD part mass or a stated formula)

| Item | Before | After | g saved | Basis |
|---|---|---|---|---|
| XPS foam 30 -> 25 kg/m3, wing core and elevon foam | 116 core + 2 x 8.5 | 102 + 2 x 8.0 | 15.4 | foam 82 g core (structures_a.py formula, kerf and elevon cut-outs) + 4.4 g per elevon, x 5/30. Foamular 150 is the BOM foam; Owens Corning EPD entry gives 1.3 lb/ft3 minimum = 20.8 kg/m3 (OneClickLCA, searched 2026-11-15; Owens Corning datasheet density row not read). **25 is a nominal estimate: weigh a block before ordering; compressive strength falls with density and the iter-2 foam-bearing checks used 120 kPa: C1 to re-run at 90-100 kPa** |
| Fin fairing foam 30 -> 25 (3 mm XPS, 2 fins) | 9.0 each | 8.4 each | 1.2 | 3.9 g foam x 5/30 per fin, rounded |
| Pack tray, 1.5 mm floor with ribs | 5.3 | 3.8 | 1.5 | print design, EST |
| Avionics plate, 4 lightening windows | 12.0 | 8.0 | 4.0 | EST |
| Motor cups, 4 | 5.0 each | 4.0 each | 4.0 | wall 1.2 -> 1.0 mm, EST; C1 to re-check prop-strike 30 N |
| Hub shell | 16.0 | 13.0 | 3.0 | 2 perimeters, 10 % infill, EST |
| Fin root blocks, 2 | 4.0 each | 3.2 each | 1.6 | EST |
| Foot shoes, 4 | 1.8 each | 1.4 each | 1.6 | EST |
| Spar plugs, 5 | 1.65 each | 1.2 each | 2.25 | 1.2 mm wall, EST |
| Hardware lump: no paint (aircraft is tape-skinned) | 37.0 | 30.0 | 7.0 | bottom-up: 16 motor M3 about 8 g, 43 epoxy joints about 15 g, clevis, strap, tie about 7 g; paint line removed. EST, weigh |
| Elevon span +10 mm (item 2) | | | -0.5 | +0.26 g each, already netted in the foam row |
| **Gross savings** | | | **41.6** | sum of the rows above |
| Balance D-187 v2 vs QP-4 | 11.3 each | 17.1 each | **-11.6** | s1.2 |
| **Net basic** | 1,245.5 | 1,215.9 | **29.6 g (CAD: 1,245.5 - 1,215.9)** | |

(Rows sum: 15.4 + 1.2 + 1.5 + 4.0 + 4.0 + 3.0 + 1.6 + 1.6 + 2.25 + 7.0 = 41.6 g gross; less the balance 11.6 g = 30.0 g; the CAD roll-up reads 29.6 g, the 0.4 g being the elevon-span mass in the CAD.)

### 3.2 Predicted mass (growth + overrun)

| Method | QP-4 (basic 1,245.5) | Now (basic 1,215.9) | Saved |
|---|---|---|---|
| ASDRAWN script method: basic x 1.1174 + 48 | 1,439.7 | **1,406.7** | **33.0 g** |
| CAD.md method: basic + 11.16 % growth + 48 | 1,432.5 | 1,399.6 | 32.9 g |
| `mission_gate_a.py` (growth by maturity, items updated to the CAD in this pass) | - | 1,400 (basic 1,215.9 + 136.5 + 48) | - |

Against the 1.44 kg target the headroom is **33-40 g** (was 0.3-7 g), and the transition window (+-5 % needs <= 1.441 kg, MASS-GATE) is met with 34 g to spare; capped window +-8.0 % at 1.40 kg (`mission_gate_a.py`). Gate 1.50 kg headroom 93-100 g.

### 3.3 What is not claimed
The weights are CAD masses; the printed-part, hardware and foam lines are `EST` and none is weighed. The honest range on the 41.6 g gross is perhaps +-10 g. The balance, the single biggest item, grew by 11.6 g because the QP-4 balance did not fit. Lighter balance options: lead 12.8 g (-6.2 g pair) if the K test shows K >= 2 N m/rad and 2 % damping is accepted; 2 mm foam elevons (-2 g each, FLUTTER.md) shrink the lead by a further 2 g each but cut K=0.2 flutter to 34-36.

### 3.4 Structure for the board
Structure (CAD, with the D-187 balance): QP-4 494.3 g; now wing 208 incl. balance 34.2, fins 109 + feet 8.4 + hardware 30 + cage 113.3 (CAD groups, not the board's 473 g partition). The balance grew 11.6 g, so the **494 g ask rises to about 506 g before the foam and printed-part cuts and falls to about 465 g after them** (CAD-based, STRUCTURES-R partition not re-derived). The board decision stands: raise the line, or accept the foam / printed-part cuts as the offset (41.6 g gross, if C1 accepts 25 kg/m3 foam and the thinner cups and hub).

## 4. CAD gates, re-run on the final geometry (`redesign/qp/A/cad/`)

| Gate | Result |
|---|---|
| `build_a.py` | PASS, 10 modules, 0 errors, 0 warnings; declared mass 1,216 g |
| `collide_a.py` (70 parts, 133 bodies, 0.05 mm) | **PASS**: static 0, elevons -20 deg 0, +20 deg 0, wire ends 0, folds 0 |
| `a_assembly.py` | **PASS, 25 of 25 steps, 70 of 70 parts**, 0 blocked, 0 unsupported, no wire before its ends. Step C2 now carries the elevons with the 106 mm strip (tabs enter the 108 mm pocket window from aft); strip y 0.232-0.338 clears the servo pocket (to 0.2225) |

## 5. SITL re-run, as-drawn (`sitl/jobs_z5.txt`, logs `sitl/runs/Z5_*` git-ignored; ArduPlane 4.7.3-beta1 JSON backend; 1.41 kg = predicted + overrun, 1.50 kg = gate)

SIM overrides as QP-3/QP-4: `THR_MAX 80`, `Q_WVANE_ENABLE 0`; **`wv_after` removed from the back-transition runs** because the vane is now off in A.param (QP-4 had it on after the back-transition), so the belly heading stays where the pilot left it. Plant: `cad_mass.json` (CG 22.5 mm, new inertia, elevon y 0.04-0.35, hinge inertia 1.7e-5).

### 5.1 Transition

| Mass | Wind (m/s, from) | Alt gain at handover / peak abs (m) | V handover | t to 1.3 Vs (s) | Pitch use of 15 / of 20 deg | Elevon peak (deg) | u max | Rating |
|---|---|---|---|---|---|---|---|---|
| 1.41 | 0 | 34.4 / 88.4 | 13.6 | 7.1 | 0.60 / 0.45 | 9.3 | 0.786 | pass |
| 1.41 | 5 head | 35.6 / 89.5 | 13.6 | 7.2 | 0.60 / 0.45 | 9.0 | 0.843 | pass |
| 1.41 | 5 cross | 35.9 / 89.8 | 13.7 | 7.1 | 0.58 / 0.44 | 8.9 | 0.832 | pass |
| 1.50 | 0 | 33.5 / 87.3 | 13.6 | 7.5 | 0.62 / 0.47 | 9.5 | 0.786 | pass (0.02 over on the old 15 deg basis) |
| 1.50 | 5 head | 32.4 / 86.0 | 13.5 | 7.4 | 0.62 / 0.46 | 9.3 | 0.851 | pass (same) |
| 1.50 | 5 cross | 32.5 / 86.0 | 13.5 | 7.4 | 0.62 / 0.47 | 9.6 | 0.837 | pass (same) |

No run reaches the 0.90 cap (0 s), no alt loss, peak 86-90 m (fence margin 20 m), cruise settles 17.1 m/s. The window at the gate mass (1.50 kg) is +-4.5 % as before; at the predicted 1.41 kg it is about +-7.6 % (`mission_gate_a.py` at 1.40 kg +-8.0 %).

### 5.2 Back-transition (vane off, pilot yaw, 0.5 m/s turbulence, 5 m/s wind unless noted)

| Mass | Wind from | Balloon above switch (m) | u max | Lean max in descent (deg) | Sink / lean / lateral at touch | Tipped | Rating |
|---|---|---|---|---|---|---|---|
| 1.41 | 0 (head) | 6.8 | 0.792 | **31.3** | 0.12 m/s / 29.1 deg / 0.16 m/s | no | pass |
| 1.41 | 45 | 6.8 | 0.858 | 23.5 | 0.15 / 17.2 / 0.21 | no | pass |
| 1.41 | 90 | 6.8 | **0.900 (at the cap, momentary)** | 21.0 | 0.28 / 9.9 / 0.10 | no | marginal (same flag as QP-4), no tip |
| 1.50 | 45 | 5.7 | 0.900 (momentary) | 21.9 | 0.23 / 11.0 / 0.50 | no | pass |
| 1.50 | 0 (calm) | 5.7 | 0.808 | 3.8 | 0.02 / 0.0 / 0.01 | no | pass |

Sink at touch 0.02-0.28 m/s against the 1.2 m/s design case; no tip-over. Without the vane the belly stays into the wind (heading 0 to -5 deg) so the **head-wind lean at touch is 29 deg** (QP-4 with the vane edge-on: 10 deg at touch for the cross-wind case). That is inside the A-P6 45 deg lean line but is the cost of D-184's pilot-yaw rule: the flight card must yaw the aircraft edge-on before QLAND in wind above 3 m/s.

### 5.3 Not re-run
Roll is in s2. Cruise trim, fence run-out and the weathervane turbulence runs were not re-run: not affected by these changes beyond the CG shift of 0.4 mm and 30 g of mass; QP-4 results stand.

## 6. `A.param`, files, and open items

- `A.param`: `Q_WVANE_ENABLE,0` (was 3); gain 1 and `SPD_MAX 2` kept so a later retest only sets ENABLE 3. Reason and the failed numbers are written beside it (15.4-23.7 deg at gain 1 against 15). Header notes the FIXES edits. Nothing else changed; SERVO5/6 MIN/MAX still to be bench-calibrated for +-20 deg.
- Files edited in `qp/A/`: `cad/a_model.py` (elevon y1, `BAL_*` strip with two tabs, masses), `sitl/cad_mass.py`, `sitl/cad_mass.json` (regenerated), `sitl/a_aero.py` (EL_Y1 0.35), `sitl/jobs_z5.txt` (new), `structures/flutter_a.py` (options), `structures/fixes_run.py` + `fixes_run.md` (new), `mission_gate_a.py` (items updated to the CAD), `BOM-A.csv` (R11 lead and caps, $10 `EST`; `bom_a.py`: total 1,762.96, +30 % margin +120.85, **G7 PASS**; was 1,751.94 / +135.18), `A.param`. `MASS-GATE.md` was not rewritten: its s2-s5 tables still carry the QP-3 values (basic 1,206 g); the numbers above supersede them (A1 to fold in).
- Open for owners: (1) **K test** (FLUTTER step 5) before the elevons are glued, K >= 2; (2) **weigh** a 25 kg/m3 foam block and a printed cup and hub, then re-run the C1 foam-bearing and prop-strike checks; (3) caps not drawn, drag not computed; (4) lead bond to the elevon nose; (5) board: structure line 494 g and the pitch-use basis; (6) flight card edge-on yaw before QLAND without the vane.
