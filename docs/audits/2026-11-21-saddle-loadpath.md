# D-226 fin-saddle / wing-root load path ruling, concept A O4b (2026-11-21)

Opus ruling on the T-077 part 6 / part 7 STOP. I wrote none of T-071b, T-076c/d, T-077 (parts 1-7), T-080, D-220..D-225 or the audits I cite. **This file is the only repo file I wrote.** No CAD, FEA, SITL, ledger, CHANGE-LOG, BOM or MASS-GATE file was edited or run. Status: **review record, not VERIFIED COMPLETE.**

Runs (all read-only; scratch scripts in the session scratchpad, not in the repo, each `python -I`, exit 0). They read `T077p6_data/demand_p6.json` and the git-ignored `T077p6_data/fea/demand_p6.npz` (foot forces, hub / R / L wrenches, a_cg, alpha; written by `t077p6_demand.py`) and do their own arithmetic. They import no repo module.
- `d226_check.py`: mass, CG and inertia split; hub My at the spar axis against the total foot couple; N8 by hand.
- `d226_p12.py`: P12 by hand from the foot forces.
- `d226_relief.py`: P12 with the d'Alembert relief of the outboard fin group.
- `d226_env.py`, `d226_zeta.py`, `d226_halves.py`: wrench envelopes per zeta, per wing half, and at the rib station x 0.17.
- `d226_hand.py`: every option row in s2 and s3.
Geometry constants are read from `cad/amodel/common.py` / `wing.py` (SPAR_X 0.060, HUB_X1 = -0.045 + CAGE_DX -0.012 = -0.057, BR_Z -0.002, YFIN 0.38, STRUT_S / STRUT_E at z 0, section heights `wing.zl / zu`). Repo constants are read from `structures/landing_path_a.py` (KF 1.725, KP 2.156, BOND 2.0 MPa, CF 350 / 30 MPa, F_SHEAR foam 86 kPa, G_S 3 GPa).

Limits held, none relaxed: RF >= 1.0 at max(DAF, 1.5); KF 1.725 / KP 2.156; D-223 DAF (2.23 bridge and interim wing / saddle / fin rows, 1.97 tubes / bond, 1.5 floor permanent); the 23 cases with the hard 1.2 m/s sink; pad zeta 0.02 / 0.05 / 0.10 and mu 0.40 / 0.30 as D-223; A-P3 window >= +5.0 % with the 3 % download at derate 0.93; no ballast; $2,000 total with the crash reserve held (BOM $1,957.51, margin +$42.49, `mechanism/out/T082_data/bom_t082.py`, re-run here: "Total 1,957.51 / Margin 42.49"). Every allowable is EST unless a source is named. 6061-T6 yield is 240 MPa (minimum; Wikipedia, read 2026-11-20 in T-076c s4 / T-080 s1, secondary source), judged von Mises x KF <= 240. "—" = unknown.

## 0. Ruling in one place

