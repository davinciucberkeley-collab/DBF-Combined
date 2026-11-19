# T-073 O4 Phase 1 checks (R-OPT-01, R-OPT-05, R-PHY-08), concept A, 2026-11-19

Status: analysis only, $0, **NOT VERIFIED COMPLETE**. Nothing committed. Edited one existing file: `redesign/qp/A/structures/arm_cup_checks.py` (new `--r3` / `--r3fix` flags; default output unchanged, `arm_cup_checks.md` byte-identical after a rerun, `git status` shows it unmodified). New files only under `redesign/qp/A/mechanism/out/T073_data/`. No CAD, docs/, CHANGE-LOG, ledger, MASS-GATE, `landing_path_a.py` or `landing_*` script edited; no SITL.
Inputs: D-216 / T-070 s4 (R1-R5, W, T), s7 steps 4-6; T-067 (adopted printed masses, basis S/M/C); T-071 (skin 1 ply 48 g/m2 +-45, strut 6x4.0, GJ/EI/mass); `landing_a.py` force histories; AM-005 (O4).

## Acceptance test (restated from the brief)
1. Step 4: hand calc and margin for R1 (windowed tray at the landing peak g), R2 (FC/ESC bosses, plate removed, vs IMU hard mount A-P25), R3 (lightened cups re-run through `arm_cup_checks.py`, default output reproducible), R4 (tubular strut clamps: bond, truss load); delta mass from volume x the T-067 basis.
2. Step 5: A-P10 wing modal / forced response (`fe_a.py` path of `iter3_run.py`) and `flutter_d205*` with the skin GJ, at both 1P bands including the lower hover band of a 10x4.5 prop (rpm basis and source stated). Stop rule: strongly coupled mode within 20 % of a 1P band that ply orientation cannot tune.
3. Step 6: `mission_gate_a.py` roll-up with all s4 deltas, skin, strut +3 g, T-068 package, and the O2 pack options, to a scratch output; predicted mass vs 1,470 g and vs the O4 target (about 1.58 kg EST).

## Categories
Step 4: rigid-body dynamics (landing_a traces) + hand-calculation part checks + geometry arithmetic. Step 5: FEA-class beam-frame modal analysis (`fe_a.py`) and flight-dynamics-class flutter (`flutter_a.py` Theodorsen). Step 6: illustrative mass bookkeeping + the repo's own mission arithmetic (`mission_gate_a.py`, `prop_a.py`). No interference, CFD or kinematics. Every allowable is the repo's EST value (no coupons) unless a source is named. "-" = unknown.

## Commands (cwd `redesign/qp/A/mechanism/out/T073_data` unless noted; all `python -I`, exit 0 unless noted)
| # | Command | Output |
|---|---|---|
| 1 | `python -I t073_traces.py` (32 s) | `traces_out.txt`, `t073_traces.pkl` (23 cases, D2 pad, plateau 30 N, dt 2e-4) |
| 2 | `cd ../../../structures; python -I landing_a.py 30` (cross-check, 33 s) | `landing_a_30N.txt` (hard level n 10.79, matches T-069/T-071) |
| 3 | `python -I t073_step4.py > step4_out.txt` | `step4_out.txt` |
| 4 | `cd ../../../structures; python -I arm_cup_checks.py` (default) / `--r3` / `--r3fix` | `arm_cup_default_stdout.txt`, `arm_cup_r3_stdout.txt`, `arm_cup_r3fix_stdout.txt`, `arm_cup_checks_r3.md`, `arm_cup_checks_r3fix.md` |
| 5 | `python -I t073_modal.py` with env `T073_SKIN`, `T073_PROP`, `T073_O4`, `T073_PLIES`, `T073_ROT`, `T073_EIIN`, `T073_OPEN` | `modal_*.txt` (20 runs; names say the case) |
| 6 | `python -I t073_flutter.py wing` (base `T073_FSKIN=0`, skin 1 ply, skin 2 plies) and `... elevon` (23 s) | `flutter_wing_*.txt`, `flutter_elevon_skin1.txt` |
| 7 | `python -I t073_rollup.py > rollup_out.txt` | `rollup_out.txt`, `rollup_raw/*.txt`, `equal_current_12A.txt` |
Self-checks: `flutter_wing_base.txt` reproduces `flutter_d205_wing.md` row for row (10.4 / 41.0 / 77.8 Hz kd ... 163.4 Hz, 46.2 ... 56.3 m/s); `rollup_out.txt` S0 reproduces `mission_gate_a.py` (1,466 g, window +-5.4 %); S1 reproduces T-067 (1,632 g itemised, 1,624 g flat; T-067 1,633 / 1,625, 1 g from the 1,273.3 vs 1,274.3 basic).

## Headline
1. **R1 as specified FAILS** (tab bending RF 0.25, end wall RF 0.24, hub bond RF 1.00 on a 1.2 mm plate). A passing variant (R1'') saves -10.1 g, not -16.3 g.
2. **R3 as specified FAILS** the strike S2 plate cantilever (MS -0.71). Keeping 5 mm over the +y cantilever (R3fix) passes with unchanged margins; saving -11.2 g.
3. R2 passes (mount stiffness RF 2.8 / 4.3, bonds RF 98); saves -16.9 g. R4 bond RF 1.92 (better than the present 1.09) but the socket-to-ring junction is 0.87 on an EST footprint (needs fillets in CAD); saves -5.8 g.
4. **Step 5 STOP rule triggers** for the 10x4.5 lower hover band (and for the hi property corner at 9x4.5): the strongly coupled cage / wing-torsion mode with the skin sits at 71 / 78 / 89 Hz (kd / nom / hi) inside the 10 in exclusion zone 70.2-304 Hz, within 7-15 % of the 84.3-100.3 Hz hover 1P band, and neither more nor less ply, nor ply angle, moves it out (s5.3). Forced response at 10 in hover rpm with the skin is 55-79 m/s2 (limit 30).
5. **Step 6**: O4 engineering list with the passing variants predicts **1,634 g (9 in, 270 g pack) to 1,575-1,608 g (with O2 pack and 10 in props)** itemised, 1,560-1,626 g flat, i.e. 105-164 g over 1,470 g and 0 to +54 g over the 1,580 g O4 target. **The 10 in prop's thrust gain depends on the current allowed:** -6 % at equal current to the 9x4.5, +3 % at 12.1 A, +11 % at the 13 A rating (T-070 assumed +7.3 % at equal shaft power, which is not the current-limited case).

## Step 4 hand calcs (`step4_out.txt`)
Landing peak loads on the pack (limit, 23 cases, M 1.5 kg, plateau 30 N, D2 pad; N_x = m_pack (sum|Fx_feet|/M + lam g), lam 0.667): axial on the aft lip **11.47 g** (hard level) = 30.4 N for the 270 g pack (BOM W01); lateral y 3.27 g = 8.7 N; z 3.10 g = 8.2 N. Factor KP 2.156 on printed/bonded parts. Tilt neglected (end tilt <= 3 deg).
Stance geometry: body +x is down, so the pack sits on the aft lip (z 8..18 mm, 2 mm thick, 109 wide in the CAD) and on one end wall (51 mm long, z 8..30, 2 mm).