| # | Question | Answer |
|---|---|---|
| 1a | Is the p6 demand credible? | **Yes, and it is computed correctly.** `demand_p6.json` matches D-222 / D-223: Fp 30 N, stroke 24 mm, x_foot 0.3475 (D2 0.3415 + 6 mm), z_foot 0.1918, 1.705 kg, CG 23.91 mm, 23 cases x zeta 0.02 / 0.05 / 0.10 x mu 0.40 / 0.30. The stats reproduce D-222: zeta 0.10 gives n 12.41 g, zeta 0.02 gives stroke 21.5 mm and tilt 2.98 deg. Units are SI and the sum-to-zero residual is 3.2e-13. The moment arm P0 to spar axis is 0.117 m, which matches wing.py. **The hub pitch moment 12.83 N m RB at the spar axis is physical.** In the governing case (SITL Z5_b45 narrow, zeta 0.10, mu 0.30), the two z-side feet each carry 42 N, with 12.5 N of friction. The couple about the CG is 24.1 N m. Hand check: 2 x [0.199 x 42 + 0.324 x 12.5] = 24.8 N m. The hub group (motors, arms, hub, pack: 0.813 kg) holds **54 % of Iyy** (0.0187 of 0.0346 kg m2), because the motors sit at z +-0.156 m. So it must receive about half the couple: 12.83 / 24.1 = 0.53. The magnitude is capped by the pad force, not by the sink rate (s1.1). |
| 1b | Are the hand bounds right? | **N8 and P12 reproduce exactly by hand:** N8 0.491 RB / 0.220 at x2.23; P12 0.451 / 0.202 (s1.2). The struts are coplanar with the bridge (z 0), so they take about 1.5 % of My. Ignoring them is right. The fin rows ignore the inertia of the fin outboard of the cut. That is conservative by 23 % on P12 (0.451 to 0.554 RB), not by 4-5x. **The unconservative formulation is elsewhere.** P14a / P15 credit the glass skin with 89 % of the wing torsion (spar 5.6 %), but no drawn element puts torque into the skin cell. A ring bonded on the spar puts it into the spar. The foam can pass at most 6.2 N m into the skin over the whole 0.32 m bay, unfactored, against 56.9 N m needed (RF 0.11). So the spar is the actual torsion member, and it gives RF **0.10** (fin bay) / **0.16** (centre half) at x2.23 (s1.3). The P7.3 fixes "137 mm ring" and "96 mm ring" therefore would not work. |
| 1c | Root cause | **A missing load-path element, not a weak saddle.** The narrow-strike pitch couple has to cross 0.32 m of a 24 mm-deep foam wing, from the fin stations to the hub. Every design drawn so far (part-4 PETG saddles, X7 node, CF clamshell and cradle) hands it to a 12x10 spar through epoxy rings. Bonded-sleeve torque capacity scales with D² L, and the spar cannot carry the torque anyway. So no material or ring size fixes it. The same demand also fails the fin rows outside the saddles: rib tube 0.34-0.38 (torsion from spanwise friction x 0.19 m), 1-ply skin 0.40 (shear) / 0.39 (wrinkling, T-076d), root block and shoe (pre-package RB 0.41 / 0.55, T-076d; the drawn enlarged parts are not yet judged). |
| 2 | Load path chosen | **(a3) the torsion-cell path.** The wing's glass skin cell carries the pitch moment. Torque goes in and out of it through bonded CF bulkheads: a CF node at each fin station and a 6061 centre torque tube to two bulkheads at y +-0.060. The printed saddles FIN-005 and CGE-006 leave the primary path. The spar carries bending only. (b) a 6061 saddle and (c) a lower pad demand are rejected: their governing rows stay at 0.22 / 0.10 and about 0.3 (s2). The new parts pass by hand at x2.23 (minimum 1.16-1.49, s3). Two existing items must also change: the skin and the rib. |
| 3 | Window | **It cannot close.** The (a3) saddle replacement costs **+32.7 g basic (EST)**. With the 6.8 g already over, the gap is 39.5 g. The recoveries named in the Part 7 / CG-closure tallies give 6.6 g (elevon lead -5.6 g after a flutter re-run, Onyx shoes -1 g), plus 4-8 g from X7 root blocks, which are conditional on root-block rows nobody has judged. **Shortfall: 33 g basic with the bound demand (25-29 g with X7 blocks).** It is 55 g with the 2nd skin ply that D-223 already plans, and about 100 g on the full bound path (3-ply skin, 25x23 rib). Physics requirements that fail: **A-P3** (window about +3.7 % at +32.7 g; linear 0.0324 point per g, from P7.4's 6.8 g = 0.22 point). **A-P2 fresh T/W >= 2.0** also fails above 1.730 kg predicted (no download, derate 0.93, CG-closure s3.1). The saddle replacement alone gives 1.739 kg. |

## 1. Root cause: what I recomputed

### 1.1 Demand (`d226_check.py`, `d226_env.py`, `d226_zeta.py`, `d226_halves.py`)
- Point-mass model: 1.7050 kg. Hub group (idx 2, 3, 4, 6) 0.813 kg: Ixx 0.0304, **Iyy 0.0187**, Izz 0.0296 kg m2. Wing + fins (idx 0, 1, 5, 7, 8, 9) 0.892 kg: Iyy 0.0159. Iyy share of the hub group: **0.54**.
- Top hub My at the spar axis (RB, N m), with the total foot couple about the CG at the same instant:

| Case | Hub My | Foot couple |
|---|---|---|
| Z5_b45 narrow z0.10 mu0.30 | 12.83 | 24.10 |
| hard 10 narrow neg | 11.64 | 20.25 |
| Ta_h5 narrow z0.05 | 11.56 | 21.30 |

  Every governing case is a **narrow** (z-side) strike, so the moment is pitch. Per zeta, hub My is 10.30 / 11.56 / 12.83 and fin My at the spar crossing is 9.85 / 10.41 / 13.29 (zeta 0.02 / 0.05 / 0.10).
- Envelopes (RB):
  - Fin wrench at (SX, +-YF, 0): Fx 119.8 N, Fy 57.0, Fz 38.3, Mx 5.09 N m, My 13.29, Mz 16.39.
  - Hub wrench at the spar axis: Fx 95.2, Fy 43.5, Fz 41.6, Mx 4.80, My 12.83, Mz 15.62.
  - Largest root torque of one wing half: **8.76 N m** (hard 7/7 combo, asymmetric).
  - Rib wrench at x 0.17: Mx 5.09, My 10.00, Mz 10.12.
- Minor conservatism: the zeta 0.10 set bounds a pad that D-223 caps at <= 0.085 (n 12.41 > 12 g at 0.10). Linear interpolation gives about -3 % on hub My. D-223 keeps the 0.10 set until TP-3, so it stays.

### 1.2 The two worst rows by hand (formulas shown)
**P12, rib-saddle socket-to-ring junction** (`d226_p12.py`). Case: hard 7/7 combo, zeta 0.10, mu 0.40, fin R. Cut at x 0.0665. Section a = 19 mm (y) x b = 2 sqrt(10.5² - 6.5²) = 16.49 mm (z).
- Loads at the cut: F = (-105.6, 18.1, -38.3) N, M = (0.4, 13.01, 5.08) N m.
- Section moduli: Z1 = a b²/6 = 861 mm3, Z2 = b a²/6 = 992 mm3, A = 313.3 mm2.
- sigma = KP (My/Z1 + Mz/Z2 + Fx/A) = 2.156 x (15.11 + 5.12 + 0.34) = **44.35 MPa**.
- tau = KP (V/A + Mx / (0.21 a b²)) = 2.156 x (0.13 + 0.37) = 1.07 MPa.
- RF = 1 / sqrt((44.35/20)² + (1.07/20)²) = **0.451 RB, 0.202 at x2.23.** Reproduces P7.2 (0.45 / 0.20).

**N8, bridge-saddle ring bond on the spar** (`d226_check.py`). T = hub My at the spar axis = 12.83 N m.
- tau = T / (2 pi r² L) = 12.83 / (2 pi x 0.006² x 0.030) = 1.891 MPa; x KP = 4.077 MPa.
- RF = 2.0 / 4.077 = **0.491 RB, 0.220 at x2.23.** Reproduces P7.2 (0.49 / 0.22).

### 1.3 Formulation checks
- **Struts.** STRUT_S (-0.077, 0.0229, 0) and STRUT_E (0.050, 0.285, 0) lie in the bridge plane. The out-of-plane stiffness of the two 8x6 struts against My is about 2 x 4 E (137 mm4) (0.436)² / 0.291 m = 716 E mm4/m. The bridge 16x14 gives 4 E (1,331) / 0.11 = 48,400. The struts' share is **about 1.5 %**. Ignoring them is correct.
- **Fin inertia.** `d226_relief.py` applies d'Alembert to the idx-1 points (fins, ribs, root blocks) outboard of x 0.0665. P12 goes from 0.451 to **0.554 RB**, and the peak My at the cut from 13.04 to 9.60 N m. That is real but small. Do not take the credit until DR-6 (D-1 / CAD mass reconciliation) is closed.
- **Spar vs skin (the error).** `landing_path_a.wing_checks_skin` shares torsion by GJ: skin 0.890, spar 0.056 (strength_adopted.txt header). That split holds only where the torque is applied to the whole section. A saddle ring puts it into the spar, and the spar can only hand it to the skin through the foam.
  - Foam capacity over the whole bay y 0.06-0.38: F_SHEAR x 2 pi r² x L = 86 kPa x 2 pi x 0.006² x 0.32 = **6.22 N m** (unfactored). Needed: 0.89 x 13.29 x 2.23 x KP = 56.9 N m. **RF 0.11.**
  - So the spar carries the torque. Spar 12x10 (J 1,054 mm4, J/r 175.7 mm3): tau = T x 2.23 x KF / (J/r) = **291 MPa at the fin (RF 0.10), 192 MPa per centre half (RF 0.16)** against 30 MPa.
  - P14a (0.48 at x2.23) understates this, because it charges the spar only 5.6 % of My.
- **No hidden error in the demand file, the arm or the units.** Mass 1.705 against the 1.702 kg predicted at P7 is 0.2 % conservative.

### 1.4 Root cause
At touchdown the per-foot force is capped (plateau plus rate term). A narrow strike therefore makes a pitch couple of 20-24 N m RB about the CG. About half of it is owed to the motor group (54 % of Iyy), and the rest mostly to the fins themselves. That moment has to travel from the fins at y +-0.38 to the hub at the centre. The only member in the wing that can carry it is the closed skin cell (2A = 6,778 mm2, against 2 pi r² = 226 mm2 for the spar). **No drawing has ever put torque into that cell.** Each saddle, node or clamshell handed the moment to the 12 mm spar through epoxy rings. Their rows fail by 2-5x, and the spar behind them fails by 6-10x. Re-drawing the joint in another material (PETG, Onyx, CF plate, 6061) attacks the symptom. This is the same process failure the D-222 audit named (LR-2): one part judged at a time, never the whole path on one demand.

## 2. Options (governing RF at max(DAF, 1.5) = x2.23 for these rows; hand; `d226_hand.py`)

| Option | Governing row (x2.23) | Δ mass, basic (EST) | Cost | Student build | Verdict |
|---|---|---|---|---|---|
| **(a1)** continuous CF from the rib straight into the spar (no printed saddle: CF/Al collar, cross-pins) | spar torsion **0.10** (fin bay) / 0.16 (centre); rib tube 0.34 | about 0 to +10 | — | easy | **Rejected:** the spar cannot carry the torque (s1.3) |
| **(a2)** external CF struts from each motor station to the fin tip (pitch carried as axial force over z +-0.16 m) | 8x6 strut Euler at about 300 N x KF passes; wing joints still loaded by the fins' own share ("—") | **+44 to +56** (4 x 0.40 m 6x4.5 to 8x6 tube + 4 fittings) | — (tube R10 $4.40 / m, verified 2026-11-15; fittings —) | moderate | **Rejected:** mass. The struts sit in the prop slipstream (download, A-P3), and it is a configuration change (fins, arms, collision, A-P8 / A-P11) |
| **(a3) torsion-cell path** (s3) | new parts min **1.16-1.49** with the s3 dimensions. The path still needs the skin (1-ply **0.40**, 2-ply 0.80, or 1.10 with fin relief; 3-ply 1.20) and the rib (14x12 **0.34**; 25x23 1.20, or a torsion coupon) | **+32.7** (saddle replacement); skin +21.6 per extra ply over y 0.06-0.38; rib +23.8 (25x23) or 0 (coupon) | — (0.5 mm CF sheet, 6061 tube 5/8 x 0.035 in, 6061 bar: not priced); 1080 glass already in the BOM (T3, $6.46, TEST-PLAN l.187: covers the 2-ply skin) | moderate: waterjet / ShopBot plates, hot-wire slots, flox and glass tape (standard foam-core practice); Tormach for the T-fitting and flanges (training in the Maker Pass) | **Chosen**: the only option whose governing rows can be made to pass |
| (b) machined 6061 saddles (part-4 envelope, Tormach) | material rows pass (P12 in 6061: 0.451 x (240/20) x (2.156/1.725) = 6.77 RB, 3.03 at x2.23). But **N8 bond shear 0.22, P13 0.42 and spar torsion 0.10 are unchanged** | +30 to +100 (solid-envelope equivalents 51 g per rib saddle and 34 g centre, against 14.39 / 9.67 g PETG; pocketing range EST) | 6061 bar "—"; machine time $0 EST (Jacobs pass, `docs/reference/jacobs-equipment.md`) | moderate (thin walls in a 24 mm envelope, two setups) | **Rejected**: fixes the wrong element |
| (c) lower demand through the pad (D-222 gate: drop test TP-3) | best measured case (zeta 0.02, plateau 26 N): hub My 10.30 x 0.90, so N8 about 0.22 x 1.25 x 1.11 = **0.31**; P12 about 0.20 x 1.35 x 1.11 = 0.30 | +2 to +4 (D-222) | foam "—" (D-222) | easy | **Rejected as the fix.** To pass by demand alone, the foot force must fall 4.5x: plateau 6.7 N needs 0.5 m v² / (4 Fp - m g) = 1.228 / 10.0 = **123 mm** of stroke, and two feet (13.3 N) cannot hold 16.7 N of weight. **TP-3 stays** because it sets the (a3) grams |

## 3. The chosen path (a3): specification and hand rows (x2.23, no fin relief unless stated)

**Fin node (each side; replaces FIN-005)**
- Two 0.5 mm CF bulkheads at y 0.38 +- 7.5 mm, cut to the cell profile (LE to x 0.184).
- Slotted into the core, flox-filleted, and taped to both skins with 2-ply 1080 at an 8 mm lap.
- The 14x12 rib is bonded between the bulkheads over x 0.0705-0.17, with a glass wrap.
- The spar passes through bonded holes in the bulkheads.
- Two 0.5 mm CF in-plane plates (z-normal, 110 x 40 mm) under the skins, bonded to the rib, spar and bulkheads. They carry Mz / Fy, the role of the D-221 clamshell, but bonded to CF lines and not to a printed cradle.

**Centre (replaces CGE-006)**
- Two 0.5 mm CF bulkheads at y +-0.060, outboard of the pack-tray slot (|y| <= 58.5, `wing.py` l.922). The cell is open inside that slot.
- A 6061-T6 tube, 5/8 in x 0.035 in, 120 mm long, over the spar (flox-filled), is the torque member across the slot.
- A 6061 T-fitting (Tormach) takes the bridge in a 24 mm socket with its mouth at x 0.030.
- 6061 flanges, 100 x 18 x 1.5 mm, are bonded and bolted to each bulkhead.

| Element | Formula | Demand (RB) | Result | RF x2.23 |
|---|---|---|---|---|
| Fin bulkhead to skin lap (two bulkheads, 8 mm) | q = T x 2.23 x KP / 2A, A 3,389 mm2 | T 13.29 | q 9.43 N/mm; tau 0.59 MPa | **3.39** |
| Fin bulkhead plate shear (0.5 mm) | q / 2t | 13.29 | 9.4 MPa; CF plate shear "—" (glass +-45 S 70 MPa used as the lower bound) | >= 7 |
| Rib to bulkhead (moment taken out over L) | w = 6M/L² + V/L, two 7 mm fillets | My 10.00, Fz 38.3 at x 0.17 | L 99.5 mm: 2.21 MPa (RF **0.90**). L 113 mm: 1.73 MPa (**1.16**). Needs a 4-ply 0/90 wrap, or the plates extended to the rib top under the FIN-006 fairing (EST) | 0.90-1.16 |
| In-plane plates, polar bond (Mz) | tau = M r / J over the rib line (r 10-110 mm) and the spar line (+-30 mm), 2 plates, w 7 mm; J 6.46e6 mm4 | Mz 16.39 | 1.34 MPa | **1.49** |
| Centre torque tube 6061, 5/8 x 0.035 in (J/r 297 mm3) | vM: sqrt3 tau x KF <= 240 | half-root T 8.76 | tau 65.8 MPa | **1.22** (9/16 in: 0.97, rejected) |
| Centre flange bond 100 x 18 mm | tau = T KP r / J_p | 8.76 | 1.38 MPa | **1.45** (80 x 18: 0.93) |
| Centre bulkhead lap (8 mm) | as above | 8.76 | q 6.21 N/mm | **2.57** |
| Bridge at the T-fitting mouth x 0.030 | P7.2 B1 forward end | — | — | **1.02** |
| Bridge CF wall bearing in the 6061 socket | 6M/(D L²) + V/(D L) | P7.2 N6 equivalent | 48.5 MPa on the CF wall; allowable "—" | **—** (coupon, with TP-4) |
| Skin cell, existing WNG-011 (S 70 MPa, 0.0537 mm per ply, `landing_path_a.skin_laminate`) | q / (n t) | 13.29 (fin) / 9.60 (relief) / 8.76 (centre) | — | 1-ply **0.40** / 2-ply 0.80 / 3-ply **1.20** (relief: 0.55 / 1.10 / 1.66; centre: 0.60 / 1.21 / 1.81) |
| Rib tube at x 0.17 (tube_rf; envelope components combined, a bound) | comb(sigma/350, tau/30), KF | Mx 5.09, My 10.00, Mz 10.12 | — | 14x12 **0.34**; 20x18 0.75; 22x20 0.92; **25x23 1.20** |
| Spar | bending only, P16 with the in-plane plates spreading Mz into the section | — | — | **—** (re-run P16 at the node; T-071b P16 spar 24.6 at the older demand) |

Mass (basic, EST; CF 1.55 g/cm3, 6061 2.70):
- **Fin node:** bulkheads 2 x 2.63 g + plates 2 x 3.41 g + flox / tape / wrap 3.0 g = 15.1 g, against FIN-005 14.39 g: **+0.7 g per side.**
- **Centre:** bulkheads 5.26 g + tube 13.6 g + T-fitting 6.0 g + flanges 14.6 g + flox / tape 1.5 g = 41.0 g, against CGE-006 9.67 g: **+31.3 g.**
- **Saddle-replacement total: +32.7 g.**
- The struts and R4 clamps stay as resized in Part 7: they carry Fx as the truss, and the bridge cannot take the 45.6 N m RB in-plane root moment alone (Fx 120 N x 0.38 m).

## 4. Window (A-P3)

| State | Basic g (EST) | Δ to the 1,474.3 g ceiling | Predicted kg | Window % (linear, EST) | Bench derate line (0.934 x m / 1.702) |
|---|---|---|---|---|---|
| P7 tallied | 1,481.1 | -6.8 | 1.702 | +4.78 | 0.934 |
| + (a3) saddle replacement | 1,513.8 | -39.5 | 1.739 | +3.72 | 0.954 |
| ... minus the recoveries in the tallies (elevon lead -5.6 g, needs the flutter re-run; Onyx shoes -1.0 g) | 1,507.2 | **-32.9** | 1.731 | +3.93 | 0.950 |
| ... plus X7 root blocks -4 to -8 g (only if the D-223 root-block rows pass: not judged) | 1,499-1,503 | -25 to -29 | 1.722-1.727 | +4.0 to +4.2 | 0.945-0.948 |
| + 2nd skin ply y 0.06-0.38 (D-223 plans it; passes only with fin relief, 1.10) | 1,528.8 | -54.5 | 1.755 | +3.23 | 0.963 |
| + 3rd ply + 25x23 ribs (the full bound path) | 1,574 | about -100 | 1.806 | about +1.8 | about 0.99 |
| Best case after TP-3 (zeta 0.02), the D-1 wing DAF (about 1.93 EST, not below 1.5), fin relief, and favourable rib torsion and TP-8 coupons | about 1,502 | about -28 | 1.726 | about +4.1 | about 0.947 |

**No named recovery closes it.** Shortfall at the D-223 bound: **33 g basic** for the saddle replacement alone (25-29 g with X7 blocks). It is **55 g** with the planned 2nd skin ply and about **100 g** on the full bound path. Failing physics requirements:
- **A-P3** transition window >= +5 % with the download at derate 0.93.
- **A-P2** fresh T/W >= 2.0 (ceiling 1.730 kg without the download, 1.678 kg with it; CG-closure s3.1). At 1.731-1.739 kg it fails in either form.

The window passes only if the 2026-12-15 bench derate is at least the last column (0.950 or more). The CG-closure already called 0.920 a go/no-go risk. Not used, because it would be a method change: the itemised growth rule (1.666 against 1.704 kg, CG-closure s3.2, "information only"; D-208 keeps both mass claims).

## 5. Findings

| ID | Severity | Evidence | Required fix |
|---|---|---|---|
| SL-1 | **CRITICAL** | s1.3: no element puts torque into the skin cell. Foam transfer RF 0.11. The spar acts as the torsion member: RF 0.10 / 0.16 at x2.23. P14a / P15 credit 89 % to the skin. P7.3's ring-length fixes cannot work | Adopt (a3): bulkheads at the fin stations and y +-0.060, centre 6061 torque tube; FIN-005 and CGE-006 leave the primary path. Add a "torque introduction" row and a spar torsion-with-introduced-torque row to the single path table (LR-2) |
| SL-2 | **CRITICAL** | s4: with a passing path the window is 25-100 g short; A-P3 and A-P2 fresh fail at 1.73-1.81 kg | Conductor: record that no landing path inside the A-P3 window passes the D-223 bound on paper. Run TP-3, add the D-1 wing / fin-node output (DR-5), run the rib torsion coupon and TP-8 **before any further saddle CAD**: together they set the grams (28-100 g). Take the residual to the 2026-12-15 go/no-go as a bench-derate line of 0.95 or more |
| SL-3 | MAJOR | s0 1c, s3: the same demand fails the rib tube (0.34-0.38), the 1-ply skin (0.40 shear / 0.39 wrinkling) and, pre-package, the root block and shoe (0.41 / 0.55 RB, T-076d step5) | Judge the drawn and tallied root blocks and shoes (+12.2 g / +7.0 g EST) on `demand_p6` with the p6 method. No fin part is signed off alone |
| SL-4 | MAJOR | s3 rib row: CF in-plane shear 30 MPa (EST) governs the rib. The +23.8 g rib hangs on it | Torsion coupon on a 14x12 offcut (lever arm and weights, $0): if the measured allowable is >= 79 MPa (KF and x2.23), keep 14x12. Otherwise 25x23 (outside the 24 mm section: fairing and collision re-check) |
| SL-5 | MAJOR | s3: CF tube bearing in a 6061 socket, and CF plate shear and bearing: allowables "—" | Add them to the TP-4 coupon (same CF-in-Al interface and prep) |
| SL-6 | MINOR | s1.3: fin rows ignore the outboard fin inertia (+23 % RF on P12) | Add a relief column; no credit until DR-6 is closed |
| SL-7 | MINOR | s1.1: the zeta 0.10 bound exceeds the TP-3 hard line 0.085 (n 12.41 > 12 g); about 3 % conservative | Keep it until TP-3 (D-223); re-pair the DAF and RB at the measured zeta afterwards |
| SL-8 | INFO | s1.3: struts take about 1.5 % of My | None; the bounds are right to ignore them |

## 6. Implementation scope (sonnet implementer; nothing here is done)

1. **No saddle CAD** until the step 2 inputs exist.
2. **Analysis first:**
   - D-1 wing / fin-node section output (DR-5, minutes).
   - TP-3 drop test (December).
   - Rib torsion coupon (SL-4).
   - TP-8 skin coupon.
   - Then re-run `t077p6_demand.py` at the measured zeta and re-tally the (a3) grams with `d226_hand.py`-style rows in a repo script.
3. **Repo script `t077p8_path.py`:** one table from the pad to the hub on `demand_p6` covering pad, shoe, root block, rib, fin node, skin cell (P15 with relief as a column), spar (P16 and the introduced torsion), centre node, bridge, hub, arm tubes, bond. One minimum per part (LR-2).
4. **CAD (a3)** only after step 2:
   - wing.py: bulkhead slots at y +-0.38 / +-0.060; FIN-005 and CGE-006 replaced; T-fitting, tube and flanges.
   - Electrical: phase bundles, servo leads and I2C cross the centre bay. Route them through holes in the y +-0.060 bulkheads, and list any exposed length.
   - Then the gates once: build, `collide_a.py` pose 21, linkage poses, assembly, wire_inventory, cad_mass, mission gate, prop_a, proofs, drawings, `python -I tools/ledger_audit.py`.
5. **BOM (conductor):** price the 0.5 mm CF sheet (about 0.04 m2), the 6061 tube 5/8 x 0.035 in (>= 150 mm) and the 6061 bar before ordering. All of it must fit inside the $42.49 margin with the reserve held. No order before early December.

## 7. Limits
- Hand calculations only: no FEA. Every allowable is EST except the 6061 yield (minimum, secondary source).
- The rib, fin-node and plate rows combine non-concurrent envelope components (a bound).
- The fillet width (7 mm), lap (8 mm), flox / tape masses, the T-fitting mass (6 g) and the flange sizes are design choices with EST masses, not drawn.
- The window uses a linear 0.0324 point per g from P7.4, not a `prop_a` re-run.
- The (a2) and (b) masses are envelope arithmetic.
- No price was looked up: every new item is "—".
- The cell area 3,389 mm2 is the root section ahead of the hinge (`strength_V0.txt` header). The cell at y 0.38 is the same airfoil (constant chord).
- Whether the bulkhead slots clear the bundles, servo leads and conduits in the centre bay is unchecked.