### R1 pack tray CGE-008 (T-070: plate 1.2 mm 50 % windows, rim/ribs 1.2, end walls 1.2 mm 60 % windows, lips = 2 tabs 20 x 1.2 mm)
| Check | Demand | Allowable (EST) | RF |
|---|---|---|---|
| Aft-lip bending, baseline 2 mm x 109 | 5.0 MPa | 9.5 MPa interlayer | 1.92 |
| **Aft-lip tabs 2 x 20 x 1.2 (R1 as specified)** | 37.5 MPa | 9.5 | **0.25** |
| Tabs 2 x 30 x 2.0 / 2 x 20 x 2.0 | 9.0 / 13.5 MPa | 9.5 | 1.05 / 0.70 |
| Tabs 2 x 40 x 2.0 (R1'') | 6.8 MPa | 9.5 | 1.41 |
| Plate-end-face bond to the hub flange (27.2 mm wide), 2.0 mm plate | 1.20 MPa | 2.0 epoxy | 1.66 |
| same, **1.2 mm plate (R1)** | 2.01 MPa | 2.0 | **1.00** |
| 1.2 mm plate with 2.0 mm root pad (R1'') | 1.20 MPa | 2.0 | 1.66 |
| End wall lateral bending, baseline 2.0 mm solid | 5.8 MPa | 9.5 | 1.65 |
| **End wall 1.2 mm, 60 % windows (R1)** | 40.1 MPa | 9.5 | **0.24** |
| End wall 2.0 / 1.6 mm, 60 % windows | 14.4 / 22.5 MPa | 9.5 | 0.66 / 0.42 |
| End wall 2.0 mm, 30 % windows (R1'') | 8.2 MPa | 9.5 | 1.15 |
Not an RF: the eccentric moment of the lip load about the plate midplane is 0.43 N m; the plate lies on the 16 mm bridge tube and is strapped to it, so no unsupported-plate bound applies, but the contact and strap preload have no data ("-"): a drop coupon is needed. Strap z load 8.2 N limit; webbing strength "-". Orientation (tab rising in z, interlayer allowable) is an assumption: orientation is not specified anywhere in the repo.
Mass (volume x 1.27 g/cm3, members under 2.5 mm are solid in the T-067 M basis): R1 7.69 cm3 = 9.8 g vs 25.80 g adopted: **-16.0 g (fails)**. **R1'' (plate 1.2 mm windowed + ribs + 2.0 mm root pad, walls 2.0 mm 30 % windows, 2 tabs 40 x 2.0 per lip): 12.36 cm3 = 15.7 g, -10.1 g (passes, EST geometry).**

### R2 FC / ESC bosses, AVN-001 removed
Boss heights from `common.zu(x)` to the plane the CAD already uses: FC bosses at x 50 / 70 mm, heights 5.1 / 4.5 mm (to ZP+GEL 16.9 mm); ESC bosses at x 89.5 / 109.5 mm, heights 2.0 / 3.6 mm (to ZP 13.9 mm). Boss 6 x 6 mm (T-070), PETG E 2.1 GPa (`fe_a.py` nom). Stiffness is foam-limited: rigid square punch on a half-space, foam E 30 MPa, G 8 MPa (`landing_path_a.py`), nu 0.2 EST: 0.21 MN/m vertical, 0.12 MN/m shear per boss.
| Mount | mass | f_z | f_horizontal | f_rocking | RF vs 304 Hz |
|---|---|---|---|---|---|
| FC stack, 4 bosses | 17.0 g (AVN-002) | 1,115 Hz | 839 Hz | 1,055 Hz | **2.76** |
| ESC, 4 bosses | 7.2 g (BOM P04) | 1,719 Hz | 1,298 Hz | 1,923 Hz | 4.27 |
The 304 Hz criterion is 1.2 x the top 2P band (253 Hz) by the A-P10(a) convention, applied to a mount: EST (no mount-frequency requirement exists). A-P25 asks for a hard mount (thin foam tape or harder); the old tape has no stiffness datum ("-"), so no "better than before" claim. A-P10(b)'s FE still treats the FC as the rigid spar centre. Landing: FC + ESC at 11.5 g give 0.73 N per boss, bond RF 98; foam bearing at 3.1 g normal 5.5 kPa vs 103 kPa, RF 19.
Mass: 8 bosses 1.02 g (6 x 6 x h less M2 nut pocket and hole; nuts about 0.03 g each, EST) vs AVN-001 17.91 g adopted: **-16.9 g** (T-070 -15.0).
**Open for Phase 2 (the plate also carries these in the CAD): GPS 13.5 g and compass, the RP3 receiver, the AVN-008 seat, the ESC lead lanes; each needs its own pad (EST +1..3 g, not in the -16.9). ESC hole pattern and screw size "-" (not re-read).**

### R3 lightened motor cups (`arm_cup_checks.py --r3` / `--r3fix`; default run unchanged)
Flags: `--r3` = T-070 as written (5 mm boss plate, 3 mm web everywhere including the two +y cantilever tabs, sleeve wall 3.5 -> 2.5 mm, pockets keep 3.5 mm); `--r3fix` = same but the +y cantilever region keeps the full 5 mm plate. The tab width of the 3 mm web (2 x 9 mm) is my assumption (not drawn). Margins are MS (= RF - 1), the script's own convention.
| Row | default | `--r3` | `--r3fix` |
|---|---|---|---|
| Strike S2 plate cantilever bending beyond the sleeve end | +0.37 | **-0.71 FAIL** | +0.37 |
| Plate cantilever (operating) | +7.51 | +0.82 | +7.51 |
| Fatigue plate cantilever | +6.25 | +0.55 | +6.25 |
| Sleeve hoop at mouth, strike S3 (2.5 mm wall) | +2.19 | +1.28 | +1.28 |
| Sleeve hoop, operating | +57.66 | +40.90 | +40.90 |
| Plate-to-sleeve junction in-plane shear (20 x 3 mm web) | +13.69 | +7.81 | +7.81 |
All other rows identical to default (head pull-through, hole bearing, screws, arm). Worst six rows: default +0.33 (tip-over arm), +0.37, +0.39 ...; `--r3fix` the same six. Geometry note for CAD: with the sleeve OD 17.2 the crest sits 3.4 mm from the plate face, so a 3.0 mm web leaves a 0.4 mm gap: use a 3.4 mm web at the sleeve or fillet it. Head-pocket overlap row unchanged (18 % of head volume in the sleeve wall, handled by the local pocket bosses).
Mass: sleeve wall -1.29 cm3 (incl. +0.34 cm3 local pocket bosses, EST); plate in the adopted basis 3.39 cm3 (5.29 solid x 0.64 S-basis fraction) -> 2.60 (spec) / 2.46 (fix: 5 mm over the +y 13 mm, 3 mm cross web elsewhere, EST). x 4 cups x 1.27: **spec -10.5 g (fails), r3fix -11.2 g (passes)**; T-070 -12.0.

### R4 tubular strut clamps (socket OD 9 x 25 mm, wall 1.5; ring wall 2.5 mm)
Strut peak axial 227.6 N limit (23 cases; same value as T-071), x KP = 491 N.
| Check | Demand | Allowable | RF |
|---|---|---|---|
| Strut bond, present block (14.2 mm) | 1.83 MPa | 2.0 | 1.09 (T-071) |
| Strut bond, 20 mm / **25 mm socket** | 1.30 / 1.04 MPa | 2.0 | 1.54 / **1.92** |
| Socket wall axial (A 35.3 mm2), axis in the print plane | 13.9 MPa | 20 in-layer | 1.44 (0.68 if printed standing, 9.5 MPa) |
| Clamp ring on the spar D12 x 16 (Ny + torque Nx x 10 mm) | 0.92 MPa | 2.0 | 2.17 |
| **Socket-to-ring junction, 2 x 2.5 x 9 mm strips (EST footprint)** | 10.9 MPa | 9.5 interlayer | **0.87** |
| Strut Euler pinned 6x4.0 (unchanged) | | | 1.10 |
The bond RF of 1.92 needs the strut bonded the full 25 mm. The junction row is a footprint guess; it needs 2 mm fillets or a wider footprint in CAD, then a recheck. Mass: 2.91 cm3 (socket 0.88 + ring 1.82 + fillets 0.20 EST) = 3.69 g each vs 6.58 g adopted: **-5.8 g** (T-070 -5.2).

### Step 4 delta table (basic g)
| Item | T-070 | T-073 as specified | T-073 passing variant |
|---|---|---|---|
| R1 tray | -16.3 | -16.0 (FAILS) | **-10.1** (R1'') |
| R2 plate out | -15.0 | -16.9 | -16.9 |
| R3 cups | -12.0 | -10.5 (FAILS) | **-11.2** (r3fix) |
| R4 clamps | -5.2 | -5.8 (junction 0.87, fix in CAD) | -5.8 |
| Sum R1-R4 | -48.5 | -49.2 | **-44.0** |
(R5-R8 are not rechecked: T-070 values -2.0, -3.0, -0.4 are carried as EST in the roll-up.)

## Step 5 A-P10 modal / forced response and flutter with the skin
**Bands and rpm basis.** 9x4.5: hover 6,018 / 6,272 / 7,151 rpm (1P 100.3-119.2 Hz), cruise 7,300-7,600 rpm (1P 121.7-126.7 Hz) (`iter2_eval.py`). **10x4.5:** same real hover thrust, table thrust equal (both x 0.93): APC `PER3_10x45MR.dat` static rows read 2026-11-19 (https://www.apcprop.com/files/PER3_10x45MR.dat, via WebFetch; rows to 10,000 rpm only; thrust lbf x 4.4482, power hp x 745.7) against the 9x4.5 table in `prop_a.py`: hover rpm **5,056 / 5,268 / 6,017 -> 1P 84.3-100.3 Hz (2P 168.5-200.6)**. Cruise rpm is set by the 4.5 in pitch, so 7,300-7,600 rpm is kept (EST: not a computation). At the cap, equal shaft power gives 8,167 rpm (1P 136 Hz), uncapped 8,709 rpm. Exclusion zone for strongly coupled modes (coupling >= 0.5, A-P10(a): f <= band_low/1.2 or f >= 1.2 band_high): 9 in **83.6-304 Hz**; 10 in **70.2-304 Hz**.
**Skin model** (T-071 laminate, EST): GJ = 4 A^2 G t / perimeter = 49.9 N m2 (1 ply, nom; A 3,389 mm2, perimeter 383 mm), corner scale on skin G and E 0.7 / 1.0 / 1.3 for kd / nom / hi (EST spread, as T-071 V3), over |y| <= 0.40; out-of-plane EI 16.3 N m2 (from the CAD airfoil); in-plane EI 728 N m2 about the spar (509 at kd); mass 27.0 g + 5 g plates + 3.7 g strip; wing torsional inertia I'_EA from `flutter_a.wing_mass` added at the spar nodes (**the committed `fe_a.py` has none**: fe_a lumps carry 1e-5 m of rotary inertia, so I show every case also without it, `T073_ROT=0`). O4 masses (10 in cases): pack 232 g, tray -16 g, plate -17 g, props +3 g each (EST). Flutter: `flutter_a.GJ_parts`, `I12`, `wing_mass` patched at run time; GJ in series with the bare spar over the last 0.05 m.

### 5.1 Wing flutter, `flutter_d205_wing` cases with the skin (flutter-model frequencies, cantilevered semispan, fin on tip)
| Skin | corner | f1 / f2 / f3 Hz | flutter V m/s (x 28.8 line) |
|---|---|---|---|
| none (reproduces `flutter_d205_wing.md`) | kd / nom / hi | 10.4 / 41.0 / 77.8, 12.1 / 45.0 / 91.4, 14.0 / 51.3 / 106.0 | 46.2 / 49.5 / 56.3 |
| 1 ply | kd / nom / hi | 18.0 / 55.9 / 143.8, 20.5 / 64.3 / 165.7, 23.5 / 73.9 / 190.4 | 61.6 / 70.9 / 81.5 PASS |
| 2 plies | kd / nom / hi | 20.7 / 63.0 / 164.0, 23.6 / 72.9 / 189.1, 27.1 / 84.2 / 217.7 | 71.4 / 82.9 / 95.8 PASS |
| 1 ply, fins off | kd / nom / hi | 32.1 / 85.0 / 200.4 ... 40.7 / 115.3 / 259.9 | 81.9 / 98.5 / >100 PASS |
The wing torsion frequency rises from 41-51 to **56-74 Hz** (1 ply), not the 115-145 Hz of the T-070 scaling estimate (which took GJ x 8 on the whole chord; the series spar stub, the added mass and inertia and the fin hold it down). Flutter margin rises (VREQ 28.8 m/s). The 2nd torsion / bending mode f3 (144-190 Hz, 1 ply) falls inside the hover 2P / cruise 1P zone for the 9 in props; its motor coupling is not available in this model (FE below: the corresponding FE spar modes are weakly coupled, 0.1-0.2).
Elevon (`flutter_d205` cases, `flutter_elevon_skin1.txt`, wing f_h / f_a 18.3 / 56.0 (kd), 20.8 / 64.4, 23.8 / 74.0): no-damper case A still fails at kd and nom (as D-205: the damper is required; unstable K band 1.24-1.60 and 1.89-2.12, needed damping ratio 1.2e-3 / 3.3e-4, down from 7.4e-3 / 5.1e-3; hi passes); **damper cases B-E all PASS at all corners, lowest onset 41.5 m/s (case E kd) against 31.5 m/s before**.

### 5.2 FE modal and forced response (`fe_a.py` CFG of `iter3_run.py`, 100 modes, zeta 1 %, U 1 g mm, 1P + 2P of all rotors summed, worst-phase)
| Case (nom unless noted) | strongly coupled mode in the exclusion zone | highest strong mode below / limit | forced response, physical envelope (sum of axes, limit 30) |
|---|---|---|---|
| 9 in, no skin, no rotary inertia (iter3 basis) | none | 63 / 67 / 77 Hz (kd/nom/hi) vs 83.6 | 18.7 / 18.6 / 19.0 m/s2 at <= cap; sweep max 25.8 at 10,500 rpm |
| 9 in, 1 ply skin, no rotary inertia | **hi corner 89.8 Hz (coupling 1.12)**; kd, nom none | 72 / 79 / 57 vs 83.6 | 17.9 / 17.9 / 19.3 |
| 9 in, 1 ply skin, with rotary inertia | **hi corner 86.3 Hz (1.09)** | 69 / 76 / 56 | 25.6 (kd, 9,250 rpm) / 18.3 / 19.0 |
| 10 in, no skin, no rotary inertia | **hi corner 79.2 Hz (1.26)** | 65 / 70 / 54 vs 70.2 | 16.8 / 16.9 / **38.3 at 4,800 rpm** |
| 10 in, 1 ply, no rotary inertia | **kd 74.6, nom 81.7, hi 92.9 Hz (1.2)** | 47 / 50 / 58 | 16.6 / **54.3** / **70.4** (hover-rpm resonance, 4,900-5,600 rpm) |
| 10 in, 1 ply, with rotary inertia | **kd 71.1, nom 78.2, hi 89.0 Hz (1.16)** | 46 / 49 / 57 | 21.9 / 21.5 / **54.8** |
| 10 in, 2 plies, with rotary inertia | kd 76.9, nom 84.7, hi 96.3 Hz (1.11) | 48 / 53 / 61 | 20.1 / **48.7** / **63.9** |
| 10 in, 1 ply, skin absent for |y| < 0.057 (open centre cell) | nom 72.5 and hi 82.9 Hz (1.24) | see `modal_skin1open_O4_p10.txt` | |
The mode is the cage / wing-torsion mode (arm 43-46 % of strain energy, motor coupling 0.9-1.2). It exists without the skin at 56-68 Hz (committed iter3: "arm 46 %, 1.17" at 56-68 Hz) and the skin's torsion stiffness raises it by 20-30 Hz. Torsion GJ alone moves it (`T073_PARTS=gj` 78.6 Hz; out-of-plane EI, in-plane EI and mass alone do nothing to it; the in-plane EI variants (about the spar, about the skin centroid, none) are identical, so the 728 N m2 overstatement does not matter).

### 5.3 STOP decision (rule: strongly coupled mode within 20 % of a 1P band that ply orientation cannot tune)
**STOP for the 10x4.5 lower hover band, and for the hi corner at 9x4.5.** Reasoning:
- 10 in, nom: mode 78.2 Hz is 7 % below the hover 1P band edge 84.3 Hz and inside the 20 % zone (>= 70.2 Hz); hi corner (89 Hz) sits inside the band itself; kd (71.1 Hz) is inside the zone by 1 Hz.
- Ply count: 2 plies raises it to 84.7 Hz (nom), i.e. into the band. 0 plies (no skin) leaves 54-70 Hz with the hi corner 79 Hz already in the zone, plus forced response 38 m/s2 at 4,800 rpm.
- Ply orientation: `f` varies only about as GJ^0.10 (59 Hz at GJ 3.2, 78 Hz at GJ 53). To get nom below 70.2 Hz needs GJ of about 18 N m2: that is 0/90 at 1 ply (GJ 19), which T-071 V8 fails (P15 0.55, foam shear). ++/-45 -> +/-30 ... 38 deg lowers G 6-20 % only (about 3 Hz), well inside the property scatter (kd to hi spans 18 Hz). Above the band, 120 Hz would need GJ of order 10^3-10^4 N m2: not reachable.
- 9 in: nom 76-79 Hz is clear of the 83.6 Hz limit by 5-9 %, kd clear, hi corner (skin G and E x1.3) hits at 86-90 Hz. A 9 in aircraft with a skin therefore has no margin on the stiff corner; the scatter basis (x0.7 / 1.3) is my EST, not measured.
- Forced response with the skin at 10 in hover rpm (4,900-6,000 rpm) is 49-79 m/s2 on the nom / hi corners against the 30 m/s2 limit (sum-of-axes bound; the per-axis VIBE-like figure is about 1/sqrt 2 of the largest axis, still above 30).
A fix needs a design change, not a ply choice: re-tune the cage (V-strut / bridge stiffness moves the arm mode), or keep 9 in props, or notch/balance (A-P10(d) fallback) with numbers; all are Phase 2 decisions. The tap test must measure this mode (cage + wing torsion) before Dec 15.

## Step 6 roll-up (`rollup_out.txt`; scratch, not MASS-GATE)
`mission_gate_a.py` source executed with the item list modified; deltas carry the item's growth (20 % EST). Window = repo T/W arithmetic (sag 3.73 V/cell, 0.90 spin cap, cant 17 deg, x0.93), not the C3 time-domain run.
| Scenario | basic g | itemised g | flat rule g | vs 1,470 | vs 1,580 | window +- % | cruise to BATT_LOW min (need 3.41) |
|---|---|---|---|---|---|---|---|
| S0 listed now | 1,273.3 | 1,466 | 1,470 | -4 | -114 | 5.4 | 4.24 |
| S1 T-067 basis (+138.1) | 1,411.4 | 1,632 | 1,624 | +162 | +52 | 0.1 | 3.28 |
| S2 + R1-R4 as specified | 1,362.2 | 1,573 | 1,569 | +103 | -7 | 1.9 | 3.60 |
| S3 + R1-R4 passing variants | 1,367.4 | 1,579 | 1,575 | +109 | -1 | 1.7 | 3.57 |
| S4 + R5-R8 (T-070 EST) | 1,362.0 | 1,573 | 1,569 | +103 | -7 | 1.9 | 3.60 |
| **S5 + skin 35.7, strut 3.0, T-068 12.0 (O4 engineering, 9 in, 270 g)** | 1,412.7 | **1,634** | 1,626 | **+164** | +54 | 0.0 | 3.27 |
| S6 + pack 232 g (CNHL 2000) | 1,374.7 | 1,596 | 1,583 | +126 | +16 | 1.2 | **2.38** |
| S7 + pack 211 g (2200 40C) instead | 1,353.7 | 1,575 | 1,560 | +105 | -5 | 1.8 | **3.23** |
| S8 S6 + 10x4.5 props (+12 g), duty cap 0.90 | 1,386.7 | 1,608 | 1,597 | +138 | +28 | 11.1 (+28 % current) | 2.67 |
| S9 S7 + 10x4.5 props | 1,365.7 | 1,587 | 1,573 | +117 | +7 | 11.8 | 3.51 |
| S10 / S11 + thermoformed cover -4.5 g (232 / 211 g) | 1,382.2 / 1,361.2 | 1,603 / 1,582 | 1,592 / 1,568 | +133 / +112 | +23 / +2 | 11.3 / 11.9 | 2.70 / 3.53 |
| S12 S8 with R1/R3 as specified | 1,381.5 | 1,602 | 1,591 | +132 | +22 | 11.3 | 2.70 |
Answers: **predicted mass is 105-164 g over 1,470 g (itemised) in every O4 scenario** (flat rule 98-156 g over); against the O4 re-derived target of about 1.58 kg (EST, T-070 s6) it is **-5 to +54 g** (itemised) and **-12 to +46 g** (flat); only the 211 g pack with the T-070 R5-R8 list and no 10 in prop (S7: 1,575 g itemised, 1,560 flat) is under it, and it then has a 1.8 % window.
**Pack energy (T-070 O2 was wrong in a favourable direction):** the 2000 mAh pack gives 2.38 min cruise to BATT_LOW at 1.50-1.6 kg, not the 3.66 min of the linear scaling (hover, transition and climb energy are fixed): it **fails** the 3.41 min need. The 2200 mAh 211 g pack gives 3.23 min (9 in, **fails by 0.18 min**) or 3.51 min with 10 in props (passes). "U" pack masses and the CNHL ratings are search snippets; the sag figure for a 40C pack is "-".
**10x4.5 thrust, from the APC static tables with the repo's motor model (Kv 780, Rm 0.173, I0 0.5 EST), sag, vs the 9x4.5 at duty cap 0.90 (7.72 N per motor):**
| 10 in fresh motor current | duty cap | sag thrust | vs 9 in | mass for +-5 % window |
|---|---|---|---|---|
| 11.15 A (equal to 9 in at 0.90 fresh) | 0.755 | 7.24 N | **-6.2 %** | 1,386 g |
| 12.1 A (9 in one motor at 0.90) | 0.803 | 7.98 N | +3.4 % | 1,529 g |
| 13.0 A (A-P16 rating, no margin) | 0.843 | 8.59 N | +11.3 % | 1,646 g |
| 14.25 A (duty 0.90, the S8-S12 rows) | 0.90 | 9.50 N | +23.1 % | over the rating |
(9 in at 0.90: mass for +-5 % = 1,478 g.) At equal current the larger prop is worse because the motor is torque-limited (T/Q falls with diameter at fixed Cp/Ct), which is the opposite of the equal-shaft-power momentum estimate (+7.3 %). A-P16 requires 0.90 cap on the 9x4.5 to keep 12.1 A (one motor) under 13 A; the 10 in prop reaches the O4 gain only by spending that margin. Window at 1.58 kg: 9 in +1.7 %; 10 in at 11.15 A -1.5 %; at 13 A +7.0 %; the S8-S12 rows (+11-12 %) assume 14.25 A and are not admissible.

## Findings
| ID | Severity | Evidence | Needed |
|---|---|---|---|
| F-1 | CRITICAL | O4 step 5: strongly coupled cage / wing-torsion mode inside the 10 in exclusion zone with the skin (71-89 Hz, 7-15 % below the 84-100 Hz band), forced response 49-79 m/s2 at hover rpm; ply count and angle cannot move it out (s5.3). The same mode hits at 9 in on the hi corner. | Decision before the Dec 15 go/no-go: cage tuning, keep 9 in, or a measured tap test. Not mine to relax A-P10. |
| F-2 | CRITICAL | O4's premise (10 in thrust +7.3 %) is current dependent: -6 % at equal current, +11 % only at the 13 A rating. Predicted mass 1,575-1,634 g itemised vs the 1,580 g target. | Bench the 1045 props at 12.1 and 13 A; decide whether A-P16 margin may be spent. |
| F-3 | MAJOR | R1 and R3 as written fail (R1 tab 0.25, wall 0.24; R3 plate MS -0.71). Passing variants save 10.1 and 11.2 g instead of 16.3 and 12.0 g. | Phase 2 uses R1'' and r3fix; the tab/wall geometry is EST. |
| F-4 | MAJOR | R4 junction 0.87 and R1 plate bond 1.00 are at or below 1.0 on EST footprints; R2 leaves GPS, receiver and cover seat without a plate. | CAD fillets / root pad; Phase 2 mounts for GPS and RX. |
| F-5 | MAJOR | O2 pack arithmetic: 2000 mAh gives 2.38 min, 2200 mAh 3.23 min (9 in): below 3.41 min. | Re-run T-070 O2 with fixed hover / transition energy. |
| F-6 | OBSERVATION | Skin raises wing flutter margins (V 62-82 m/s vs 46-56); elevon no-damper case still needs the damper; wing torsion 56-74 Hz, not 115-145. | none |

## Limits of this record
Every allowable is EST (no coupons); the printed-orientation assumptions (interlayer on tab roots, in-layer on strut sockets) are not specified in the repo. The skin property spread x0.7 / 1.3, the foam half-space stiffness and the 304 Hz mount criterion are my EST. The FE wing has no chord inertia in the committed model: I added it from `flutter_a.wing_mass` and show both. The "strongly coupled" threshold 0.5 is A-P10(a); no per-axis VIBE figure is computed. The 10 in rpm basis is a static-table, equal-thrust computation (cruise rpm kept by pitch: EST); the 10 in prop mass (+12 g) is T-070's EST. The window figures are `mission_gate_a.py` T/W arithmetic, not the C3 time-domain run (A-P3 governs). R5-R8 are T-070 values, not rechecked. No FEA of the cups, hub or tray (hand calcs only, as T-070 s7 step 4 asks), no SITL, no CFD.
